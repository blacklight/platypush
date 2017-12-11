import os
import sys
import logging

class Plugin(object):
    def __init__(self, config):
        self.config = config
        self._set_logging()

        for cls in reversed(self.__class__.mro()):
            if cls is not object:
                try:
                    cls._init(self)
                except AttributeError as e:
                    pass

    def _set_logging(self):
        if 'logging' in self.config:
            logging.basicConfig(level=getattr(logging, self.config['logging']))
        else:
            logging.basicConfig(level=logging.INFO)

    def run(self, method, *args, **kwargs):
        res = getattr(self, method)(*args, **kwargs)
        return res

# vim:sw=4:ts=4:et:

