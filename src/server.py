import sys
import time
from concurrent import futures
import logging
import signal
import json

import grpc
from grpc import StatusCode
from protos.generated import editor_pb2
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *
from doc import Document

me = (sys.argv[1], sys.argv[2])
server_nodes = set()
active_nodes = set()
self_port = int(me[1])
document: Document
clock = 0


def signal_handler(sig, frame):
    global document
    print("ctrl+c pressed")
    with open("file.txt", 'w') as f:
        f.write(document.get_content())
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def broadcast(request, cmd_id):
    global clock
    local_clock = clock
    status = 0
    document.get_log().set_true(cmd_id)
    # print("broadcasting")
    # this is not correct, any specific peer might not have received the broadcast yet
    for (ip, port) in active_nodes - {me}:  # broadcasting the cmd
        # print(f"broadcasting to: {ip}:{port}")
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            try:
                response = stub.SendCommand(
                    editor_pb2.Command(operation=request.operation, position=request.position,
                                       id=int(me[1]), transmitter=SERVER, char=request.char, clock=local_clock))
                status += response.status
            except Exception as e:
                rpc_state = e.args[0]
                if rpc_state.code == StatusCode.UNAVAILABLE:
                    print(f"node: {ip}:{port} is down")
                    active_nodes.remove((ip, port))
                else:
                    raise e
    return status


def broadcast_done(operation):
    return operation[0]


def must_local_port_rollback(request_port):
    return self_port > request_port


def rollback_required(request_port):
    last_operation = document.get_log().get_last()
    print(f"this {self_port} - other {request_port}")
    if not broadcast_done(last_operation):
        print(f"{self_port} must rollback")
        return True
    if must_local_port_rollback(request_port):
        print(f"{self_port} must rollback")
    else:
        print(f"{request_port} must rollback")
    return must_local_port_rollback(request_port)


def handle_server_request(request, local_clock):
    global clock
    print(f"request_clock: {request.clock} - local clock: {local_clock}")
    if request.clock < local_clock:  # conflict
        if rollback_required(request.id):
            document.do_rollback(request.clock)
            clock += 1
            status = document.apply(request.operation, request.position, request.char, request.clock)[0]
            status += document.apply_rollback_operations()
        else:
            status = document.apply(request.operation, request.position, request.char, request.clock)[0]
        # print(f"Rollback Clock: {clock}")
    else:  # normal broadcast
        # if request.operation == 0:
        # print(f"receiving command: ins('{request.char}', {request.position})")
        # else:
        # print(f"receiving command: del({request.position})")
        # print(f"from: server {request.id}")
        status = document.apply(request.operation, request.position, request.char, request.clock)[0]

    print(f"Content: {document.get_content()}")
    return status


def handle_user_request(request, local_clock):
    global clock
    # if request.operation == 0:
    #   print(f"receiving command: ins('{request.char}', {request.position})")
    # else:
    #   print(f"receiving command: del({request.position})")
    # print(f"from: user {request.id} through the app")
    status, log_id = document.apply(request.operation, request.position, request.char, local_clock)
    print(f"Content: {document.get_content()}")

    if status == 0:
        clock += 1
        print(f"increasing clock to: {clock} before broadcast")
        time.sleep(3)
        status = broadcast(request, log_id)

    return status


class Editor(editor_pb2_grpc.EditorServicer):

    def SendCommand(self, request, context):
        global clock
        clock = max(clock + 1, request.clock)
        local_clock = clock
        # print(f"increasing clock to: {clock} after receiving")
        print(f"msg clock: {request.clock} - curr clock: {local_clock} - transmitter: {request.transmitter}")
        if request.transmitter == SERVER:
            status = handle_server_request(request, local_clock)
        elif request.transmitter == USER:
            status = handle_user_request(request, local_clock)
        else:
            print(f"Couldn't handle request, unknown transmitter: {request.transmitter}")
            status = 1

        if status != 0:
            print("error, status: " + str(status))
        return editor_pb2.CommandStatus(status=status)

    def Notify(self, request, context):
        node = (request.ip, request.port)
        # print(f"Node: {request.ip}:{request.port} is now connected")
        active_nodes.add(node)
        return editor_pb2.NotifyResponse(status=True)

    def RequestContent(self, request, context):
        return editor_pb2.Content(content=document.get_content())


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    editor_pb2_grpc.add_EditorServicer_to_server(Editor(), server)
    (ip, port) = me
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    # print("Server started, listening on " + port)
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
        except Exception as e:
            rpc_state = e.args[0]
            if rpc_state.code == StatusCode.UNAVAILABLE:
                print(f"Connection refused by node: {ip}:{port}")
            else:
                raise e


def request_content_to(node) -> Document:
    ip, port = node
    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        response = stub.RequestContent(editor_pb2.FileInfo(file_name="file.txt"))
        # TODO: now we have one file, in the future the user could want to access to other files
        return Document(response.content)


def read_local_file_content() -> Document:
    with open("file.txt", 'a+') as f:
        f.seek(0)
        file_content = f.read()
        return Document(file_content)


def load_server_nodes():
    with open("nodes.json") as f:
        data = json.load(f)
        for node in data['nodes']:
            server_nodes.add((node['ip'], node['port']))


def notify_nodes():
    for node in server_nodes - {me}:
        notify(node)


def load_data():
    global document
    if not active_nodes:
        document = read_local_file_content()
        print("Content loaded from local file")
    else:
        node = next(iter(active_nodes))
        document = request_content_to(node)
        ip, port = node
        print(f"Content loaded from node: {ip}:{port}")

    print("Content: " + document.get_content())


def setup():
    logging.basicConfig()
    load_server_nodes()
    notify_nodes()
    load_data()


if __name__ == '__main__':
    setup()
    serve()
