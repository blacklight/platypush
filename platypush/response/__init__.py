import json

class Response(object):
    def __init__(self, output=None, errors=[]):
        self.output = output
        self.errors = errors

    def __str__(self):
        return json.dumps({ 'output': self.output, 'error': self.errors })

    def is_error(self):
        return len(self.errors) != 0


# vim:sw=4:ts=4:et:

