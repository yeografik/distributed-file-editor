import json
import threading

import grpc
from grpc import StatusCode
from protos.generated import editor_pb2_grpc
from document.doc import Document
from server_components.clock import Clock
from document.command import Command as Cmd
from protos.generated.editor_pb2 import NodeInfo, FileInfo


class Node:

    def __init__(self, me, document: Document, clock: Clock):
        self.server_nodes = set()
        self.active_nodes = set()
        self.document = document
        self.clock = clock
        self.me = me
        self.sync_lock = threading.Lock()
        self.load_server_nodes()
        self.notify_nodes()

    def load_server_nodes(self):
        with open("server_components/config/nodes.json") as f:
            data = json.load(f)
            for node in data['nodes']:
                self.server_nodes.add((node['ip'], node['port']))

    def notify_nodes(self):
        for node in self.server_nodes - {self.me}:
            self.__notify(node)

    def load_data(self):
        if not self.active_nodes:
            self.__read_local_file_content()
            print(f"Content loaded from local file for {self.me}")
        else:
            best_log = []
            content_to_load = ""
            node1 = None
            self.sync_lock.acquire()
            print("sync lock acquired")
            for node in self.active_nodes:
                content, log = self.__request_data_to(node)
                if len(log) >= len(best_log):  # FIXME: Maybe we should check more things
                    best_log = log
                    content_to_load = content
                    node1 = node
            self.document.set_content(content_to_load)
            logger = self.document.get_logger()
            for cmd in best_log:
                logger.log(cmd)
            ip, port = node1
            print(f"Data loaded from node: {ip}:{port}, for {self.me}")
            self.sync_lock.release()
            print("releasing sync lock")

        self.document.get_logger().print_log()
        print(f"Content for {self.me}: \n{self.document.get_content()}")

    def get_active_nodes(self):
        return self.active_nodes

    def remove_active_node(self, ip, port):
        try:
            self.active_nodes.remove((ip, port))
        except KeyError as e:
            return

    def add_active_node(self, node):
        self.active_nodes.add(node)

    def __notify(self, node):
        ip, port = node
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            try:
                my_ip, my_port = self.me
                response = stub.Notify(NodeInfo(ip=my_ip, port=my_port))
                if response.status:
                    print(f"Connected to node: {ip}:{port}")
                    self.clock.set(response.clock)
                    self.active_nodes.add((ip, port))
                else:
                    print(f"Connection refused by node (timeout): {ip}:{port}")
            except Exception as e:
                rpc_state = e.args[0]
                if rpc_state.code == StatusCode.UNAVAILABLE:
                    print(f"Connection refused by node: {ip}:{port}")
                else:
                    raise e

    def __request_data_to(self, node):
        ip, port = node
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            print(f"requesting data to {ip}:{port}")
            stub = editor_pb2_grpc.EditorStub(channel)
            response = stub.RequestContent(FileInfo(file_name="document/file.txt"))
            content = response.content
            log = []
            for cmd in stub.RequestLog(FileInfo(file_name="document/file.txt", ip=self.me[0], port=int(self.me[1]))):
                log.append(Cmd(cmd.operation, cmd.position, cmd.id, cmd.clock, cmd.char))

            return content, log

    def __read_local_file_content(self):
        with open("document/file.txt", 'a+') as f:
            f.seek(0)
            file_content = f.read().strip()
            return self.document.set_content(file_content)
