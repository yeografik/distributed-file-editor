from command import Command
from typing import List


class Logger:

    def __init__(self):
        self.__log = []

    def log(self, cmd: Command):
        self.__log.append(cmd)
        self.print_log()

    def print_log(self):
        print("log:")
        for item in self.get_log():
            print(f"{item}")
        print("")

    def get_last(self) -> Command:
        return self.get_log()[-1]

    def get_log(self) -> List[Command]:
        return self.__log

    def get_events_after(self, clock, port) -> [Command]:
        operations_out_of_time = []
        index_to_remove = []
        for i in range(0, len(self.get_log())):
            cmd: Command = self.get_log()[-1 - i]
            # print(f"clock: {clock - 1}, command {i} clock: {cmd[4]}")
            print(f"checking cmd log: {cmd}")
            if clock < cmd.when():
                print(f"added because: clock < cmd[3] ({clock} < {cmd.when()})")
                operations_out_of_time.append(cmd)
                index_to_remove.append(len(self.get_log()) - 1 - i)
            elif clock == cmd.when():
                if port < cmd.who():
                    print(
                        f"added because: clock == cmd.when ({clock} == {cmd.when()}) and port < cmd.who ({port} < {cmd.who()})")
                    operations_out_of_time.append(cmd)
                    index_to_remove.append(len(self.get_log()) - 1 - i)
            else:
                break
        for index in index_to_remove:
            del self.get_log()[index]
        return operations_out_of_time
