from logger import Logger
from command import Command


class Document:

    def __init__(self, content: str = ""):
        self.__content = content
        self.__logger = Logger()
        self.__logging = True
        self.__corrected_commands = []

    def get_logger(self):
        return self.__logger

    def get_log(self):
        return self.__logger.get_log()

    def __insert_at(self, char, idx):
        if len(char) != 1:
            raise Exception("Character should be inserted")
        if idx not in range(0, len(self.__content) + 1):
            raise Exception(f"insert {char} at {idx} - Index out of bound on '{self.__content}'")
        self.__content = self.__content[:idx] + char + self.__content[idx:]

    def __delete_at(self, idx):
        if idx not in range(0, len(self.__content)):
            raise Exception(f"delete at {idx} - Index out of bound on '{self.__content}'")
        char = self.__content[idx]
        assert len(char) == 1
        self.__content = self.__content[:idx] + self.__content[idx + 1:]
        return char

    def get_content(self):
        return self.__content

    def set_content(self, content):
        self.__content = content

    def do_rollback(self, request_clock, request_port):
        commands_to_revert = self.__logger.get_events_after(request_clock, request_port)
        inverse_commands = []
        for cmd in commands_to_revert:
            inverse_commands.append(cmd.get_inverse())
            self.__corrected_commands.insert(0, cmd)

        for cmd in inverse_commands:
            # print(f"applying {cmd}")
            self.__logging = False
            self.apply(cmd)
            self.__logging = True

    def apply_rollback_operations(self):
        status = 0
        for cmd in self.__corrected_commands:
            status += self.apply(cmd)
        self.__corrected_commands.clear()
        return status

    def apply(self, cmd: Command):

        # TODO: this operation could fail, a try catch statement should be used
        if cmd.is_insertion():
            self.__insert_at(cmd.elem(), cmd.position())
        elif cmd.is_deletion():
            cmd.set_elem(self.__delete_at(cmd.position()))

        if self.__logging:
            self.__logger.log(cmd)
        return 0
