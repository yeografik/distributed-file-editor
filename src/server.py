import sys
import threading
from concurrent import futures
import logging
import signal
from time import sleep

import grpc
from grpc import StatusCode
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *
from infrastructure.broadcast import Broadcast
from document.doc import Document
from infrastructure.node import Node
from infrastructure.clock import Clock
from document.command import Command as Cmd
from functools import partial


class Editor(editor_pb2_grpc.EditorServicer):

    def __init__(self, ip, port):
        self.me = (ip, port)
        self.port = int(port)
        self.document = Document()
        self.clock = Clock()
        self.node = Node(self.me, self.document, self.clock)
        self.node_lock = threading.Lock()
        self.cmd_to_broadcast = []
        self.__broadcast_t = Broadcast()
        self.__broadcast_t.start()
        self.node_lock.acquire()

    def SendCommand(self, request, context):
        self.node_lock.acquire()
        local_clock = self.clock.update(request.clock)
        if request.transmitter == SERVER:
            status = self.__handle_server_request(request, local_clock)
        elif request.transmitter == USER:
            status = self.__handle_user_request(request, local_clock)
        else:
            print(f"Couldn't handle request, unknown transmitter: {request.transmitter}")
            status = 1
        self.node_lock.release()
        if status != 0:
            print("error, status: " + str(status))

        content = self.document.get_content()
        print(content)
        return CommandStatus(status=status, content=content)

    def Notify(self, request, context):
        self.__broadcast_t.lock()
        node = (request.ip, request.port)
        print(f"adding server {request.port}")
        self.node.add_active_node(node)
        return NotifyResponse(status=True, clock=self.clock.get())

    def RequestContent(self, request, context):
        return Content(content=self.document.get_content())

    def RequestLog(self, request, context):
        for log in self.document.get_log():
            yield Command(operation=log.operation(), position=log.position(), char=log.elem(),
                          clock=log.when(), id=log.who(), transmitter=SERVER)
        ip, port = request.ip, request.port
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            try:
                response = stub.AreYouReady(SyncConfirmation(answer=True), timeout=10)
                if response.answer:
                    print(f"{ip}:{port} synchronized successfully")
                else:
                    raise Exception(f"{ip}:{port} fails to synchronize")
            except Exception as e:
                rpc_state = e.args[0]
                if rpc_state.code == StatusCode.UNAVAILABLE:
                    print(f"node {ip}:{port} is down")
                elif rpc_state.code == StatusCode.DEADLINE_EXCEEDED:
                    print("Timeout in synchronization")
                else:
                    raise e
        self.__broadcast_t.unlock()

    def AreYouReady(self, request, context):
        return SyncConfirmation(answer=True)

    def __handle_server_request(self, request, local_clock):
        request_clock = request.clock - 1  # Who execute the cmd of the request made it with clock-1
        cmd = Cmd(request.operation, request.position, request.id, request_clock, request.char)
        for cmd1 in self.document.get_log():
            if cmd.who() == cmd1.who() and cmd.when() == cmd1.when():
                return 0

        if request_clock <= local_clock:
            self.document.do_rollback(request_clock, request.id)
            status = self.document.apply(cmd)
            status += self.document.apply_rollback_operations()
        else:
            status = self.document.apply(cmd)

        return status

    def __handle_user_request(self, request, local_clock):
        cmd = Cmd(request.operation, request.position, self.port, local_clock, request.char)
        status = self.document.apply(cmd)
        if status == 0:
            local_clock = self.clock.increase()
            current_active_nodes = self.node.get_active_nodes()
            self.__broadcast_t.enqueue(request, local_clock, self.me, self.node, current_active_nodes)
        return status

    def load_data(self):
        self.node.load_data()
        self.node_lock.release()

    def shutdown(self):
        print("\nctrl+c pressed")
        with open("document/file.txt", 'w') as f:
            f.write(self.document.get_content())
        while not self.__broadcast_t.stop():
            sleep(0.5)
        sys.exit(0)


def sigint_handler(sig, frame, editor):
    editor.shutdown()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ip, port = (sys.argv[1], sys.argv[2])
    editor = Editor(ip, port)
    signal.signal(signal.SIGINT, partial(sigint_handler, editor=editor))
    editor_pb2_grpc.add_EditorServicer_to_server(editor, server)
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    editor.load_data()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
