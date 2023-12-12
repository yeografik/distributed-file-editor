from logger import Logger
from protos.generated.editor_pb2 import *


class Document:

    def __init__(self, content: str = ""):
        self._content = content
        self.logger = Logger()
        self.corrected_operations = []  # [0] boolean: broadcast done, [1] Operation, [2] int: pos,
        # [3] string: char, [4] int: clock

    def get_log(self):
        return self.logger

    def insert_at(self, char, idx):
        if len(char) != 1:
            raise Exception("Character should be inserted")
        if idx not in range(0, len(self._content) + 1):
            raise Exception(f"insert {char} at {idx} - Index out of bound on '{self._content}'")
        self._content = self._content[:idx] + char + self._content[idx:]

    def delete_at(self, idx):
        if idx not in range(0, len(self._content)):
            raise Exception(f"delete at {idx} - Index out of bound on '{self._content}'")
        char = self._content[idx]
        assert len(char) == 1
        self._content = self._content[:idx] + self._content[idx + 1:]
        return char

    def get_content(self):
        return self._content

    def set_content(self, content):
        self._content = content

    def do_rollback(self, request_clock):
        print("Doing rollback")
        operations = self.logger.get_events_after(request_clock)
        inverse_operations = []
        for operation in operations:
            op = DEL if operation[1] == INS else INS
            pos = operation[2]
            char = operation[3]
            inverse_operations.append((op, pos, char, operation[5]))
            self.corrected_operations.insert(0, operation)

        for inverse_operation in inverse_operations:
            print(f"applying {inverse_operation}")
            self.apply(inverse_operation[0], inverse_operation[1], inverse_operation[2], request_clock, inverse_operation[3])

    def apply_rollback_operations(self, prev_op, prev_pos):
        status = 0
        for (broadcast_done, op, pos, char, clock, node_id) in self.corrected_operations:
            if prev_pos < pos:
                if prev_op == INS:
                    status += self.apply(op, pos+1, char, clock, node_id)[0]
                elif prev_op == DEL:
                    status += self.apply(op, pos-1, char, clock, node_id)[0]
                else:
                    raise Exception
            else:
                status += self.apply(op, pos, char, clock, node_id)[0]
        self.corrected_operations.clear()
        return status

    def apply(self, operation, pos, elem, local_clock, node_id):

        # TODO: this operation could fail, a try catch statement should be used
        if operation == INS:
            self.insert_at(elem, pos)
        elif operation == DEL:
            elem = self.delete_at(pos)
        else:
            raise Exception(f"Unknown operation {operation}")

        log_id = self.logger.log((False, operation, pos, elem, local_clock, node_id))
        return 0, log_id
