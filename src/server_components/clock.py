import threading


class Clock:

    def __init__(self):
        self.__time = 0
        self.__lock = threading.Lock()

    def increase(self):
        with self.__lock:
            self.__time += 1
            return self.__time

    def update(self, clock_time):
        with self.__lock:
            self.__time = max(self.__time + 1, clock_time)
            return self.__time

    def get(self):
        return self.__time

    def set(self, time):
        self.__time = time
