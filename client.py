from concurrent import futures

import grpc
import messaging_pb2
import messaging_pb2_grpc
import time
import ipaddress
from _thread import *
import random
from google.protobuf import empty_pb2
import threading

otherClient = {} #IP/Port -> ClientNum

class MessagingServicer(messaging_pb2_grpc.MessagingServicer):
    def SendMessage(self, request, context):
        time.sleep(3)
        peer_ip = context.peer().split(":")[-1]
        print(f"Received message: {request.message} from {peer_ip}")
        print()
        return messaging_pb2.Response(message=f"Server received message: {request.message}")
    
class ClientNumberServicer(messaging_pb2_grpc.ClientNumberServicer):
    def SendClientNumber(self, request, context):
        peer_ip = context.peer().split(":")[-1]
        otherClient[peer_ip] = request.message
        print(f"Received message: {request.message} from {otherClient[peer_ip]}")
        print()
        return empty_pb2.Empty()
    
class HeartbeatServicer(messaging_pb2_grpc.HeartbeatServicer):
    def SendHeartbeat(self, request, context):
        global electionTimer
        peer_ip = context.peer().split(":")[-1]
        otherClient[peer_ip] = request.message
        print(f"Received heartbeet: from {otherClient[peer_ip]}")
        electionTimer = random.randint(20,30)
        print()
        return empty_pb2.Empty()
    
class RequestVoteServicer(messaging_pb2_grpc.RequestVoteServicer):
    def SendVoteRequest(self,request,context):
        global currentTerm, votedFor, electionTimer,forfeit,state
        time.sleep(3)
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        receivedTerm = request.term 
        print(f"Received vote request from {otherClientNumber} with term {receivedTerm}")
        voteGranted = False
        if currentTerm < receivedTerm:
            currentTerm = receivedTerm
            writeTermToFile()
            votedFor = -1
            writeVotedForToFile()
            if state != "follower":
                forfeit = 1
                state = "follower"
                print("Forfeiting election for term",currentTerm)
                electionTimer = random.randint(20, 30)
        if currentTerm == receivedTerm and (votedFor == -1 or votedFor == otherClientNumber) and clientNum > otherClientNumber:#TODO: hardcoded
            if state != "follower":
                forfeit = 1
                state = "follower"
                print("Forfeiting election for term",currentTerm)
                electionTimer = random.randint(20, 30)
            votedFor = otherClientNumber
            writeVotedForToFile()
            voteGranted = True
            electionTimer = random.randint(20, 30)
        response = messaging_pb2.electionRequestResponse(
            term=messaging_pb2.receivedTerm(term=currentTerm),
            vg=messaging_pb2.voteGranted(vote=voteGranted)
        )
        return response

class AppendEntriesServicer(messaging_pb2_grpc.AppendEntriesServicer):
    def SendAppendEntries(self,request,context):
        global currentTerm,state,forfeit, electionTimer, log
        peer_ip = context.peer().split(":")[-1]
        print("RECEIVED APPEND")
        otherClientNumber = otherClient[peer_ip] #PID of other client
        print("log string received",request.entries)
        
        receivedLog = [[eval(item) if item.isdigit() else item.strip("\"") for item in inner.split(",")] for inner in request.entries.message.split(";")]
        print(receivedLog)

        if currentTerm > request.term.term:
            response = messaging_pb2.SendAppendEntriesResponse(
                recipientTerm=messaging_pb2.Term(term=currentTerm),
                success=messaging_pb2.appendedEntry(success=False)
            )
        elif currentTerm <= request.term.term:
            currentTerm = request.term.term
            writeTermToFile()

            if state != "follower":
                state = "follower"
                forfeit = 1
                print("Forfeiting election for term",currentTerm)
            electionTimer = random.randint(20, 30)
            #implement log stuff later
            #while the local log's term at prevlogindex != leader/sender's log's term at prevlogindex
            #decrement 
            if request.prevLogIndex.index != -1:
                tempindex = request.prevLogIndex.index
                print(request.prevLogIndex.index)
                if tempindex >= len(log):
                    print("should not be here in this case")
                    tempindex = len(log) - 1
                print("index 1")
                while log[tempindex][0] != receivedLog[tempindex][0] and tempindex >= 0:
                    print("should not be here, this while loop should not be executed")
                    log = log.pop(-1)
                    writeLogToFile()
                    tempindex -= 1
                if len(log) < request.prevLogIndex.index + 1:
                    print("index 2")
                    print("should not be here, we immediately found a match so we didn't pop anything")
                    for i in range(tempindex+1,len(receivedLog)-1): #append everything to match up to everything from tempindex + 1 to last element in receivedLog
                        if receivedLog[i][1] == 1: #if commited, do that action 
                            print(receivedLog[i][2])
                        log.append(receivedLog[i])
                        writeLogToFile()
            print("about to append final entry")
            print(request.prevLogIndex.index + 1)
            print(log)
            log.append(receivedLog[request.prevLogIndex.index + 1])
            writeLogToFile()
            print("its 121")
            print(log)
            print(request.prevLogIndex.index+1)
            if log[request.prevLogIndex.index + 1][1] == 1:
                print(log)
            print("Appended")
            response = messaging_pb2.SendAppendEntriesResponse(
                recipientTerm=messaging_pb2.Term(term=currentTerm),
                success=messaging_pb2.appendedEntry(success=True)
            )
        return response
    
class CommitServicer(messaging_pb2_grpc.CommitServicer):
    def SendCommitUpdate(self,request,context):
        print("Committing!")
        global log
        log[-1][1] = 1
        print("log after commit:", log)
        return empty_pb2.Empty()

    
def serve(clientNum):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
    messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingServicer(), server)
    messaging_pb2_grpc.add_ClientNumberServicer_to_server(ClientNumberServicer(), server)
    messaging_pb2_grpc.add_RequestVoteServicer_to_server(RequestVoteServicer(),server)
    messaging_pb2_grpc.add_HeartbeatServicer_to_server(HeartbeatServicer(),server)
    messaging_pb2_grpc.add_AppendEntriesServicer_to_server(AppendEntriesServicer(),server)
    messaging_pb2_grpc.add_CommitServicer_to_server(CommitServicer(),server)
    port = '[::]:5005' + clientNum
    server.add_insecure_port(port)
    server.start()
    print("Server started on ",port)
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def sendAppendEntriesFunc():
    global currentTerm,clientNum,log,state,AppendEntriesStubs,CommitStubs, channel, AppendEntriesStubsTwo
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,numVotes,forfeit,currentTerm


    if len(log) == 0:
        prevLogTerm = -1
    else:
        print(log)
        prevLogTerm = log[len(log) - 1][0]
    

    prevLogIndex = len(log) - 1
    log.append([currentTerm, 0, "hello"])
    writeLogToFile()
    #append requested entry
    #maybe make special cse for when log was empty prior to appending for the first time?
    logString = ";".join([",".join(map(str, inner_lst)) for inner_lst in log])
    print("Log is:", log)
    print("Log string is:", logString)
    args = messaging_pb2.SendAppendEntriesArgs( 
        term=messaging_pb2.Term(term = currentTerm),
        prevLogIndex=messaging_pb2.Index(index = prevLogIndex),
        prevLogTerm = messaging_pb2.Term(term = prevLogTerm),
        entries = messaging_pb2.Request(message = logString),
        commitIndex = messaging_pb2.Index(index = -1)
    )
  
        
    successclients = [0]*5
    for i in range(0,5):
        if str(i) != clientNum:
            print("Sending request to client",i)
            results = AppendEntriesStubs[i].SendAppendEntries(args)                                                     
            if results.success.success:
                print("successful log update")
                successclients[i] += 1
                if sum(successclients) == 3:
                    log[-1][1] = 1
                    print(log[-1][2])
                    for j in range(0,i):
                        if str(j) != clientNum:
                            print("here send commit update")
                            nullret = CommitStubs[j].SendCommitUpdate(empty_pb2.Empty())

            #         #issue commit update here
            

def run():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,heartbeatStubs,AppendEntriesStubs, CommitStubs, channel
    
    for i in range(0,5): #Initalize clientNumberStubs with clientNumberStubs to send clientNumbers
        if str(i) != clientNum: 
            port = 'localhost:5005'+str(i)
            channel = grpc.insecure_channel(port)
            clientNumberStubs.append(messaging_pb2_grpc.ClientNumberStub(channel))
            messageStubs.append(messaging_pb2_grpc.MessagingStub(channel))
            requestVotesStub.append(messaging_pb2_grpc.RequestVoteStub(channel))
            heartbeatStubs.append(messaging_pb2_grpc.HeartbeatStub(channel))
            AppendEntriesStubs.append(messaging_pb2_grpc.AppendEntriesStub(channel))
            CommitStubs.append(messaging_pb2_grpc.CommitStub(channel))
        else:
            clientNumberStubs.append(-1)
            messageStubs.append(-1)
            requestVotesStub.append(-1)
            AppendEntriesStubs.append(-1)
            heartbeatStubs.append(-1)
            CommitStubs.append(-1)
    for i in range(0,5): #Send initial message
        if str(i) != clientNum:
            message = str(clientNum)
            nullret = clientNumberStubs[i].SendClientNumber(messaging_pb2.Request(message=message))


def terminalInput():
    while True: #terminal input
        option = input()
        match option:
            case "create":
                print("Selected: create")
                sendAppendEntriesFunc()

            case "put":
                print("Selected: put")

            case "get":
                print("Selected: get")

            case "printDict":
                print("Selected: printDict")
            
            case "printAll":
                print("Selected: printAll")
    
            case "failLink":
                print("Selected: failLik")

            case "fixLink":
                print("Selected: fixLink")

            case "failProcess":
                print("Selected: failProcess")


            case _:
                print("Invalid input,",option)






        
def sendElectionRequests():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,numVotes,forfeit,currentTerm
    for i in range(0,5):
        if str(i) != clientNum:
            print("Sending request to client",i)
            results = requestVotesStub[i].SendVoteRequest(messaging_pb2.Term(term=currentTerm))
            receivedTerm = results.term.term #requested client's updated term
            if receivedTerm > currentTerm:
                currentTerm = receivedTerm
                writeTermToFile()
                forfeit = 1
            voteGranted = results.vg.vote #whether requested client gives vote to us or not
            print(voteGranted)
            if voteGranted:
                numVotes+=1



def election():
    #add variable here
    global clientNum, votedFor,numVotes,forfeit, electionTimer,state,currentTerm,candidateElectionTimer
    votedFor = clientNum
    writeVotedForToFile()
    numVotes = 1
    forfeit = 0
    start_new_thread(sendElectionRequests, ())
    #either the election has timed out, i have received enough votes, or i have forfeited the election
    while numVotes < 3 and forfeit != 1 and candidateElectionTimer > 0:
        time.sleep(.1)
    
    if numVotes >= 3:
        state = 'leader'
        print('I am the leader')
        return
    elif forfeit == 1:
        state = 'follower'
        forfeit = 0
        electionTimer = random.randint(20, 30)
        print('in the forfeit branch with election timer = ',electionTimer)
        return
    elif candidateElectionTimer == 0:
        return
    

    

def candidateElectionTimeout():
    global state, currentTerm,candidateElectionTimer
    while True:
        if state != 'candidate':
            return
        currentTerm = currentTerm + 1
        writeTermToFile()
        candidateElectionTimer = random.randint(20, 30)
        election_thread = threading.Thread(target=election)
        election_thread.start()
        while candidateElectionTimer > 0 and state == 'candidate':
            # print(candidateElectionTimer)
            time.sleep(1)
            candidateElectionTimer-=1
        election_thread.join()


    
def electionTimeout():
#     #Except if leader maybe the timer does not decrament
    global electionTimer,state,heartbeatTimer
    while True:
        while state == "follower":
            while electionTimer:
                time.sleep(1)
                electionTimer-=1
            print("Election timedout!")
            state = "candidate"
            candidateElectionTimeout()
        while state == "leader":
            while heartbeatTimer:
                time.sleep(1)
                heartbeatTimer-=1
            #send heartbeats to all other clients
            sendHeartBeats()
            heartbeatTimer = random.randint(10,15)
            print("Heartbeat timeout!")
            
def sendHeartBeats():
    global heartbeatStubs
    for i in range(0,5):
        if str(i) != str(clientNum):
            print("Sending heartbeat to client",i)
            nullret = heartbeatStubs[i].SendHeartbeat(messaging_pb2.Request(message=str(clientNum)))


def writeTermToFile():
    global lines,filename,currentTerm
    lines[-3] = "CurrentTerm: " + str(currentTerm) + "\n"
    with open(filename, 'w') as file:
        file.writelines(lines)

def writeVotedForToFile():
    global lines,filename,votedFor
    lines[-2] = "VotedFor: " + str(votedFor) + "\n"
    with open(filename, 'w') as file:
        file.writelines(lines)

def writeLogToFile():
    global lines,filename,log
    if len(log) == 0:
        lines[-1] = "log: " + "\n"
    else:
        print(log)
        logString = ";".join([",".join(map(str, inner_lst)) for inner_lst in log])
        lines[-1] = "log: " + logString + "\n"
    with open(filename, 'w') as file:
        file.writelines(lines)
if __name__ == '__main__':
    print("Client num:",end="")
    clientNum = input()
    start_new_thread(serve, (clientNum,))
    print("Press enter to start")
    input()
    channel = 0
    clientNumberStubs = []
    messageStubs = []
    requestVotesStub = []
    heartbeatStubs = []
    AppendEntriesStubs = []
    CommitStubs = []
    run()
    
    start_new_thread(terminalInput,())
    filename = "file"+str(clientNum)+".txt"

    lines = [] #content of files
    with open(filename, 'r') as file:
        lines = file.readlines()

    
    

   
    state = "follower"
    currentTerm = 0
    writeTermToFile()
    
    time.sleep(10)
    
    heartbeatTimer = 0
    electionTimer = random.randint(20,30)
    votedFor = -1
    writeVotedForToFile()
    numVotes = 0
    forfeit = 0
    candidateElectionTimer = 1
    #term, committed, number
    log = []
    writeLogToFile()
    #log = [[index, term, committed, dictionary_id, client_numbersthathaveaccess, dictionary public key, version],]
    electionTimeout()
  
    while True:
        time.sleep(1)
