import asyncio
import logging
import threading
import time

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Optional

from platypush.bus import Bus
from platypush.common import ExtensionWithManifest
from platypush.event import EventGenerator
from platypush.message.response import Response
from platypush.utils import get_decorators, get_plugin_name_by_class, set_thread_name

PLUGIN_STOP_TIMEOUT = 5  # Plugin stop timeout in seconds


def action(f: Callable[..., Any]) -> Callable[..., Response]:
    """
    Decorator used to wrap the methods in the plugin classes that should be
    exposed as actions.

    It wraps the method's response into a generic
    :meth:`platypush.message.response.Response` object.
    """

    @wraps(f)
    def _execute_action(*args, **kwargs) -> Response:
        response = Response()
        result = f(*args, **kwargs)

        if result and isinstance(result, Response):
            result.errors = (
                result.errors if isinstance(result.errors, list) else [result.errors]
            )
            response = result
        elif isinstance(result, tuple) and len(result) == 2:
            response.errors = result[1] if isinstance(result[1], list) else [result[1]]

            if len(response.errors) == 1 and response.errors[0] is None:
                response.errors = []
            response.output = result[0]
        else:
            response = Response(output=result, errors=[])

        return response

    # Propagate the docstring
    _execute_action.__doc__ = f.__doc__
    return _execute_action


class Plugin(EventGenerator, ExtensionWithManifest):  # lgtm [py/missing-call-to-init]
    """Base plugin class"""

    def __init__(self, **kwargs):
        super().__init__()
        self.logger = logging.getLogger(
            'platypush:plugin:' + get_plugin_name_by_class(self.__class__)
        )
        if 'logging' in kwargs:
            self.logger.setLevel(getattr(logging, kwargs['logging'].upper()))

        self.registered_actions = set(
            get_decorators(self.__class__, climb_class_hierarchy=True).get('action', [])
        )

    def run(self, method, *args, **kwargs):
        assert (
            method in self.registered_actions
        ), f'{method} is not a registered action on {self.__class__.__name__}'
        return getattr(self, method)(*args, **kwargs)


class RunnablePlugin(Plugin):
    """
    Class for runnable plugins - i.e. plugins that have a start/stop method and can be started.
    """

    def __init__(
        self,
        poll_interval: Optional[float] = None,
        stop_timeout: Optional[float] = PLUGIN_STOP_TIMEOUT,
        **kwargs,
    ):
        """
        :param poll_interval: How often the :meth:`.loop` function should be
            execute (default: None, no pause/interval).
        :param stop_timeout: How long we should wait for any running
            threads/processes to stop before exiting (default: 5 seconds).
        """
        super().__init__(**kwargs)
        self.poll_interval = poll_interval
        self.bus: Optional[Bus] = None
        self._should_stop = threading.Event()
        self._stop_timeout = stop_timeout
        self._thread: Optional[threading.Thread] = None

    def main(self):
        raise NotImplementedError()

    def should_stop(self):
        return self._should_stop.is_set()

    def wait_stop(self, timeout=None):
        return self._should_stop.wait(timeout=timeout)

    def start(self):
        set_thread_name(self.__class__.__name__)
        self._thread = threading.Thread(target=self._runner)
        self._thread.start()

    def stop(self):
        self._should_stop.set()
        if self._thread and self._thread.is_alive():
            self.logger.info('Waiting for %s to stop', self.__class__.__name__)
            try:
                if self._thread:
                    self._thread.join(timeout=self._stop_timeout)
                    if self._thread and self._thread.is_alive():
                        self.logger.warning(
                            'Timeout (seconds={%s}) on exit for the plugin %s',
                            self._stop_timeout,
                            (
                                get_plugin_name_by_class(self.__class__)
                                or self.__class__.__name__
                            ),
                        )
            except Exception as e:
                self.logger.warning('Could not join thread on stop: %s', e)

        self.logger.info('%s stopped', self.__class__.__name__)

    def _runner(self):
        self.logger.info('Starting %s', self.__class__.__name__)

        while not self.should_stop():
            try:
                self.main()
            except Exception as e:
                self.logger.exception(e)

            if self.poll_interval:
                time.sleep(self.poll_interval)

        self._thread = None


class AsyncRunnablePlugin(RunnablePlugin, ABC):
    """
    Class for runnable plugins with an asynchronous event loop attached.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_runner: Optional[threading.Thread] = None
        self._task: Optional[asyncio.Task] = None

    @property
    def _should_start_runner(self):
        return True

    @abstractmethod
    async def listen(self):
        pass

    async def _listen(self):
        try:
            await self.listen()
        except KeyboardInterrupt:
            pass
        except RuntimeError as e:
            if not (
                str(e).startswith('Event loop stopped before ')
                or str(e).startswith('no running event loop')
            ):
                raise e

    def _start_listener(self):
        set_thread_name(self.__class__.__name__ + ':listener')
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._task = self._loop.create_task(self._listen())
        if hasattr(self._task, 'set_name'):
            self._task.set_name(self.__class__.__name__ + '.listen')
        self._loop.run_forever()

    def main(self):
        if self.should_stop() or (self._loop_runner and self._loop_runner.is_alive()):
            self.logger.info('The main loop is already being run/stopped')
            return

        if self._should_start_runner:
            self._loop_runner = threading.Thread(target=self._start_listener)
            self._loop_runner.start()

        self.wait_stop()

    def stop(self):
        if self._task and self._loop and not self._task.done():
            self._loop.call_soon_threadsafe(self._task.cancel)

        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None

        if self._loop_runner and self._loop_runner.is_alive():
            try:
                self._loop_runner.join(timeout=self._stop_timeout)
            finally:
                self._loop_runner = None

        super().stop()


# vim:sw=4:ts=4:et:
