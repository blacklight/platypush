import os
import sys
import logging
import traceback

from platypush.response import Response

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
            self._logging = self.config.pop('logging')
        else:
            self._logging = logging.INFO

        logging.basicConfig(level=self._logging)

    def run(self, method, *args, **kwargs):
        try:
            res = getattr(self, method)(*args, **kwargs)
        except Exception as e:
            res = Response(output=None, errors=[e, traceback.format_exc()])

        return res

# vim:sw=4:ts=4:et:

