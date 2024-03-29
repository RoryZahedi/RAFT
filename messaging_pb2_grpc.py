# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import messaging_pb2 as messaging__pb2


class MessagingStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendMessage = channel.unary_unary(
                '/messaging.Messaging/SendMessage',
                request_serializer=messaging__pb2.Request.SerializeToString,
                response_deserializer=messaging__pb2.Response.FromString,
                )


class MessagingServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MessagingServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMessage,
                    request_deserializer=messaging__pb2.Request.FromString,
                    response_serializer=messaging__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.Messaging', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Messaging(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.Messaging/SendMessage',
            messaging__pb2.Request.SerializeToString,
            messaging__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class HeartbeatStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendHeartbeat = channel.unary_unary(
                '/messaging.Heartbeat/SendHeartbeat',
                request_serializer=messaging__pb2.SendAppendEntriesArgs.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class HeartbeatServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendHeartbeat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_HeartbeatServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendHeartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.SendHeartbeat,
                    request_deserializer=messaging__pb2.SendAppendEntriesArgs.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.Heartbeat', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Heartbeat(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendHeartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.Heartbeat/SendHeartbeat',
            messaging__pb2.SendAppendEntriesArgs.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ClientNumberStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendClientNumber = channel.unary_unary(
                '/messaging.ClientNumber/SendClientNumber',
                request_serializer=messaging__pb2.Request.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class ClientNumberServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendClientNumber(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ClientNumberServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendClientNumber': grpc.unary_unary_rpc_method_handler(
                    servicer.SendClientNumber,
                    request_deserializer=messaging__pb2.Request.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.ClientNumber', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ClientNumber(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendClientNumber(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.ClientNumber/SendClientNumber',
            messaging__pb2.Request.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class RequestVoteStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendVoteRequest = channel.unary_unary(
                '/messaging.RequestVote/SendVoteRequest',
                request_serializer=messaging__pb2.RequestVoteArgs.SerializeToString,
                response_deserializer=messaging__pb2.electionRequestResponse.FromString,
                )


class RequestVoteServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendVoteRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RequestVoteServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendVoteRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.SendVoteRequest,
                    request_deserializer=messaging__pb2.RequestVoteArgs.FromString,
                    response_serializer=messaging__pb2.electionRequestResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.RequestVote', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RequestVote(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendVoteRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.RequestVote/SendVoteRequest',
            messaging__pb2.RequestVoteArgs.SerializeToString,
            messaging__pb2.electionRequestResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class AppendEntriesStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendAppendEntries = channel.unary_unary(
                '/messaging.AppendEntries/SendAppendEntries',
                request_serializer=messaging__pb2.SendAppendEntriesArgs.SerializeToString,
                response_deserializer=messaging__pb2.SendAppendEntriesResponse.FromString,
                )


class AppendEntriesServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendAppendEntries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AppendEntriesServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendAppendEntries': grpc.unary_unary_rpc_method_handler(
                    servicer.SendAppendEntries,
                    request_deserializer=messaging__pb2.SendAppendEntriesArgs.FromString,
                    response_serializer=messaging__pb2.SendAppendEntriesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.AppendEntries', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AppendEntries(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendAppendEntries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.AppendEntries/SendAppendEntries',
            messaging__pb2.SendAppendEntriesArgs.SerializeToString,
            messaging__pb2.SendAppendEntriesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class CommitStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendCommitUpdate = channel.unary_unary(
                '/messaging.Commit/SendCommitUpdate',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class CommitServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendCommitUpdate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CommitServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendCommitUpdate': grpc.unary_unary_rpc_method_handler(
                    servicer.SendCommitUpdate,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.Commit', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Commit(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendCommitUpdate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.Commit/SendCommitUpdate',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class RedirectStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendTerminalCommandRedirect = channel.unary_unary(
                '/messaging.Redirect/SendTerminalCommandRedirect',
                request_serializer=messaging__pb2.TerminalArgs.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class RedirectServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendTerminalCommandRedirect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RedirectServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendTerminalCommandRedirect': grpc.unary_unary_rpc_method_handler(
                    servicer.SendTerminalCommandRedirect,
                    request_deserializer=messaging__pb2.TerminalArgs.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.Redirect', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Redirect(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendTerminalCommandRedirect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/messaging.Redirect/SendTerminalCommandRedirect',
            messaging__pb2.TerminalArgs.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
