import os
import sys
import logging

from platypush import get_logging_level
from platypush.response import Response

class Plugin(object):
    def __init__(self, config):
        self.config = config
        logging.basicConfig(stream=sys.stdout, level=get_logging_level()
                            if 'logging' not in config
                            else getattr(logging, config.pop('logging')))

        for cls in reversed(self.__class__.mro()):
            if cls is not object:
                try:
                    cls._init(self)
                except AttributeError as e:
                    pass

    def run(self, method, *args, **kwargs):
        return getattr(self, method)(*args, **kwargs)


# vim:sw=4:ts=4:et:

