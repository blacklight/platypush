import sys
import logging

from platypush.config import Config
from platypush.message.response import Response

class Plugin(object):
    """ Base plugin class """

    def __init__(self, **kwargs):
        logging.basicConfig(stream=sys.stdout, level=Config.get('logging')
                            if 'logging' not in kwargs
                            else getattr(logging, kwargs['logging']))

    def run(self, method, *args, **kwargs):
        return getattr(self, method)(*args, **kwargs)


# vim:sw=4:ts=4:et:

