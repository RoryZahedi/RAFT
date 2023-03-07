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
    
class RequestVoteServicer(messaging_pb2_grpc.RequestVoteServicer):
    def SendVoteRequest(self,request,context):
        global currentTerm, votedFor, electionTimer,forfeit
        time.sleep(3)
        print(f"Received vote request from {otherClientNumber} with term {receivedTerm}")
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]
        receivedTerm = request.term 
        voteGranted = False
        if currentTerm < receivedTerm:
            currentTerm = receivedTerm
            votedFor = -1
            if state != "follower":
                forfeit = 1
                state = "follower"
                print("Forfeiting election for term",currentTerm)
                electionTimer = random.randInt(6, 12)
        if currentTerm == receivedTerm and (votedFor == -1 or votedFor == otherClientNumber) and clientNum > otherClientNumber:
            votedFor = otherClientNumber
            voteGranted = True
            electionTimer = random.randInt(6, 12)
        response = messaging_pb2.electionRequestResponse(
            rt=messaging_pb2.recipientTerm(term=currentTerm),
            vg=messaging_pb2.voteGranted(vote=voteGranted)
        )
        return response
    
def serve(clientNum):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingServicer(), server)
    messaging_pb2_grpc.add_ClientNumberServicer_to_server(ClientNumberServicer(), server)
    messaging_pb2_grpc.add_RequestVoteServicer_to_server(RequestVoteServicer(),server)
    port = '[::]:5005' + clientNum
    server.add_insecure_port(port)
    server.start()
    print("Server started on ",port)
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


def run():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub 
    
    for i in range(0,5): #Initalize clientNumberStubs with clientNumberStubs to send clientNumbers
        if str(i) != clientNum: 
            port = 'localhost:5005'+str(i)
            channel = grpc.insecure_channel(port)
            clientNumberStubs.append(messaging_pb2_grpc.ClientNumberStub(channel))
            messageStubs.append(messaging_pb2_grpc.MessagingStub(channel))
            requestVotesStub.append(messaging_pb2_grpc.RequestVoteStub(channel))
        else:
            clientNumberStubs.append(-1)
            messageStubs.append(-1)
            requestVotesStub.append(-1)
    for i in range(0,5): #Send initial message
        if str(i) != clientNum:
            message = str(clientNum)
            nullret = clientNumberStubs[i].SendClientNumber(messaging_pb2.Request(message=message))
    
    # for i in range(0,5): 
    #     if str(i) != clientNum:
    #         message = str(term)
    #         retval = requestVotesStub[i].SendVoteRequest(messaging_pb2.Term(term=term))
    #         print("votegranted = ",retval.vg.vote, "and recipient term = ",retval.rt.term)
    # while True:
    #     message = input("Enter a message to send: ")
    #     for stub in messageStubs:
    #         if stub != -1:
    #             response = stub.SendMessage(messaging_pb2.Request(message=message))
    #             print(f"Received response: {response.message}")




        
def sendElectionRequests():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,numVotes
    for i in range(0,5):
        if str(i) != clientNum:
            print("Sending request to client",i)
            results = requestVotesStub[i].SendVoteRequest(messaging_pb2.Term(term=currentTerm))
            receivedTerm = results.term.term #requested client's updated term
            voteGranted = results.vg.vote #whether requested client gives vote to us or not
            if voteGranted:
                numVotes+=1


def election():
    #add variable here
    global clientNum, votedFor,numVotes,forfeit, electionTimer,state,currentTerm 
    # global clientNum,clientNumberStubs,messageStubs,requestVotesStub,term,votedFor,forfeit,state,heartBeatTimer,electionTimeoutReturn,numVotes, votedServer
    # global currentTerm,numVotes, electionTimer
    # currentTerm+=1
    # numvotes += 1
    # electionTimer = random.randint(6,12)
    # sendElectionRequests()
    votedFor = clientNum
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
        electionTimer = random.randInt(6, 12)
        return
    elif candidateElectionTimer == 0:
        currentTerm += 1
        return
    

    

def candidateElectionTimeout():
    global state 
    while True:
        if state != 'candidate':
            return
        candidateElectionTimer = random.randint(6, 12)
        election_thread = threading.Thread(target=election)
        election_thread.start()
        while candidateElectionTimer > 0 and state == 'candidate':
            time.sleep(1)
            candidateElectionTimer-=1
        election_thread.join()


    
def electionTimeout():
#     #Except if leader maybe the timer does not decrament
    global electionTimer,state
    while True:
        while state == "follower":
            while electionTimer:
                time.sleep(1)
                electionTimer-=1
            print("Election timedout!")
            state = "candidate"
            candidateElectionTimeout()



       
if __name__ == '__main__':
    print("Client num:",end="")
    clientNum = input()
    start_new_thread(serve, (clientNum,))
    print("Press enter to start")
    input()
    
    clientNumberStubs = []
    messageStubs = []
    requestVotesStub = []
    state = "follower"
    currentTerm = 0
    Heartbeattimeout = random.randint(6,12)
    electionTimer = random.randint(6,12)
    votedFor = -1
    numVotes = 0
    forfeit = 0
    candidateElectionTimer = 1

    electionTimeout()
 

    # electionTimeoutReturn = 0

    run() #initalize stubs
    while True:
        time.sleep(1)
