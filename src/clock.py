class Clock:

    def __init__(self):
        self.time = 0

    def increase(self):
        self.time += 1

    def update(self, clock_time):
        self.time = max(self.time + 1, clock_time)

    def get(self):
        return self.time

    def set(self, time):
        self.time = time
