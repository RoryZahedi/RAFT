from concurrent import futures
import secrets
import string
import grpc
import messaging_pb2
import messaging_pb2_grpc
import time
import ipaddress
from _thread import *
import random
from google.protobuf import empty_pb2
import threading
import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

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
        global electionTimer, votedFor, state, forfeit
        global failedLinks
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        if failedLinks[int(otherClientNumber)] == 1:
            status_code = grpc.StatusCode.INVALID_ARGUMENT
            context.abort_with_status(grpc.StatusCode.INVALID_ARGUMENT, "")
    
      
        print(f"Received heartbeet: from {otherClient[peer_ip]}")
        votedFor = int(otherClientNumber)
        print("voting for",votedFor)
        if state != "follower":
            state = "follower"
            forfeit = 1
        electionTimer = random.randint(20,30)
        print()
        return empty_pb2.Empty()
    
class RequestVoteServicer(messaging_pb2_grpc.RequestVoteServicer):
    def SendVoteRequest(self,request,context):
        global currentTerm, votedFor, electionTimer,forfeit,state
        global failedLinks
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        # print("Made it here and failed links is",failedLinks)
        if failedLinks[int(otherClientNumber)] == 1:
            status_code = grpc.StatusCode.INVALID_ARGUMENT
            context.abort_with_status(grpc.StatusCode.INVALID_ARGUMENT, "")
        time.sleep(3)
        receivedTerm = request.term
        
        leaderLog = request.leaderLog
        # print("Leader log is ",request.leaderLog)
        if len(leaderLog) == 0:
            leaderLog = []
        else:
            leaderLog = [[eval(item) if item.isdigit() else item.strip("\"") for item in inner.split(",")] for inner in request.leaderLog(";")]
 
        print(f"Received vote request from {otherClientNumber} with term {receivedTerm}")
        voteGranted = False
        if currentTerm < receivedTerm:
            currentTerm = receivedTerm
            writeTermToFile()
            votedFor = -1
            writeVotedForToFile()
            if state != "follower":
                forfeit = 1
                # voteGranted = True
                # votedFor = int(otherClientNumber)
                state = "follower"
                print("Forfeiting election for term",currentTerm)
                electionTimer = random.randint(20, 30)
        if currentTerm == receivedTerm and (votedFor == -1 or int(votedFor) == int(otherClientNumber)): 
            if len(log) > 0 and len(leaderLog) == 0:
                return messaging_pb2.electionRequestResponse(
                    term=messaging_pb2.receivedTerm(term=currentTerm),
                    vg=messaging_pb2.voteGranted(vote=False)
                )
                #rejectleader
            elif (len(log) ==0 and len(leaderLog) >=0):
                voteGranted = True
                votedFor = int(otherClientNumber)
                #default to leader
            elif int(log[-1][0]) < int(leaderLog[-1][0]):
                voteGranted = True
                votedFor = int(otherClientNumber)
                #default to leader
            elif int(log[-1][0]) == int(leaderLog[-1][0]):
                if len(log) <= len(leaderLog):
                    voteGranted = True
                    votedFor = int(otherClientNumber)
                    #default to leader
            if voteGranted == True:
                votedFor = int(otherClientNumber)
                electionTimer = random.randint(20, 30)
                writeVotedForToFile()
                if state != "follower":
                    forfeit = 1
                    state = "follower"
                    print("Forfeiting election for term",currentTerm)
        response = messaging_pb2.electionRequestResponse(
            term=messaging_pb2.receivedTerm(term=currentTerm),
            vg=messaging_pb2.voteGranted(vote=voteGranted)
        )
        return response

class AppendEntriesServicer(messaging_pb2_grpc.AppendEntriesServicer):
    def SendAppendEntries(self,request,context):
        global currentTerm,state,forfeit, electionTimer, log
        global failedLinks
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        if failedLinks[int(otherClientNumber)] == 1:
            status_code = grpc.StatusCode.INVALID_ARGUMENT
            context.abort_with_status(grpc.StatusCode.INVALID_ARGUMENT, "")
        time.sleep(3)
        peer_ip = context.peer().split(":")[-1]
        print("RECEIVED APPEND")
        otherClientNumber = otherClient[peer_ip] #PID of other client
        # print("log string received",request.entries)
       
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
                    tempindex = len(log) - 1
                while log[tempindex][0] != receivedLog[tempindex][0] and tempindex >= 0:
                    log.pop(-1)
                    writeLogToFile()
                    tempindex -= 1
                if len(log) < request.prevLogIndex.index + 1:
                    for i in range(tempindex+1,len(receivedLog)-1): #append everything to match up to everything from tempindex + 1 to last element in receivedLog
                        if receivedLog[i][1] == 1: #if commited, do that action 
                            print(receivedLog[i][2])
                        log.append(receivedLog[i])
                        if len(log) == 1:
                            log[0][3] = hashlib.sha256(b"").hexdigest()
                        else:
                            temp_string_list = list(map(str,log[-2]))
                            prevListString = ''.join(temp_string_list) 
                            log[-1][3] = hashlib.sha256(prevListString.encode()).hexdigest()
                        writeLogToFile()
            log.append(receivedLog[request.prevLogIndex.index + 1])
            if len(log) == 1:
                log[0][3] = hashlib.sha256(b"").hexdigest()
            else:
                temp_string_list = list(map(str,log[-2]))
                prevListString = ''.join(temp_string_list) 
                log[-1][3] = hashlib.sha256(prevListString.encode()).hexdigest()
            writeLogToFile()

            response = messaging_pb2.SendAppendEntriesResponse(
                recipientTerm=messaging_pb2.Term(term=currentTerm),
                success=messaging_pb2.appendedEntry(success=True)
            )
        return response
    
class RedirectServicer(messaging_pb2_grpc.RedirectServicer):
    def SendTerminalCommandRedirect(self,request,context):
        global failedLinks
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        if failedLinks[int(otherClientNumber)] == 1:
            status_code = grpc.StatusCode.INVALID_ARGUMENT
            context.abort_with_status(grpc.StatusCode.INVALID_ARGUMENT, "")

        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        # print("Received", request.commandIssued, "from", str(otherClientNumber))
        # print(request.commandIssued)
        # print(int(otherClientNumber))
        # print(request.clientIDs)
        # print(request.clientIDs)
        # print(request.dictID)

        sendAppendEntriesFunc(command = request.commandIssued, issuingClientNum=int(otherClientNumber), 
                              clientIDs=request.clientIDs,dictID=request.dictID,dictKey=request.dictKey,
                              dictValue=request.dictValue)
        
        return empty_pb2.Empty()


class CommitServicer(messaging_pb2_grpc.CommitServicer):
    def SendCommitUpdate(self,request,context):
        global failedLinks
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        if failedLinks[int(otherClientNumber)] == 1:
            status_code = grpc.StatusCode.INVALID_ARGUMENT
            context.abort_with_status(grpc.StatusCode.INVALID_ARGUMENT, "")
        global log,replicatedDictionary
        time.sleep(3)
        print("Committing!")
        log[-1][1] = 1
        writeLogToFile()
        performComittedAction()
      
        return empty_pb2.Empty()

def performComittedAction():
    global log,clientNum,replicatedDictionary
    # print("log = ",log)
    # print(log[-1][2])
    command = log[-1][2].lower()
    
    # print("log = ",log)
    if command == 'create':

            #    currentTerm, committed, nameofcomamnd, hash of previous entry, clientlist, 
            # , dictionaryid, dictionary public key, list of dictionary private keys]
        print("command is create!")
        dictionaryID = str(log[-1][5])
        print
        clientList = log[-1][4].split()
        if str(clientNum) in clientList:
            replicatedDictionary[dictionaryID] = {}
    elif command == 'put':
        dictionaryID = str(log[-1][4])
        if dictionaryID in replicatedDictionary:
            # [currentTerm, committed, nameofCommand,hash of previous entry, dictionary_id, issuing client's client-id, 
            # key-vlalue pair encrypted with dictionary public key]
            replicatedDictionary[dictionaryID][log[-1][6]] = log[-1][7] 
    elif command == 'get':
        dictionaryID = str(log[-1][4])
        #  currentTerm,0,command,"",dictID,issuingClientNum,dictKey]
        if int(clientNum) == int(log[-1][5]):
            if log[-1][-1] not in replicatedDictionary[dictionaryID]:
                print("Key",log[-1][-1], "not found in dict")
            else:
                print("Get returned:",replicatedDictionary[dictionaryID][log[-1][-1]])  
    else:
        print("Unknown command:",command)
      

    
def serve(clientNum):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
    messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingServicer(), server)
    messaging_pb2_grpc.add_ClientNumberServicer_to_server(ClientNumberServicer(), server)
    messaging_pb2_grpc.add_RequestVoteServicer_to_server(RequestVoteServicer(),server)
    messaging_pb2_grpc.add_HeartbeatServicer_to_server(HeartbeatServicer(),server)
    messaging_pb2_grpc.add_AppendEntriesServicer_to_server(AppendEntriesServicer(),server)
    messaging_pb2_grpc.add_CommitServicer_to_server(CommitServicer(),server)
    messaging_pb2_grpc.add_RedirectServicer_to_server(RedirectServicer(),server)
    port = '[::]:5005' + clientNum
    server.add_insecure_port(port)
    server.start()
    print("Server started on ",port)
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def sendAppendEntriesFunc(command,issuingClientNum = -1, clientIDs = [],dictID = "", dictKey = "", dictValue = ""):
    global currentTerm,clientNum,log,state,AppendEntriesStubs,CommitStubs, channel, AppendEntriesStubsTwo, usingCrypto
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,numVotes,forfeit,currentTerm,counter

    if len(log) == 0:
        prevLogTerm = -1
    else:
        # print(log)
        prevLogTerm = log[len(log) - 1][0]  

    command = command.lower()
    prevLogIndex = len(log) - 1

    if command == 'create':

        dictID = str(currentTerm) + '.'+ str(counter)
        counter += 1
        private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048,)
        public_key = private_key.public_key()
        private_keyList = []
        for i in range(len(clientIDs)):
            if usingCrypto:
                res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(128))
                private_keyList.append(res.encode())
            else:
                print("here")
                private_keyList.append(private_key)
        # print("priv_keyList:",private_keyList)
        print(type(clientIDs),print(type(clientIDs) == type(list)))
        s = ''
        if type(clientIDs) != type(str):
            for i in clientIDs:
                s += i
            clientIDs = s
        print("Client IDs = ",clientIDs)

        log.append([currentTerm,0,command,"",clientIDs,dictID, public_key, private_keyList]) #Still not finished; TODO : create actual dict, dictionary public key, list of dictionary private keys
        #currentTerm, committed, nameofcomamnd, hash of previous entry, clientlist, 
    # , dictionaryid, dictionary public key, list of dictionary private keys]

    elif command == 'get':
        
        # log.append([currentTerm,0,command,"",dictID,issuingClientNum,dictKey])
        log.append([currentTerm,0,command,"",dictID,issuingClientNum,dictKey])
        #get command log entry [currentTerm, committed, nameofCommand, hash of previous entry, 
        # dictionary_id, issuing client's client-id,  key (to get value) encrypted with dictionary public key
        


    elif command == 'put':
        print("Dict Value = ",dictValue)
        log.append([currentTerm,0,command,"",dictID,issuingClientNum,dictKey,dictValue])
        #TODO actually put it
        #put command log entry [currentTerm, committed, nameofCommand,hash of previous entry, dictionary_id, issuing client;s client-id, 
        # key-vlalue pair encrypted with dictionary public key]


    else:
        print("Unrecognized command:", command)
        return
    

    if len(log) == 1:
        log[0][3] = hashlib.sha256(b"").hexdigest()
    else:
        temp_string_list = list(map(str,log[-2]))
        prevListString = ''.join(temp_string_list) 
        log[-1][3] = hashlib.sha256(prevListString.encode()).hexdigest()

    writeLogToFile()
    #append requested entry
    #maybe make special cse for when log was empty prior to appending for the first time?
    logString = ";".join([",".join(map(str, inner_lst)) for inner_lst in log])
    # print("Log is:", log)
    # print("Log string is:", logString)
    args = messaging_pb2.SendAppendEntriesArgs( 
        term=messaging_pb2.Term(term = currentTerm),
        prevLogIndex=messaging_pb2.Index(index = prevLogIndex),
        prevLogTerm = messaging_pb2.Term(term = prevLogTerm),
        entries = messaging_pb2.Request(message = logString),
        commitIndex = messaging_pb2.Index(index = -1)
    )
  

    threads = []
    numSucc = [0]*5
    numSucc[int(clientNum)] = 1
    for i in range(0,5):
        if i != int(clientNum):
            t = threading.Thread(target=asynchSendAppendEntries, args=(args,i,numSucc))
            threads.append(t)
            t.start()
    for t in threads:
        t.join()
    
    if sum(numSucc) >= 3:
        log[-1][1] = 1

        performComittedAction()
        threads = []
        for i in range(0,5):
            if i != int(clientNum):
                t = threading.Thread(target=asynchSendCommit, args=(i,))
                threads.append(t)
                t.start()
        for t in threads:
             t.join()
        writeLogToFile()
        
        
    
            
def asynchSendAppendEntries(args,clientNumToSendTo,numSucc):
    global log, AppendEntriesStubs
    print("Sending request to client",clientNumToSendTo)
    try:
        if failedLinks[int(clientNumToSendTo)] != 1:
            results = AppendEntriesStubs[clientNumToSendTo].SendAppendEntries(args)

        if results.success.success:
            numSucc[clientNumToSendTo] = 1                                                
    except grpc.RpcError as e:
        print("Could not reach client",clientNumToSendTo)
      
def asynchSendCommit(i):
    global CommitStubs
    global failedLinks
    try:
        if failedLinks[int(i)] != 1:
            nullRet = CommitStubs[i].SendCommitUpdate(empty_pb2.Empty())
    except grpc.RpcError as e:
        print("Could not reach client for commit",i)
    return

def run():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,heartbeatStubs,AppendEntriesStubs, CommitStubs, channel,terminalStubs
    global failedLinks
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
            terminalStubs.append(messaging_pb2_grpc.RedirectStub(channel))
        else:
            clientNumberStubs.append(-1)
            messageStubs.append(-1)
            requestVotesStub.append(-1)
            AppendEntriesStubs.append(-1)
            heartbeatStubs.append(-1)
            CommitStubs.append(-1)
            terminalStubs.append(-1)
    for i in range(0,5): #Send initial message
        if str(i) != clientNum:
            message = str(clientNum)
            if failedLinks[int(i)] != 1:
                nullret = clientNumberStubs[i].SendClientNumber(messaging_pb2.Request(message=message))


def terminalInput():
    global clientNum,state,votedFor,terminalStubs,getValue,replicatedDictionary,failedLinks, usingCrypto
    while True: #terminal input
        option = input()
        match option:
            case "create":
                print("Selected: create")
                print("With encryption(y/n)?",end='')
                encryptionAnswer = input()
                if encryptionAnswer == 'n':
                    usingCrypto = False
                else:
                    print(encryptionAnswer)
                print("Please enter list of clients seperated by space.",end='')
                members = input()
                # clientIDList = [int(str(x)) for x in members]
                clientIDList = members
                if state == 'leader':
                    sendAppendEntriesFunc(command='Create',issuingClientNum=clientNum,clientIDs = clientIDList)
                elif state == 'follower': #redirect it
                    args = messaging_pb2.TerminalArgs( 
                        commandIssued="create",
                        clientIDs=clientIDList,
                        dictID = "",
                        dictKey = "",
                        dictValue = "" 
                    )
                    print("Voted for = ",votedFor)
                    try:
                        if failedLinks[int(votedFor)] != 1:
                            terminalStubs[int(votedFor)].SendTerminalCommandRedirect(args) 
                    except grpc.RpcError as e:
                        print("Could not reach client",votedFor)
                    
                
            case "put":
                print("Selected: put")
                print("Please enter DICTID \n")
                PID = input("PID:")
                dIDCounter = input("Counter:")
                dictID = PID + "." + dIDCounter
                key = input("Please enter the dict key")
                value = input("Enter the value you wish to place")
                if state == 'leader':
                    sendAppendEntriesFunc(command= 'Put',issuingClientNum=clientNum,dictID=dictID,dictKey=key,dictValue=value)
                    # def sendAppendEntriesFunc(command,issuingClientNum = -1, clientIDs = [],dictID = "", dictKey = "", dictValue = ""):
                elif state == 'follower': #redirect it
                    args = messaging_pb2.TerminalArgs( 
                        commandIssued="put",
                        clientIDs=[],
                        dictID = dictID,
                        dictKey = key,
                        dictValue = value
                    )
                    try:
                        if failedLinks[int(votedFor)] != 1:
                            terminalStubs[int(votedFor)].SendTerminalCommandRedirect(args) 
                    except grpc.RpcError as e:
                         print("Could not reach client",votedFor)
                
            case "get":
                print("Selected: get")
                dictID = input("Please enter dictionary ID (PID.Counter):")
                key = input("Please enter the dict key (key):")
                if state == 'leader':
                    sendAppendEntriesFunc(command= 'Get',issuingClientNum=clientNum,dictID=dictID,dictKey=key)
                elif state == 'follower':
                    args = messaging_pb2.TerminalArgs( 
                        commandIssued="get",
                        clientIDs=[],
                        dictID = dictID,
                        dictKey = key,
                        dictValue = ""
                    )
                    try:
                        if failedLinks[int(votedFor)] != 1:
                            terminalStubs[int(votedFor)].SendTerminalCommandRedirect(args) 
                    except grpc.RpcError as e:
                         print("Could not reach client",votedFor)
            case "printDict":
                print("Selected: printDict")
                dictKey = input("Enter key (PID.COUNTER)")
                print("Dict = ",replicatedDictionary[dictKey])

            case "printAll":
                print("Selected: printAll")
                print("Dict = ",replicatedDictionary)
    
            case "failLink":
                print("Selected: failLik")
                clientNumToSever = int(input("Client connection you wish to sever"))
                failedLinks[clientNumToSever] = 1

            case "fixLink":
                print("Selected: fixLink")
                clientNumToFix = int(input("Client connection you wish to fix"))
                failedLinks[clientNumToFix] = 0

            case "failProcess":
                print("Selected: failProcess")


            case _:
                print("Invalid input,",option)


        
def sendElectionRequests(i):
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,numVotes,forfeit,currentTerm,log
    print("Sending request to client",i)
    try:
        if failedLinks[int(i)] != 1:
            logString = ""
            if len(log) > 0:
                logString = ";".join([",".join(map(str, inner_lst)) for inner_lst in log])
            args = messaging_pb2.RequestVoteArgs( 
                term=currentTerm,
                leaderLog = logString
            )
            results = requestVotesStub[i].SendVoteRequest(args)
            receivedTerm = results.term.term #requested client's updated term
            voteGranted = results.vg.vote #whether requested client gives vote to us or not
        # print(voteGranted)
            if receivedTerm > currentTerm:
                currentTerm = receivedTerm
                writeTermToFile()
                forfeit = 1     
            if voteGranted:
                numVotes[i] = 1
    except grpc.RpcError as e:
        print("Could not reach client",i)
            


def election():
    #add variable here
    print("still here")
    global clientNum, votedFor,numVotes,forfeit, electionTimer,state,currentTerm,candidateElectionTimer
    votedFor = int(clientNum)
    writeVotedForToFile()
    numVotes = [0]*5 
    forfeit = 0

    for i in range(0,5):
        if i != int(clientNum):
            t = threading.Thread(target=sendElectionRequests, args=(i,))
            t.start()

    #either the election has timed out, i have received enough votes, or i have forfeited the election
    while sum(numVotes) < 3 and forfeit != 1 and candidateElectionTimer > 0:
        time.sleep(.1)
    

    if sum(numVotes) >= 3:
        state = 'leader'
        print('I am the leader')
        return
    elif forfeit == 1:
        state = 'follower'
        forfeit = 0
        electionTimer = random.randint(20, 30)
        return
    elif candidateElectionTimer == 0:
        return
    print("exiting election")

    

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
            # print("in here")
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

            threads = []
            for i in range(0,5):
                if i != int(clientNum):
                    t = threading.Thread(target=sendHeartBeats, args=(i,))
                    threads.append(t)
                    t.start()
            for t in threads:
                t.join()
    

            # heartbeatTimer = random.randint(10,15)
            heartbeatTimer = 5 #TODO REMOVE THIS
            print("Heartbeat timeout!")
            
def sendHeartBeats(i):
    global heartbeatStubs,votedFor
    votedFor = int(clientNum)
    try:
        if failedLinks[int(i)] != 1:
            nullret = heartbeatStubs[i].SendHeartbeat(messaging_pb2.Request(message=str(clientNum)))
    except grpc.RpcError as e:
        print("Could not send heartbeat to client",i)
    return
                


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
        # print(log)
        logString = ";".join([",".join(map(str, inner_lst)) for inner_lst in log])
        lines[-1] = "log: " + logString + "\n"
    with open(filename, 'w') as file:
        file.writelines(lines)

def loadKeysAtStart(clientNum):
    filename = "public-keyX.pub"
    pubKeyDict = {}


    filenumberIndex = filename.find('X')

    for i in range(0,5):
        fName = filename
        fName = fName.replace('X',str(i))
        with open(fName, 'rb') as file:
            pemlines = file.read()
        public_key = load_pem_public_key(pemlines)
        pubKeyDict[i] = public_key
        
    ciphertexts = []
    #Test
    for pubKey in pubKeyDict.values():
        Message = "PLEASE WORK".encode()
        ciphertext = pubKey.encrypt(
        Message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        )
        ciphertexts.append(ciphertext)


    filename = "private-keyX.pem"

    fName = 'private-key' + str(clientNum) + '.pem'
    with open(fName, 'rb') as file:
        pemlines = file.read()
    privateKey = load_pem_private_key(pemlines, None, default_backend())

    plaintext = privateKey.decrypt(
        ciphertexts[int(clientNum)],
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    hashkey = []
    for i in range(5):
        val = get_random_bytes(16)
        hashkey.append(AES.new(val, AES.MODE_EAX))

    return pubKeyDict, privateKey, hashkey

if __name__ == '__main__':
    print("Client num:",end="")
    clientNum = input()
    pubKeyDict, privateKey, hashkey = loadKeysAtStart(clientNum)
    failedLinks = [0]*5
    start_new_thread(serve, (clientNum,))
    print("Press enter to start")
    input()

    channel = 0
    counter = 0
    usingCrypto = True
    getValue = None
    clientNumberStubs = []
    messageStubs = []
    requestVotesStub = []
    heartbeatStubs = []
    AppendEntriesStubs = []
    CommitStubs = []
    terminalStubs = []
    replicatedDictionary = {}
    run()
    
    start_new_thread(terminalInput,())
    filename = "file"+str(clientNum)+".txt"

    lines = [] #content of files
    with open(filename, 'r') as file:
        lines = file.readlines()

    
    

   
    state = "follower"
    currentTerm = 0
    writeTermToFile()
    
    time.sleep(5)
    
    heartbeatTimer = 0
    electionTimer = random.randint(20,30)
    votedFor = -1
    writeVotedForToFile()
    numVotes = [0]*5
    forfeit = 0
    candidateElectionTimer = 1
    #term, committed, number
    log = []
    writeLogToFile()
    #log = [[index, term, committed, dictionary_id, client_numbersthathaveaccess, dictionary public key, version],]
    electionTimeout()
  
    while True:
        time.sleep(1)