import sys
import threading
import time
from concurrent import futures
import logging
import signal

import grpc
from grpc import StatusCode
from protos.generated import editor_pb2
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *
from doc import Document
from node import Node
from clock import Clock
from command import Command as Cmd

me = (sys.argv[1], sys.argv[2])
self_port = int(me[1])
document = Document()
clock = Clock()
self_node = Node(me, document, clock)
lock = threading.Lock()


def signal_handler(sig, frame):
    global document
    print("ctrl+c pressed")
    with open("file.txt", 'w') as f:
        f.write(document.get_content())
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def broadcast(request, local_clock):
    status = 0
    if self_port % 2 == 0:
        print("sleeping")
        time.sleep(2)
        print("wake up")
    for (ip, port) in self_node.get_active_nodes() - {me}:  # broadcasting the cmd
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
                    self_node.remove_active_node(ip, port)
                else:
                    raise e
    print("Broadcast finished")
    return status


class BroadcastThread(threading.Thread):

    def __init__(self, request, local_clock):
        super().__init__()
        self._request = request
        self._local_clock = local_clock

    def run(self):
        broadcast(self._request, self._local_clock)


def handle_server_request(request, local_clock):
    print(f"request_clock: {request.clock} - local clock: {local_clock}")
    request_clock = request.clock - 1  # Who execute the cmd of the request made it with clock-1
    cmd = Cmd(request.operation, request.position, request.id, request_clock, request.char)
    if request_clock <= local_clock:  # conflict
        document.do_rollback(request_clock, request.id)
        status = document.apply(cmd)
        # prev_cmd = document.get_log().get_last()
        status += document.apply_rollback_operations()
    else:  # normal broadcast
        status = document.apply(cmd)

    print(f"Content: {document.get_content()}")
    print("releasing lock")
    lock.release()
    print("lock released")
    return status


def handle_user_request(request, local_clock):
    global clock
    # if request.operation == 0:
    #   print(f"receiving command: ins('{request.char}', {request.position})")
    # else:
    #   print(f"receiving command: del({request.position})")
    # print(f"from: user {request.id} through the app")
    cmd = Cmd(request.operation, request.position, self_port, local_clock, request.char)
    status = document.apply(cmd)
    print(f"Content: {document.get_content()}")

    if status == 0:
        local_clock = clock.increase()
        print(f"increasing clock to: {local_clock} before broadcast")
        # time.sleep(3)
        print("releasing lock")
        t = BroadcastThread(request, local_clock)
        t.start()
        lock.release()
        print("lock released")
    else:
        print("releasing lock")
        lock.release()
        print("lock released")

    return status


class Editor(editor_pb2_grpc.EditorServicer):

    def SendCommand(self, request, context):
        global clock
        print("acquiring lock")
        lock.acquire(blocking=True, timeout=-1)
        print("lock acquired")
        print(f"clock when receiving: {clock.get()}")
        local_clock = clock.update(request.clock)
        print(f"increasing clock to: {clock.get()} after receiving")
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
        lock.acquire()
        node = (request.ip, request.port)
        self_node.add_active_node(node)
        lock.release()
        return editor_pb2.NotifyResponse(status=True, clock=clock.get())

    def RequestContent(self, request, context):
        lock.acquire(blocking=True, timeout=5)
        return editor_pb2.Content(content=document.get_content())

    def RequestLog(self, request, context):
        for log in document.get_log().get_log():
            yield editor_pb2.Command(operation=log.operation(), position=log.position(), char=log.elem(),
                                     clock=log.when(), id=log.who(), transmitter=SERVER)
        lock.release()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    editor_pb2_grpc.add_EditorServicer_to_server(Editor(), server)
    (ip, port) = me
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    server.wait_for_termination()


def setup():
    logging.basicConfig()
    self_node.load_server_nodes()
    self_node.notify_nodes()
    self_node.load_data()


if __name__ == '__main__':
    setup()
    serve()
