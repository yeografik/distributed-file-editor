import logging
import sys
from enum import Enum

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


def run():
    user_id = 1  # we need to see how to assign userID's

    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        timestamp = 0
        while True:
            operation = to_enum(input("operation: "))
            position = int(input("position: "))
            command = Command(type=operation, position=position, time_stamp=timestamp, user_id=user_id, transmitter=USER)
            response = stub.SendCommand(command)

            timestamp += 1
            if response.status != 0:
                print("operation unsuccessful")


if __name__ == "__main__":
    logging.basicConfig()
    run()
