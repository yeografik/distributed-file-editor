from protos.generated.editor_pb2 import INS, DEL


class Command:

    def __init__(self, operation, position, who, when, elem=None):
        if operation != INS and operation != DEL:
            raise Exception("Invalid command operation")
        self.__operation = operation
        self.__position = position
        self.__elem = elem
        self.__who = who
        self.__when = when

    def operation(self):
        return self.__operation

    def position(self):
        return self.__position

    def elem(self):
        return self.__elem

    def when(self):
        return self.__when

    def who(self):
        return self.__who

    def is_insertion(self):
        return self.__operation == INS

    def is_deletion(self):
        return self.__operation == DEL

    def set_elem(self, elem):
        if self.is_deletion():
            self.__elem = elem
        elif self.is_insertion():
            raise Exception("Can not change the element inserted")

    def get_inverse(self):
        return Command(self.__inverse_operation(), self.position(), self.who(), self.when(), self.elem())

    def __inverse_operation(self):
        return DEL if self.operation() == INS else INS

    def __str__(self):
        return f"({self.operation()}, {self.position()}, {self.elem()}, {self.when()}, {self.who()})"
