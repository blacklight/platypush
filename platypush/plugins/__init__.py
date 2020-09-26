import logging

from functools import wraps

from platypush.event import EventGenerator
from platypush.message.response import Response
from platypush.utils import get_decorators, get_plugin_name_by_class


def action(f):
    @wraps(f)
    def _execute_action(*args, **kwargs):
        response = Response()
        result = f(*args, **kwargs)

        if result and isinstance(result, Response):
            result.errors = result.errors \
                if isinstance(result.errors, list) else [result.errors]
            response = result
        elif isinstance(result, tuple) and len(result) == 2:
            response.errors = result[1] \
                if isinstance(result[1], list) else [result[1]]

            if len(response.errors) == 1 and response.errors[0] is None:
                response.errors = []
            response.output = result[0]
        else:
            response = Response(output=result, errors=[])

        return response

    # Propagate the docstring
    _execute_action.__doc__ = f.__doc__
    return _execute_action


class Plugin(EventGenerator):
    """ Base plugin class """

    def __init__(self, **kwargs):
        super().__init__()
        self.logger = logging.getLogger('platypush:plugin:' + get_plugin_name_by_class(self.__class__))
        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs['logging'].upper()))

        self.registered_actions = set(
            get_decorators(self.__class__, climb_class_hierarchy=True).get('action', [])
        )

    def run(self, method, *args, **kwargs):
        assert method in self.registered_actions, '{} is not a registered action on {}'.\
            format(method, self.__class__.__name__)
        return getattr(self, method)(*args, **kwargs)


# vim:sw=4:ts=4:et:
