from concurrent import futures

import grpc
import messaging_pb2
import messaging_pb2_grpc
import time
import ipaddress
from _thread import *


class MessagingServicer(messaging_pb2_grpc.MessagingServicer):
    def SendMessage(self, request, context):
        peer_ip = context.peer().split(":")[-1]
        print(f"Received message: {request.message} from {peer_ip}")
        print()
        return messaging_pb2.Response(message=f"Server received message: {request.message}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messaging_pb2_grpc.add_MessagingServicer_to_server(MessagingServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


def run():
   
    channel = grpc.insecure_channel('localhost:50052')
    stub = messaging_pb2_grpc.MessagingStub(channel)
    while True:
        message = input("Enter a message to send: ")
        response = stub.SendMessage(messaging_pb2.Request(message=message))
        print(f"Received response: {response.message}")

if __name__ == '__main__':
    start_new_thread(serve, ())
    run()
