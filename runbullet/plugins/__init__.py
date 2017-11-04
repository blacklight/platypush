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


    def run(self, method, *args, **kwargs):
        res = getattr(self, method)(*args, **kwargs)
        return res

# vim:sw=4:ts=4:et:

