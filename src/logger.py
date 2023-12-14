from src.command import Command

class Logger:

    def __init__(self):
        self._log = []

    def log(self, cmd: Command):
        self._log.append(cmd)
        print("log:")
        for item in self._log:
            print(f"{item}")
        print("")

    def get_last(self) -> Command:
        return self._log[-1]

    def get_log(self):
        return self._log

    def get_events_after(self, clock, port) -> [Command]:
        operations_out_of_time = []
        index_to_remove = []
        for i in range(0, len(self._log)):
            cmd: Command = self._log[-1-i]
            # print(f"clock: {clock - 1}, command {i} clock: {cmd[4]}")
            print(f"checking cmd log: {cmd}")
            if clock < cmd.when():
                print(f"added because: clock < cmd[3] ({clock} < {cmd.when()})")
                operations_out_of_time.append(cmd)
                index_to_remove.append(len(self._log) - 1 - i)
            elif clock == cmd.when():
                if port < cmd.who():
                    print(f"added because: clock == cmd.when ({clock} == {cmd.when()}) and port < cmd.who ({port} < {cmd.who()})")
                    operations_out_of_time.append(cmd)
                    index_to_remove.append(len(self._log) - 1 - i)
            else:
                break
        for index in index_to_remove:
            del self._log[index]
        return operations_out_of_time

