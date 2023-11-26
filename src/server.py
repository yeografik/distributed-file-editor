from concurrent import futures
import logging

import grpc
from src.protos.generated import editor_pb2
from src.protos.generated import editor_pb2_grpc

ip = "localhost"
port = "5001"


class Editor(editor_pb2_grpc.EditorServicer):
    def SendCommand(self, request, context):
        print("request: " + str(request))
        print("context: " + str(context))
        status = 0
        print(f"{ip}:{port}")
        for ip0, port0 in neighbors - {(ip, port)}:  # broadcasting the cmd
            print(f"broadcasting to: {ip}:{port}")
            with grpc.insecure_channel(f"{ip0}:{port0}") as channel:
                stub = editor_pb2_grpc.EditorStub(channel)
                response = stub.SendCommand(
                    editor_pb2.Command(type=request.type, position=request.position, timeStamp=request.timeStamp,
                                       userID=request.userID))
                status += response.status
        return editor_pb2.CommandStatus(status=status)


neighbors = {
    ("localhost", "5001"),
    # ("localhost", "5002"),
    # ("localhost", "5003")
}


def serve():
    ip = input("ip: ")
    port = input("port: ")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    editor_pb2_grpc.add_EditorServicer_to_server(Editor(), server)
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
