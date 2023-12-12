class Logger:

    def __init__(self):
        self._log = []

    def log(self, cmd_info):
        self._log.append(cmd_info)
        return len(self._log) - 1

    def get_last(self):
        return self._log[-1]

    def get_log(self):
        return self._log

    def get_events_after(self, clock):
        operations_out_of_time = []
        for i in range(0, len(self._log)):
            item = self._log[-1-i]
            # print(f"clock: {clock - 1}, command {i} clock: {item[4]}")
            if clock - 1 <= item[3]:
                operations_out_of_time.append(item)
            else:
                if clock == item[3]:
                    print(f"found request and cmd have same clock: {clock}")
                break
        return operations_out_of_time


if __name__ == "__main__":
    # This is for testing purpose
    logger = Logger()
    print(f"{logger.log('info')}")
    print(f"{logger.get_log()}")
