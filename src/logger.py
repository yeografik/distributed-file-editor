class Logger:

    def __init__(self):
        self._log = []

    def log(self, cmd_info):
        self._log.append(cmd_info)
        return len(self._log) - 1

    def pop(self):
        return self._log.pop()

    def get_log(self):
        return self._log

    def set_true(self, cmd_id):
        self._log[cmd_id][0] = True

    def get_events_after(self, clock):
        operations_out_of_time = []
        for i in range(0, len(self._log)):
            item = self._log[-1-i]
            if clock > item[4]:
                operations_out_of_time.append(item)
            else:
                break
        return operations_out_of_time


if __name__ == "__main__":
    logger = Logger()
    print(f"{logger.log('info')}")
    print(f"{logger.get_log()}")