import sys

class Logger:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message is None:
            return

        if isinstance(message, bytes):
            message = message.decode()

        message = message.rstrip()
        if message and len(message) > 0:
            self.level(message)

    def flush(self):
        pass


# vim:sw=4:ts=4:et:
