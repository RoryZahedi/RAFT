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
    
def serve(clientNum):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingServicer(), server)
    messaging_pb2_grpc.add_ClientNumberServicer_to_server(ClientNumberServicer(), server)
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
    stubs = []
    for i in range(0,5):
        if str(i) != clientNum: 
            port = 'localhost:5005'+str(i)
            channel = grpc.insecure_channel(port)
            stubs.append(messaging_pb2_grpc.ClientNumberStub(channel))
        else:
            stubs.append(-1)
    for i in range(0,5): #Send initial message
        if str(i) != clientNum:
            message = str(clientNum)
            nullret = stubs[i].SendClientNumber(messaging_pb2.Request(message=message))
            
    while True:
        message = input("Enter a message to send: ")
        # response = stub.SendMessage(messaging_pb2.Request(message=message))
        # print(f"Received response: {response.message}")


# def heartBeatTimeout():   
#     while t:
#         time.sleep(1)
#         t-=1
        



       





if __name__ == '__main__':
    global clientNum
    print("Client num:",end="")
    clientNum = input()
    start_new_thread(serve, (clientNum,))
    print("Press enter to start")
    input()
    
    
    # state = 'f'
    # term = 0
    
    # electionTimer = random.rand(6,12)
    # votedFor = -1
    # numVotes = 0
    # heartBeatTimer = random.rand(6,12)
    # t = random.rand(6,12)
    # start_new_thread(heartBeatTimeout,())
   
    
    
    run()
    while True:
        time.sleep(1)
