import os
import sys

class Plugin(object):
    def __init__(self, config):
        self.config = config

        for cls in reversed(self.__class__.mro()):
            if cls is not object:
                try:
                    cls._init(self)
                except AttributeError as e:
                    pass


    def run(self, args):
        raise NotImplementedError()

# vim:sw=4:ts=4:et:

