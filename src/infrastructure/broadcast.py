import queue
import threading

import grpc
from grpc import StatusCode
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *
from infrastructure.node import Node


class Broadcast(threading.Thread):

    def __init__(self):
        super().__init__()
        self.__cmds = queue.Queue()
        self.__broadcast_lock = threading.Lock()
        self.__stop = False

    def stop(self):
        if self.__cmds.qsize() == 0:
            self.__stop = True
            self.__cmds.put(None)  # This is only for unlock in run method
            return True
        return False

    def enqueue(self, request, local_clock, sender, node: Node, active_nodes):
        self.__cmds.put((request, local_clock, sender, node, active_nodes))

    def lock(self):
        self.__broadcast_lock.acquire()

    def unlock(self):
        self.__broadcast_lock.release()

    def run(self):
        while True:
            cmd_info = self.__cmds.get()
            if self.__stop:
                return
            self.lock()
            self.__broadcast(cmd_info)
            self.unlock()

    @staticmethod
    def __broadcast(cmd_info):
        request, local_clock, sender, node, active_nodes = cmd_info
        status = 0
        for (ip, port) in active_nodes - {sender}:
            with grpc.insecure_channel(f"{ip}:{port}") as channel:
                stub = editor_pb2_grpc.EditorStub(channel)
                try:
                    response = stub.SendCommand(
                        Command(operation=request.operation, position=request.position,
                                id=int(sender[1]), transmitter=SERVER, char=request.char,
                                clock=local_clock))
                    status += response.status
                except Exception as e:
                    rpc_state = e.args[0]
                    if rpc_state.code == StatusCode.UNAVAILABLE:
                        node.remove_active_node(ip, port)
                    elif rpc_state.code == StatusCode.DEADLINE_EXCEEDED:
                        print("Timeout in broadcast")
                    else:
                        raise e
        return status
