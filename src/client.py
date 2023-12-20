import logging
import signal
import sys

import grpc
from protos.generated import editor_pb2_grpc
from protos.generated.editor_pb2 import *

argv = len(sys.argv)
if argv != 3:
    print("Usage: python3 client.py 'ip' 'port' 'cmd' 'pos'")
    exit()

ip = sys.argv[1]
port = sys.argv[2]


def signal_handler(sig, frame):
    print("\nctrl+c pressed")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def to_enum(operation):
    if operation == "ins":
        return INS
    elif operation == "del":
        return DEL
    else:
        print("invalid operation " + operation)
        exit(1)


def get_command():
    op = input("operation: ")
    if op == "exit":
        exit(0)
    op = to_enum(op)
    pos = int(input("position: "))
    char = ''
    if op == INS:
        char = input("char: ")
        while op == INS and len(char) != 1:
            print("please insert a character, not a string")
            char = input("char: ")

    return op, pos, char


def run():
    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        timestamp = 0
        while True:
            op, pos, char = get_command()
            command = Command(operation=op, position=pos, transmitter=USER, char=char)
            response = stub.SendCommand(command)

            timestamp += 1
            if response.status != 0:
                print("operation unsuccessful")
            print(f"Content: {response.content}\n")


if __name__ == "__main__":
    logging.basicConfig()
    run()
