class ClientNumberServicer(messaging_pb2_grpc.ClientNumberServicer):
    def SendClientNumber(self, request, context):
        global clientNumberStubs,messageStubs,requestVotesStub,heartbeatStubs,AppendEntriesStubs,CommitStubs,terminalStubs,secondTime,clientNum
        peer_ip = context.peer().split(":")[-1]
        otherClient[peer_ip] = request.message
        print(f"Received message: {request.message} from {otherClient[peer_ip]}")
        print()

        port = 'localhost:5005'+str(request.message)
        channel = grpc.insecure_channel(port)
        

        # print(otherClient)
        i = int(request.message)
        if len(clientNumberStubs) == 5 and secondTime > 3:
            print("resetting for",i)
            clientNumberStubs[i] = messaging_pb2_grpc.ClientNumberStub(channel)
            messageStubs[i] = messaging_pb2_grpc.MessagingStub(channel)
            requestVotesStub[i] = messaging_pb2_grpc.RequestVoteStub(channel)
            heartbeatStubs[i] = messaging_pb2_grpc.HeartbeatStub(channel)
            AppendEntriesStubs[i] = messaging_pb2_grpc.AppendEntriesStub(channel)
            CommitStubs[i] = messaging_pb2_grpc.CommitStub(channel)
            terminalStubs[i] = messaging_pb2_grpc.RedirectStub(channel)
        secondTime += 1
        return  empty_pb2.Empty()