import sys
from concurrent import futures
import logging
import signal

import grpc
from protos.generated import editor_pb2
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import USER, SERVER, INS, DEL

ip = sys.argv[1]
port = sys.argv[2]


def signal_handler(sig, frame):
    global file_content
    file = open("doc", 'w')
    file.write(file_content)
    file.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.pause()


def broadcast(request):
    status = 0
    for ip0, port0 in server_nodes - {(ip, port)}:  # broadcasting the cmd
        print(f"broadcasting to: {ip0}:{port0}")
        with grpc.insecure_channel(f"{ip0}:{port0}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            response = stub.SendCommand(
                editor_pb2.Command(type=request.type, position=request.position, time_stamp=request.time_stamp,
                                   user_id=request.user_id, transmitter=SERVER))
            status += response.status
    return status


def apply_command(request):
    global file_content
    pos = request.position
    if pos < 0 | pos >= file_content.len:
        return 1

    if request.type == INS:
        file_content = file_content[:pos] + request.char + file_content[pos:]
    else:
        file_content = file_content[:pos] + request.char + file_content[pos + 1:]
    return 0


class Editor(editor_pb2_grpc.EditorServicer):

    def SendCommand(self, request, context):
        print("request.type:" + str(request.type))
        print("request.position:" + str(request.position))
        print("request.time_stamp:" + str(request.time_stamp))
        print("request.user_id:" + str(request.user_id))
        print("request.transmitter:" + str(request.transmitter))
        print("request.character:" + str(request.char))
        status = 0
        print(f"{ip}:{port}")
        status += apply_command(request)

        if request.transmitter == USER & status == 0:
            status = broadcast(request)

        return editor_pb2.CommandStatus(status=status)


server_nodes = {
    ("localhost", "5001"),
    ("localhost", "5002"),
    # ("localhost", "5003")
}

file_content = ""


def start_file():
    try:
        f = open("doc", 'r')
    except:
        f = open("doc", 'x')
    finally:
        content = f.read()
        f.close()
        return content


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    editor_pb2_grpc.add_EditorServicer_to_server(Editor(), server)
    server.add_insecure_port(f"{ip}:{port}")
    global file_content
    file_content = start_file()
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
