import json
import threading
import time
from typing import Dict, Union

from platypush.backend.http.utils import HttpUtils
from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.procedure import Procedure
from platypush.utils import get_enabled_plugins


class UtilsPlugin(Plugin):
    """
    A plugin for general-purpose util methods
    """

    _DEFAULT_TIMEOUT_PREFIX = '_PlatypushTimeout_'
    _timeout_hndl_idx = 0
    _timeout_hndl_idx_lock = threading.RLock()

    _DEFAULT_INTERVAL_PREFIX = '_PlatypushInterval_'
    _interval_hndl_idx = 0
    _interval_hndl_idx_lock = threading.RLock()

    _pending_timeouts: Dict[str, Union[Procedure, threading.Timer]] = {}
    _pending_intervals: Dict[str, Union[Procedure, threading.Thread]] = {}
    _pending_timeouts_lock = threading.RLock()
    _pending_intervals_lock = threading.RLock()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._plugins = {}
        self._plugins_lock = threading.RLock()

    @action
    def sleep(self, seconds):
        """
        Make the current executor sleep for the specified number of seconds.

        :param seconds: Sleep seconds
        :type seconds: float
        """

        time.sleep(seconds)

    @action
    def set_timeout(self, seconds, actions, name=None, **args):
        """
        Define a set of actions to run after the specified amount of `seconds`.

        :param seconds: Number of seconds before running the timeout procedure
        :type seconds: float

        :param actions: List of actions to be executed after the timeout expires
        :type actions: list[dict]

        :param name: Set an optional name for this timeout. It is advised to set
            a name if you are planning to programmatically cancel the timeout in
            your business logic.
        :type name: str

        :param args: Optional arguments/context to pass to the timeout function
        """

        with self._timeout_hndl_idx_lock:
            self._timeout_hndl_idx += 1
            if not name:
                name = self._DEFAULT_TIMEOUT_PREFIX + str(self._timeout_hndl_idx)
            if name in self._pending_timeouts:
                return (None, f"A timeout named '{name}' is already awaiting")

        procedure = Procedure.build(name=name, requests=actions, _async=False)
        self._pending_timeouts[name] = procedure

        def _proc_wrapper(procedure, **kwargs):
            try:
                procedure.execute(**kwargs)
            finally:
                with self._pending_timeouts_lock:
                    if name in self._pending_timeouts:
                        del self._pending_timeouts[name]

        with self._pending_timeouts_lock:
            self._pending_timeouts[name] = threading.Timer(
                seconds, _proc_wrapper, args=[procedure], kwargs=args
            )
        self._pending_timeouts[name].start()

    @action
    def clear_timeout(self, name):
        """
        Clear a pending timeout procedure

        :param name: Name of the timeout to clear
        :type name: str
        """
        with self._pending_timeouts_lock:
            if name not in self._pending_timeouts:
                self.logger.debug('%s is not a pending timeout', name)
                return
            timer = self._pending_timeouts.pop(name)

        timer.cancel()

    @action
    def get_timeouts(self):
        """
        Get info about the pending timeouts

        :returns: dict.

        Example::

            {
                "test_timeout": {
                    "seconds": 10.0,
                    "actions": [
                        {
                            "action": "action_1",
                            "args": {
                                "name_1": "value_1"
                            }
                        }
                    ]
                }
            }

        """

        response = {}

        for name in self._pending_timeouts:
            # pylint: disable=no-member
            response[name] = self.get_timeout(name).output.get(name)
        return response

    @action
    def get_timeout(self, name):
        """
        Get info about a pending timeout

        :param name: Name of the timeout to get
        :type name: str

        :returns: dict

        Example::

            {
                "test_timeout": {
                    "seconds": 10.0,
                    "actions": [
                        {
                            "action": "action_1",
                            "args": {
                                "name_1": "value_1"
                            }
                        }
                    ]
                }
            }

        If no such timeout exist with the specified name then the value of the
        timeout name will be null.
        """

        response = {name: None}

        with self._pending_timeouts_lock:
            timer = self._pending_timeouts.get(name)
            if not timer:
                return response

            return {
                name: {
                    'seconds': timer.interval,
                    'actions': [json.loads(str(a)) for a in timer.args[0].requests],
                }
            }

    @action
    def set_interval(self, seconds, actions, name=None, **args):
        """
        Define a set of actions to run each specified amount of `seconds`.

        :param seconds: Number of seconds between two runs of the interval
            procedure
        :type seconds: float

        :param actions: List of actions to be executed at each interval
        :type actions: list[dict]

        :param name: Set an optional name for this interval. It is advised to
            set a name if you are planning to programmatically cancel the
            interval in your business logic.
        :type name: str

        :param args: Optional arguments/context to pass to the interval function
        """

        with self._interval_hndl_idx_lock:
            self._interval_hndl_idx += 1
            if not name:
                name = self._DEFAULT_INTERVAL_PREFIX + str(self._interval_hndl_idx)

            if name in self._pending_intervals:
                return (None, f"An interval named '{name}' is already running")

        procedure = Procedure.build(name=name, requests=actions, _async=False)
        self._pending_intervals[name] = procedure

        def _proc_wrapper(procedure, seconds, **kwargs):
            while True:
                with self._pending_intervals_lock:
                    if name not in self._pending_intervals:
                        return

                procedure.execute(**kwargs)
                time.sleep(seconds)

        with self._pending_intervals_lock:
            self._pending_intervals[name] = threading.Thread(
                target=_proc_wrapper, args=[procedure, seconds], kwargs=args
            )
        self._pending_intervals[name].start()

    @action
    def clear_interval(self, name):
        """
        Clear a running interval procedure

        :param name: Name of the interval to clear
        :type name: str
        """
        with self._pending_intervals_lock:
            if name not in self._pending_intervals:
                self.logger.debug('%s is not a running interval', name)
                return
            del self._pending_intervals[name]

    @action
    def get_intervals(self):
        """
        Get info about the running intervals

        :returns: dict

        Example::

            {
                "test_interval": {
                    "seconds": 10.0,
                    "actions": [
                        {
                            "action": "action_1",
                            "args": {
                                "name_1": "value_1"
                            }
                        }
                    ]
                }
            }

        """

        response = {}

        for name in self._pending_intervals:
            # pylint: disable=no-member
            response[name] = self.get_interval(name).output.get(name)
        return response

    @action
    def get_interval(self, name):
        """
        Get info about a running interval

        :param name: Name of the interval to get
        :type name: str

        :returns: dict. Example:

        .. code-block:: json

            {
                "test_interval": {
                    "seconds": 10.0,
                    "actions": [
                        {
                            "action": "action_1",
                            "args": {
                                "name_1": "value_1"
                            }
                        }
                    ]
                }
            }

        If no such interval exist with the specified name then the value of the
        timeout name will be null.
        """

        response = {name: None}

        with self._pending_intervals_lock:
            timer = self._pending_intervals.get(name)
            if not timer:
                return response

            return {
                name: {
                    'seconds': timer._args[1],  # pylint: disable=protected-access
                    'actions': [
                        json.loads(str(a))
                        for a in (
                            # pylint: disable=protected-access
                            timer._args[0].requests
                        )
                    ],
                }
            }

    @action
    def search_directory(self, directory, extensions, recursive=False):
        return HttpUtils.search_directory(directory, recursive=recursive, *extensions)

    @action
    def search_web_directory(self, directory, extensions):
        return HttpUtils.search_web_directory(directory, *extensions)

    @action
    def get_enabled_plugins(self) -> dict:
        """
        :return: The list of enabled plugins as a ``name -> configuration`` map.
        """
        if self._plugins:
            return self._plugins

        plugins = {}
        with self._plugins_lock:
            for name in get_enabled_plugins():
                plugins[name] = Config.get(name)

        return plugins

    @action
    def rst_to_html(self, text: str):
        """
        Utility action to convert RST to HTML.

        It is mostly used by the frontend to render the docstring of the
        available plugins and actions.
        """
        try:
            import docutils.core  # type: ignore
        except ImportError:
            self.logger.warning(
                "docutils is not installed. "
                "Please install docutils to convert RST to HTML."
            )
            return text

        return docutils.core.publish_parts(text, writer_name='html')['html_body']


# vim:sw=4:ts=4:et:
