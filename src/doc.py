from logger import Logger
from protos.generated.editor_pb2 import *
from src.command import Command

class Document:

    def __init__(self, content: str = ""):
        self._content = content
        self.logger = Logger()
        self.logging = True
        self.corrected_operations = []  # [0] Operation, [1] int: pos,
        # [2] string: char, [3] int: clock, [4] int: port

    def get_log(self):
        return self.logger

    def _insert_at(self, char, idx):
        if len(char) != 1:
            raise Exception("Character should be inserted")
        if idx not in range(0, len(self._content) + 1):
            raise Exception(f"insert {char} at {idx} - Index out of bound on '{self._content}'")
        self._content = self._content[:idx] + char + self._content[idx:]

    def _delete_at(self, idx):
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

    def do_rollback(self, request_clock, request_port):
        print("Doing rollback")
        operations = self.logger.get_events_after(request_clock, request_port)
        inverse_operations = []
        for operation in operations:
            op = DEL if operation[0] == INS else INS
            pos = operation[1]
            char = operation[2]
            inverse_operations.append((op, pos, char, operation[4]))
            self.corrected_operations.insert(0, operation)

        for inverse_operation in inverse_operations:
            # print(f"applying {inverse_operation}")
            self.logging = False
            self.apply(inverse_operation[0], inverse_operation[1], inverse_operation[2], request_clock, inverse_operation[3])
            self.logging = True
        print(f"Rollback done: {self._content}")

    def apply_rollback_operations(self):
        status = 0
        for (op, pos, char, clock, node_id) in self.corrected_operations:
            status += self.apply(op, pos, char, clock, node_id)
        self.corrected_operations.clear()
        return status

    def apply(self, cmd: Command):

        # TODO: this operation could fail, a try catch statement should be used
        if cmd.is_insertion():
            self._insert_at(cmd.elem(), cmd.position())
        elif cmd.is_deletion():
            cmd.set_elem(self._delete_at(cmd.position()))

        if self.logging:
            self.logger.log(cmd)
        return 0
