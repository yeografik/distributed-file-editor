from protos.generated.editor_pb2 import INS, DEL


class Command:

    def __init__(self, operation, position, who, when, elem=None):
        if operation != INS and operation != DEL:
            raise Exception("Invalid command operation")
        self._operation = operation
        self._position = position
        self._elem = elem
        self._who = who
        self._when = when

    def operation(self):
        return self._operation

    def position(self):
        return self._position

    def elem(self):
        return self._elem

    def when(self):
        return self._when

    def who(self):
        return self._who

    def is_insertion(self):
        return self._operation == INS

    def is_deletion(self):
        return self._operation == DEL

    def set_elem(self, elem):
        if self.is_deletion():
            self._elem = elem
        elif self.is_insertion():
            raise Exception("Can not change the element inserted")

    def get_inverse(self):
        return Command(self._inverse_operation(), self.position(), self.who(), self.when(), self.elem())

    def _inverse_operation(self):
        return DEL if self.operation() == INS else INS

    def __str__(self):
        return f"({self.operation()}, {self.position()}, {self.elem()}, {self.when()}, {self.who()})"
