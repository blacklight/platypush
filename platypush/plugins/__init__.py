import sys
import logging
import traceback

from platypush.config import Config
from platypush.message.response import Response
from platypush.utils import get_decorators

def action(f):
    def _execute_action(*args, **kwargs):
        output = None
        errors = []

        try:
            output = f(*args, **kwargs)
            if output and isinstance(output, Response):
                errors = output.errors
                output = output.output
        except Exception as e:
            if isinstance(args[0], Plugin):
                args[0].logger.exception(e)
            errors.append(str(e) + '\n' + traceback.format_exc())

        return Response(output=output, errors=errors)

    # Propagate the docstring
    _execute_action.__doc__ = f.__doc__
    return _execute_action


class Plugin(object):
    """ Base plugin class """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs['logging'].upper()))

        self.registered_actions = set(
            get_decorators(self.__class__, climb_class_hierarchy=True)
            .get('action', [])
        )

    def run(self, method, *args, **kwargs):
        if method not in self.registered_actions:
            raise RuntimeError('{} is not a registered action on {}'.format(
                method, self.__class__.__name__))

        return getattr(self, method)(*args, **kwargs)


# vim:sw=4:ts=4:et:

