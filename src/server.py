import sys
import time
from concurrent import futures
import logging
import signal
import json

import grpc
from protos.generated import editor_pb2
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *

me = (sys.argv[1], sys.argv[2])
server_nodes = set()
active_nodes = set()
content = ""
last_operation = ()  # [0] boolean: broadcast done, [1] Operation operation, [2] int: pos, [3] string: char
rollback_operation = ()  # [0] Operation operation, [1] int: pos, [2] string: char
clock = 0


def signal_handler(sig, frame):
    global content
    print("ctrl+c pressed")
    file = open("file.txt", 'w')
    file.write(content)
    file.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def broadcast(request):
    global clock
    global last_operation
    status = 0
    last_operation = (True, last_operation[1], last_operation[2], last_operation[3])  # this is not correct, any specific peer might not have received the broadcast yet
    for (ip, port) in active_nodes - {me}:  # broadcasting the cmd
        print(f"broadcasting to: {ip}:{port}")
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            response = stub.SendCommand(
                editor_pb2.Command(operation=request.operation, position=request.position,
                                   id=int(me[1]), transmitter=SERVER, char=request.char, clock=clock))
            status += response.status
    return status


def apply(operation, pos, elem):
    global content
    global last_operation
    if pos < 0 or pos > len(content):
        return 1

    if operation == INS:
        content = content[:pos] + elem + content[pos:]
    else:
        assert operation == DEL
        if pos == len(content):  # We cant delete at len(content) but we can insert there.
            return 1
        elem = content[pos]
        content = content[:pos] + content[pos + 1:]

    last_operation = (False, operation, pos, elem)
    return 0


def rollback_required(request_port, self_port):
    global last_operation
    if last_operation[0]:
        return self_port > request_port
    else:
        return True


def do_rollback():
    global last_operation
    global rollback_operation
    operation = DEL if last_operation[1] == INS else INS
    pos = last_operation[2]
    char = last_operation[3]
    rollback_operation = (last_operation[1], pos, char)
    apply(operation, pos, char)


class Editor(editor_pb2_grpc.EditorServicer):

    def SendCommand(self, request, context):
        global clock
        global last_operation
        status = 0
        clock += 1
        if request.transmitter == SERVER and request.clock < clock:  # technically clock == request.clock + 1 when conflict

            rollback = rollback_required(request.id, me[1])
            if rollback:
                do_rollback()
                status += apply(request.operation, request.position, request.char)
                status += apply(rollback_operation[0], rollback_operation[1], rollback_operation[2])
            else:
                status += apply(request.operation, request.position, request.char)
            return editor_pb2.CommandStatus(status=status)

        if request.operation == 0:
            print(f"receiving command: ins('{request.char}', {request.position})")
        else:
            print(f"receiving command: del({request.position})")
        print(f"from: user {request.id} through {'the app' if request.transmitter == 0 else 'a node'}")
        status += apply(request.operation, request.position, request.char)
        clock += 1
        print(f"Content: {content}")

        if request.transmitter == USER and status == 0:
            time.sleep(3)
            status = broadcast(request)
        elif status != 0:
            clock -= 2  # restore clock to maintain consistency
        print(f"Clock: {clock}")
        return editor_pb2.CommandStatus(status=status)

    def Notify(self, request, context):
        node = (request.ip, request.port)
        print(f"Node: {request.ip}:{request.port} is now connected")
        active_nodes.add(node)
        return editor_pb2.NotifyResponse(status=True)

    def RequestContent(self, request, context):
        return editor_pb2.Content(content=content)


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
    with open("file.txt", 'a+') as f:
        f.seek(0)
        file_content = f.read()
        return file_content


def load_server_nodes():
    with open("nodes.json") as f:
        data = json.load(f)
        for node in data['nodes']:
            server_nodes.add((node['ip'], node['port']))


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
    load_server_nodes()
    setup()
    serve()
