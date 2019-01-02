import sys

class Logger:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if isinstance(message, bytes):
            message = message.decode()
        if message and message != '\n':
            self.level(message.rstrip())

    def flush(self):
        pass


# vim:sw=4:ts=4:et:
