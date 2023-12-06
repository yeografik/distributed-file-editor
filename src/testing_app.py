import logging
import sys

import grpc
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *

argv = len(sys.argv)
if argv != 3:
    print("Usage: python3 app.py 'ip' 'port' 'cmd' 'pos'")
    exit()

ip = sys.argv[1]
port = sys.argv[2]


def to_enum(operation):
    if operation == "ins":
        return INS
    elif operation == "del":
        return DEL
    else:
        print("invalid operation " + operation)
        exit(1)


def get_command():
    op = to_enum(input("operation: "))
    pos = int(input("position: "))
    char = ''
    if op == INS:
        char = input("char: ")
        while op == INS and len(char) != 1:
            print("please insert a character, not a string")
            char = input("char: ")
    id = int(input("id: "))
    clock = int(input("clock: "))

    return op, pos, char, id, clock


def run():
    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        timestamp = 0
        while True:
            op, pos, char, id, clock = get_command()
            command = Command(operation=op, position=pos, id=id, transmitter=SERVER, char=char, clock=clock)
            response = stub.SendCommand(command)

            timestamp += 1
            if response.status != 0:
                print("operation unsuccessful")


if __name__ == "__main__":
    logging.basicConfig()
    run()