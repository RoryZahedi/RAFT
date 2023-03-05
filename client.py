from concurrent import futures

import grpc
import messaging_pb2
import messaging_pb2_grpc
import time
import ipaddress
from _thread import *
import random
from google.protobuf import empty_pb2

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
        time.sleep(3)
        global term,votedFor,forfeit
        peer_ip = context.peer().split(":")[-1]
        otherClientNumber = otherClient[peer_ip]

        receivedTerm = request.term #might be .term or .message
        print(f"Received vote request from {otherClientNumber} with term {receivedTerm}")
        if(receivedTerm > term):
            term = receivedTerm
            votedFor = True
        elif(receivedTerm < term):
            votedFor = False
        elif(receivedTerm == term): # TODO: REMOVE THIS!!! This is not part of RAFT
            if(int(otherClientNumber) > int(clientNum) and votedFor == False):
                votedFor = True
            else:
                votedFor = False
        response = messaging_pb2.electionRequestResponse(
            rt=messaging_pb2.recipientTerm(term=term),
            vg=messaging_pb2.voteGranted(vote=votedFor)
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



def heartBeatTimeout():
    global heartBeatTimer, state
    while True:
        print("in heartbeat")
        print("heartbeattimer:",heartBeatTimer)
        while heartBeatTimer and state == 'f':
            time.sleep(1)
            heartBeatTimer -= 1
        if state == 'f':
            state = 'c'
            election()
       
        
def sendElectionRequests():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,term,votedFor,forfeit,numVotes
    for i in range(0,5):
        if str(i) != clientNum:
            print("Sending request to client",i)
            retval = requestVotesStub[i].SendVoteRequest(messaging_pb2.Term(term=term))
            recipientTerm = retval.rt.term
            receivedVote = bool(retval.vg.vote)
            if receivedVote:
                print("Received vote from",i)
                numVotes+=1
            else:
                if recipientTerm > term:
                    term = recipientTerm
                    forfeit = 1
            

def election():
    global clientNum,clientNumberStubs,messageStubs,requestVotesStub,term,votedFor,forfeit,state,heartBeatTimer,electionTimeoutReturn,numVotes

    if state == 'f' or state == 'l':
        print("Incorrect state:",state)
        return
    print("in election")
    electionTimeoutReturn = 0
    term += 1
    numVotes = 1
    forfeit = 0
    electionTimer = random.randint(6,12)
    sendElectionRequests()
    start_new_thread(electionTimeout, (electionTimer,))   # start timer 
    while electionTimeoutReturn != 1 and numVotes < 3 and forfeit != 1:
        time.sleep(.1)
    print(electionTimeoutReturn,numVotes,forfeit)
    if electionTimeoutReturn:
        print("starting another election")
        time.sleep(2)
        election()
    elif numVotes > 2:
        print("IM LEADER")
        time.sleep(10)
        state = 'l'
        #start sending heartbeats
    elif forfeit == 1:
        state = 'f'
        numVotes = 0
        heartBeatTimer = random.randint(6,12)
    else:
        print("something unexpected happened")


    
def electionTimeout(t):
    global electionTimeoutReturn
    print("in election timeout")
    while t:
        # print(t)
        time.sleep(1)
        t-= 1
    electionTimeoutReturn = 1




       
if __name__ == '__main__':
    print("Client num:",end="")
    clientNum = input()
    start_new_thread(serve, (clientNum,))
    print("Press enter to start")
    input()
    
    clientNumberStubs = []
    messageStubs = []
    requestVotesStub = []

    state = 'f'
    term = 0    
    votedFor = -1
    numVotes = 0
    heartBeatTimer = random.randint(6,12)
    electionTimeoutReturn = 0
    forfeit = 0   # start timer  
    run()
    start_new_thread(heartBeatTimeout, ())
    while True:
        time.sleep(1)
