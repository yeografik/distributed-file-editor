# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import editor_pb2 as editor__pb2


class EditorStub(object):
    """The editing service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendCommand = channel.unary_unary(
                '/editor.Editor/SendCommand',
                request_serializer=editor__pb2.Command.SerializeToString,
                response_deserializer=editor__pb2.CommandStatus.FromString,
                )


class EditorServicer(object):
    """The editing service definition.
    """

    def SendCommand(self, request, context):
        """Sends a command
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EditorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendCommand,
                    request_deserializer=editor__pb2.Command.FromString,
                    response_serializer=editor__pb2.CommandStatus.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'editor.Editor', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Editor(object):
    """The editing service definition.
    """

    @staticmethod
    def SendCommand(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/editor.Editor/SendCommand',
            editor__pb2.Command.SerializeToString,
            editor__pb2.CommandStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
