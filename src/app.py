import logging
import sys
import time

import grpc
import src.protos.generated.editor_pb2_grpc
from src.protos.generated.editor_pb2 import INS, DEL, Command

def toEnum(operation):
    if operation == "ins":
        return INS
    elif operation == "del":
        return DEL
    else:
        print("invalid opration " + operation)
        exit()

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    argv = len(sys.argv)
    if argv != 3:
        print("insuficient arguments provided")
        exit()

    ip = sys.argv[1]
    port = sys.argv[2]
    userID = 1 #we need to see how to assign userID's

    channel = grpc.insecure_channel(ip + ':' + port)
    stub = editor_pb2_grpc.EditorStub(channel)

    while True:
        operation = input("operation: ")
        operation = toEnum(operation)
        position = input("position: ")
        timestamp = time.time()
        #we should change timestamp in Command from int to float
        command = Command(operation, position, timestamp, userID)

        operation_status = stub.SendCommand(command)
        if operation_status != 0:
            print("operation usuccessful")

if __name__ == "__main__":
    logging.basicConfig()
    run()