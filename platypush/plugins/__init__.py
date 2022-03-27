import logging
import threading
import time

from functools import wraps
from typing import Optional

from platypush.bus import Bus
from platypush.common import ExtensionWithManifest
from platypush.event import EventGenerator
from platypush.message.response import Response
from platypush.utils import get_decorators, get_plugin_name_by_class, set_thread_name


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


class Plugin(EventGenerator, ExtensionWithManifest):   # lgtm [py/missing-call-to-init]
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


class RunnablePlugin(Plugin):
    """
    Class for runnable plugins - i.e. plugins that have a start/stop method and can be started.
    """
    def __init__(self, poll_interval: Optional[float] = None, **kwargs):
        """
        :param poll_interval: How often the :meth:`.loop` function should be execute (default: None, no pause/interval).
        """
        super().__init__(**kwargs)
        self.poll_interval = poll_interval
        self.bus: Optional[Bus] = None
        self._should_stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def main(self):
        raise NotImplementedError()

    def should_stop(self):
        return self._should_stop.is_set()

    def start(self):
        set_thread_name(self.__class__.__name__)
        self._thread = threading.Thread(target=self._runner)
        self._thread.start()

    def stop(self):
        self._should_stop.set()
        if self._thread and self._thread.is_alive():
            self.logger.info(f'Waiting for {self.__class__.__name__} to stop')
            try:
                if self._thread:
                    self._thread.join()
            except Exception as e:
                self.logger.warning(f'Could not join thread on stop: {e}')

        self.logger.info(f'{self.__class__.__name__} stopped')

    def _runner(self):
        self.logger.info(f'Starting {self.__class__.__name__}')

        while not self.should_stop():
            try:
                self.main()
            except Exception as e:
                self.logger.exception(e)

            if self.poll_interval:
                time.sleep(self.poll_interval)

        self._thread = None


# vim:sw=4:ts=4:et:
