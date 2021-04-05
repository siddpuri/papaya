import time


class Logger:
    def __init__(self) -> None:
        pass

    def log(self, message: str) -> None:
        print(f'{time.ctime()}: {message}')
