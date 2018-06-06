import sys
import logging

from platypush.config import Config
from platypush.message.response import Response


class Plugin(object):
    """ Base plugin class """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs['logging'].upper()))

    def run(self, method, *args, **kwargs):
        return getattr(self, method)(*args, **kwargs)


# vim:sw=4:ts=4:et:

