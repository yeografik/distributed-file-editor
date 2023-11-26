import sys
from concurrent import futures
import logging

import grpc
from protos.generated import editor_pb2
from protos.generated import editor_pb2_grpc

ip = sys.argv[1]
port = sys.argv[2]


class Editor(editor_pb2_grpc.EditorServicer):
    def SendCommand(self, request, context):
        print("request.type:" + str(request.type))
        print("request.position:" + str(request.position))
        print("request.timeStamp:" + str(request.timeStamp))
        print("request.userID:" + str(request.userID))
        status = 0
        print(f"{ip}:{port}")
        for ip0, port0 in neighbors - {(ip, port)}:  # broadcasting the cmd
            print(f"broadcasting to: {ip0}:{port0}")
            with grpc.insecure_channel(f"{ip0}:{port0}") as channel:
                stub = editor_pb2_grpc.EditorStub(channel)
                response = stub.SendCommand(
                    editor_pb2.Command(type=request.type, position=request.position, timeStamp=request.timeStamp,
                                       userID=request.userID))
                status += response.status
        return editor_pb2.CommandStatus(status=status)


neighbors = {
    ("localhost", "5001"),
    ("localhost", "5002"),
    # ("localhost", "5003")
}


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    editor_pb2_grpc.add_EditorServicer_to_server(Editor(), server)
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
