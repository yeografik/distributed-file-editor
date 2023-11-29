import sys
import time
from concurrent import futures
import logging
import signal

import grpc
from protos.generated import editor_pb2
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *

me = (sys.argv[1], sys.argv[2])

content = ""


def signal_handler(sig, frame):
    global content
    print("ctrl+c pressed")
    file = open("file.txt", 'w')
    file.write(content)
    file.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def broadcast(request):
    status = 0
    for (ip, port) in active_nodes - {me}:  # broadcasting the cmd
        print(f"broadcasting to: {ip}:{port}")
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            response = stub.SendCommand(
                editor_pb2.Command(type=request.type, position=request.position,
                                   user_id=request.user_id, transmitter=SERVER, char=request.char))
            status += response.status
    return status


def apply_command(request):
    global content
    pos = request.position
    if pos < 0 or pos >= len(content):
        return 1

    if request.type == INS:
        content = content[:pos] + request.char + content[pos:]
    else:
        content = content[:pos] + content[pos + 1:]
    return 0


class Editor(editor_pb2_grpc.EditorServicer):

    def SendCommand(self, request, context):
        if request.type == 0:
            print(f"receiving command: ins({request.char}, {request.position})")
        else:
            print(f"receiving command: del({request.position})")
        print(f"from: user {request.user_id} through {'the app' if request.transmitter == 0 else 'a node'}")
        status = 0
        status += apply_command(request)
        print(f"Content: {content}")


        if request.transmitter == USER and status == 0:
            time.sleep(3)
            status = broadcast(request)

        return editor_pb2.CommandStatus(status=status)

    def Notify(self, request, context):
        node = (request.ip, request.port)
        print(f"Node: {request.ip}:{request.port} is now connected")
        active_nodes.add(node)
        return editor_pb2.NotifyResponse(status=True)

    def RequestContent(self, request, context):
        return editor_pb2.Content(content=content)


server_nodes = {
    ("localhost", "5001"),
    ("localhost", "5002"),
}

active_nodes = set()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    editor_pb2_grpc.add_EditorServicer_to_server(Editor(), server)
    (ip, port) = me
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


def notify(node):
    ip, port = node
    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        try:
            my_ip, my_port = me
            response = stub.Notify(editor_pb2.NodeInfo(ip=my_ip, port=my_port), timeout=5)
            if response.status:
                print(f"Connected to node: {ip}:{port}")
                active_nodes.add((ip, port))
            else:
                print(f"Connection refused by node (timeout): {ip}:{port}")
        except:
            print(f"Connection refused by node: {ip}:{port}")


def request_content_to(node):
    ip, port = node
    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        response = stub.RequestContent(editor_pb2.FileInfo(file_name="file.txt"))
        # TODO: now we have one file, in the future the user could want to access to other files
        return response.content


def read_local_file_content() -> str:
    file_content = ""
    try:
        f = open("file.txt", 'r')
        file_content = f.read()
    except:
        f = open("file.txt", 'x')
    finally:
        f.close()
        return file_content


def setup():
    """This procedure notify to the other nodes that this node is now online.
       Additionally, this node request the content of the file to the other nodes.
       If no others nodes are connected, the local version of the content is used.
    """
    for node in server_nodes - {me}:
        notify(node)

    global content
    if not active_nodes:
        content = read_local_file_content()
        print("Content loaded from file")
    else:
        node = next(iter(active_nodes))
        content = request_content_to(node)
        ip, port = node
        print(f"Content loaded from node: {ip}:{port}")

    print("Content: " + content)


if __name__ == '__main__':
    logging.basicConfig()
    setup()
    serve()
