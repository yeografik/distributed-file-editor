class Logger:

    def __init__(self):
        self._log = []

    def log(self, cmd_info):
        self._log.append(cmd_info)
        print("log:")
        for item in self._log:
            print(f"{item}")
        print("")
        return len(self._log) - 1

    def get_last(self):
        return self._log[-1]

    def get_log(self):
        return self._log

    def get_events_after(self, clock, port):
        operations_out_of_time = []
        index_to_remove = []
        for i in range(0, len(self._log)):
            item = self._log[-1-i]
            # print(f"clock: {clock - 1}, command {i} clock: {item[4]}")
            print(f"checking item log: {item}")
            if clock < item[3]:
                print(f"added because: clock < item[3] ({clock} < {item[3]})")
                operations_out_of_time.append(item)
                index_to_remove.append(len(self._log) - 1 - i)
            elif clock == item[3]:
                if port < item[4]:
                    print(f"added because: diff(clock, item[3]) <= 1 (diff({clock}, {item[3]}) <= 1) and port < item[4] ({port} < {item[4]})")
                    operations_out_of_time.append(item)
                    index_to_remove.append(len(self._log) - 1 - i)
            else:
                break
        for index in index_to_remove:
            del self._log[index]
        return operations_out_of_time


if __name__ == "__main__":
    # This is for testing purpose
    logger = Logger()
    print(f"{logger.log('info')}")
    print(f"{logger.get_log()}")
