import logging
import sys

import grpc
from src.protos.generated import editor_pb2_grpc
from src.protos.generated.editor_pb2 import INS, DEL, Command


def to_enum(operation):
    if operation == "ins":
        return INS
    elif operation == "del":
        return DEL
    else:
        print("invalid operation " + operation)
        exit(1)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    # argv = len(sys.argv)
    # if argv != 3:
    #     print("insufficient arguments provided")
    #     exit()

    # ip = sys.argv[1]
    # port = sys.argv[2]
    ip = input("node ip: ")
    port = input("node port: ")
    user_id = 1  # we need to see how to assign userID's

    with grpc.insecure_channel(f"{ip}:{port}") as channel:
        stub = editor_pb2_grpc.EditorStub(channel)
        timestamp = 0
        while True:
            operation = input("operation: ")
            operation = to_enum(operation)
            position = int(input("position: "))
            # timestamp = time.time()
            # we should change timestamp in Command from int to float
            command = Command(type=operation, position=position, timeStamp=timestamp, userID=user_id)
            response = stub.SendCommand(command)

            timestamp += 1
            if response.status != 0:
                print("operation unsuccessful")


if __name__ == "__main__":
    logging.basicConfig()
    run()
