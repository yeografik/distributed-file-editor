import json

import grpc
from grpc import StatusCode
from protos.generated import editor_pb2_grpc
from protos.generated import editor_pb2
from doc import Document
from clock import Clock


def request_content_to(node, document: Document):
    ip, port = node
    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        response = stub.RequestContent(editor_pb2.FileInfo(file_name="file.txt"))
        # TODO: now we have one file, in the future the user could want to access to other files
        return document.set_content(response.content)


def read_local_file_content(document: Document):
    with open("file.txt", 'a+') as f:
        f.seek(0)
        file_content = f.read()
        return document.set_content(file_content)


class Node:

    def __init__(self, me, document: Document, clock: Clock):
        self.server_nodes = set()
        self.active_nodes = set()
        self.document = document
        self.clock = clock
        self.me = me

    def load_server_nodes(self):
        with open("nodes.json") as f:
            data = json.load(f)
            for node in data['nodes']:
                self.server_nodes.add((node['ip'], node['port']))

    def notify_nodes(self):
        for node in self.server_nodes - {self.me}:
            self.__notify(node)

    def load_data(self):
        if not self.active_nodes:
            read_local_file_content(self.document)
            print("Content loaded from local file")
        else:
            node = next(iter(self.active_nodes))
            request_content_to(node, self.document)
            ip, port = node
            print(f"Content loaded from node: {ip}:{port}")

        print("Content: " + self.document.get_content())

    def get_active_nodes(self):
        return self.active_nodes

    def remove_active_node(self, ip, port):
        self.active_nodes.remove((ip, port))

    def add_active_node(self, node):
        self.active_nodes.add(node)

    def __notify(self, node):
        ip, port = node
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            stub = editor_pb2_grpc.EditorStub(channel)
            try:
                my_ip, my_port = self.me
                response = stub.Notify(editor_pb2.NodeInfo(ip=my_ip, port=my_port), timeout=5)
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
