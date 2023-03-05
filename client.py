from concurrent import futures

import grpc
import messaging_pb2
import messaging_pb2_grpc
import time
import ipaddress
from _thread import *
import random
from google.protobuf import empty_pb2


class MessagingServicer(messaging_pb2_grpc.MessagingServicer):
    def SendMessage(self, request, context):
        peer_ip = context.peer().split(":")[-1]
        print(f"Received message: {request.message} from {peer_ip}")
        print()
        return messaging_pb2.Response(message=f"Server received message: {request.message}")
    
class ClientNumberServicer(messaging_pb2_grpc.ClientNumberServicer):
    def SendClientNumber(self, request, context):
        peer_ip = context.peer().split(":")[-1]
        print(f"Received message: {request.message} from {peer_ip}")
        print()
        return empty_pb2.Empty()
    
class RequestVoteServicer(messaging_pb2_grpc.RequestVoteServicer):
    def SendVoteRequest(self,request,context):
        global term,votedFor
        peer_ip = context.peer().split(":")[-1]
        receivedTerm = request.term #might be .term or .message
        print(f"Received vote from {peer_ip} with term {receivedTerm}")
        if(receivedTerm > term):
            term = receivedTerm
            votedFor = True
        elif(receivedTerm < term):
            votedFor = False
            forfeit = 1
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
    global clientNum
    clientNumberStubs = []
    messageStubs = []
    requestVotesStub = []
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
    input()
    for i in range(0,5): 
        if str(i) != clientNum:
            message = str(term)
            retval = requestVotesStub[i].SendVoteRequest(messaging_pb2.Term(term=term))
            print("votegranted = ",retval.vg.vote, "and recipient term = ",retval.rt.term)
    # while True:
    #     message = input("Enter a message to send: ")
    #     for stub in messageStubs:
    #         if stub != -1:
    #             response = stub.SendMessage(messaging_pb2.Request(message=message))
    #             print(f"Received response: {response.message}")



# def heartBeatTimeout():   
#     while True:
#         while heartBeatTimeout:
#             time.sleep(1)
#             heartBeatTimeout-= 1
#         election()
       
        
# def sendElectionRequests():
    #for client in otherClients:
        #sendElectionRequest rpc to client
        #message = str(clientNum)
        #recipientTerm,votedFor = client.SendClientNumber(messaging_pb2.Request(message=message))
        #if votedFor:
            #numVotes+=1
        # else:
        #     if recipientTerm > term:
        #         forfeit = 1
            



# def election():
#     electionTimeoutReturn = 0
#     state = 'c'
#     term += 1
#     votedFor = clientNum
#     numVotes = 1
#     electionTimer = random.randint(6,12)
#     #Send election requests to everyone (term)
#     start_new_thread(electionTimeout, (electionTimer,))   # start timer 
#     while electionTimeoutReturn != 1 or numVotes < 3 or forfeit != 0:
#         time.sleep(.1)
#     if electionTimeoutReturn:
#         election()
#     elif numVotes > 2:
#         state = 'l'
#         #start sending heartbeats
#     elif forfeit == 1:
#         state = 'f'
#         #Set voted for, for person who caused you to forfeit
#         numVotes = 0
#         #set term to be whatever process made us forfeit
#     else:
#         print("something unexpected happened")


        

# def electionTimeout(t):
#     while t:
#         time.sleep(1)
#         t-= 1
#     electionTimeoutReturn = 1




       





if __name__ == '__main__':
    print("Client num:",end="")
    clientNum = input()
    start_new_thread(serve, (clientNum,))
    print("Press enter to start")
    input()
    
    state = 'f'
    term = 0    
    votedFor = -1
    numVotes = 0
    heartBeatTimer = random.randint(6,12)
    forfeit = 0
    
    
    run()
    while True:
        time.sleep(1)
