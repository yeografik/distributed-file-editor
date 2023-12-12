import threading


class Clock:

    def __init__(self):
        self.time = 0
        self.lock = threading.Lock()

    def increase(self):
        with self.lock:
            self.time += 1
            return self.time

    def update(self, clock_time):
        with self.lock:
            self.time = max(self.time + 1, clock_time)
            return self.time

    def get(self):
        return self.time

    def set(self, time):
        self.time = time
