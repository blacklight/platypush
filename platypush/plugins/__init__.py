import asyncio
import logging
import threading
import warnings

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Optional
from typing_extensions import override

from platypush.bus import Bus
from platypush.common import ExtensionWithManifest
from platypush.event import EventGenerator
from platypush.message.response import Response
from platypush.utils import get_decorators, get_plugin_name_by_class

PLUGIN_STOP_TIMEOUT = 5  # Plugin stop timeout in seconds
logger = logging.getLogger(__name__)


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
        try:
            result = f(*args, **kwargs)
        except TypeError as e:
            logger.exception(e)
            result = Response(errors=[str(e)])

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

    @property
    def _db(self):
        """
        :return: The reference to the :class:`platypush.plugins.db.DbPlugin`.
        """
        from platypush.context import get_plugin
        from platypush.plugins.db import DbPlugin

        db: DbPlugin = get_plugin(DbPlugin)  # type: ignore
        assert db, 'db plugin not initialized'
        return db

    @property
    def _redis(self):
        """
        :return: The reference to the :class:`platypush.plugins.redis.RedisPlugin`.
        """
        from platypush.context import get_plugin
        from platypush.plugins.redis import RedisPlugin

        redis: RedisPlugin = get_plugin(RedisPlugin)  # type: ignore
        assert redis, 'db plugin not initialized'
        return redis

    @property
    def _entities(self):
        """
        :return: The reference to the :class:`platypush.plugins.entities.EntitiesPlugin`.
        """
        from platypush.context import get_plugin
        from platypush.plugins.entities import EntitiesPlugin

        entities: EntitiesPlugin = get_plugin('entities')  # type: ignore
        assert entities, 'entities plugin not initialized'
        return entities

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
        poll_interval: Optional[float] = 15,
        stop_timeout: Optional[float] = PLUGIN_STOP_TIMEOUT,
        **kwargs,
    ):
        """
        :param poll_interval: How often the :meth:`.loop` function should be
            execute (default: 15 seconds). *NOTE*: For back-compatibility
            reasons, the `poll_seconds` argument is also supported, but it's
            deprecated.
        :param stop_timeout: How long we should wait for any running
            threads/processes to stop before exiting (default: 5 seconds).
        """
        super().__init__(**kwargs)
        self.poll_interval = poll_interval
        self.bus: Optional[Bus] = None
        self._should_stop = threading.Event()
        self._stop_timeout = stop_timeout
        self._thread: Optional[threading.Thread] = None

        if kwargs.get('poll_seconds') is not None:
            warnings.warn(
                'poll_seconds is deprecated, use poll_interval instead',
                DeprecationWarning,
                stacklevel=2,
            )

            if self.poll_interval is None:
                self.poll_interval = kwargs['poll_seconds']

    def main(self):
        """
        Implementation of the main loop of the plugin.
        """
        raise NotImplementedError()

    def should_stop(self) -> bool:
        return self._should_stop.is_set()

    def wait_stop(self, timeout=None):
        """
        Wait until a stop event is received.
        """
        return self._should_stop.wait(timeout=timeout)

    def start(self):
        """
        Start the plugin.
        """
        self._thread = threading.Thread(
            target=self._runner, name=self.__class__.__name__
        )
        self._thread.start()

    def stop(self):
        """
        Stop the plugin.
        """
        self._should_stop.set()
        if (
            self._thread
            and self._thread != threading.current_thread()
            and self._thread.is_alive()
        ):
            self.logger.info('Waiting for the plugin to stop')
            try:
                if self._thread:
                    self._thread.join(timeout=self._stop_timeout)
                    if self._thread and self._thread.is_alive():
                        self.logger.warning(
                            'Timeout (seconds=%s) on exit for the plugin',
                            self._stop_timeout,
                        )
            except Exception as e:
                self.logger.warning('Could not join thread on stop: %s', e)

        self.logger.info('%s stopped', self.__class__.__name__)

    def _runner(self):
        """
        Implementation of the runner thread.
        """
        self.logger.info('Starting %s', self.__class__.__name__)

        while not self.should_stop():
            try:
                self.main()
            except Exception as e:
                self.logger.exception(e)

            if self.poll_interval:
                self.wait_stop(self.poll_interval)

        self._thread = None


class AsyncRunnablePlugin(RunnablePlugin, ABC):
    """
    Class for runnable plugins with an asynchronous event loop attached.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop()
        self._task: Optional[asyncio.Task] = None

    @property
    def _should_start_runner(self):
        """
        This property is used to determine if the runner and the event loop
        should be started for this plugin.
        """
        return True

    @abstractmethod
    async def listen(self):
        """
        Main body of the async plugin. When it's called, the event loop should
        already be running and available over `self._loop`.
        """

    async def _listen(self):
        """
        Wrapper for :meth:`.listen` that catches any exceptions and logs them.
        """
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

    def _run_listener(self):
        """
        Initialize an event loop and run the listener as a task.
        """
        asyncio.set_event_loop(self._loop)

        self._task = self._loop.create_task(self._listen())
        if hasattr(self._task, 'set_name'):
            self._task.set_name(self.__class__.__name__ + '.listen')
        try:
            self._loop.run_until_complete(self._task)
        except Exception as e:
            if not self.should_stop():
                self.logger.warning('The loop has terminated with an error')
                self.logger.exception(e)

        self._task.cancel()

    @override
    def main(self):
        if self.should_stop():
            self.logger.info('The plugin is already scheduled to stop')
            return

        self._loop = asyncio.new_event_loop()

        if self._should_start_runner:
            while not self.should_stop():
                try:
                    self._run_listener()
                finally:
                    self.wait_stop(self.poll_interval)
        else:
            self.wait_stop()

    @override
    def stop(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None

        super().stop()


# vim:sw=4:ts=4:et:
