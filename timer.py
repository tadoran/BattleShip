from time import perf_counter


class Timer:
    def __init__(self):
        self.period = 0
        self.exhausted = True

    def start(self, seconds: float):
        self.start_time = perf_counter()
        self.period = seconds
        self.exhausted = False

    def stop(self):
        self.exhausted = True

    def check(self) -> bool:
        if self.exhausted:
            return True
        if perf_counter() - self.start_time < self.period:
            return False
        else:
            self.exhausted = True
            return True