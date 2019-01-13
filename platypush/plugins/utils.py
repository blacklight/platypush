import threading
import time

from platypush.plugins import Plugin, action
from platypush.procedure import Procedure


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

    _pending_intervals = {}
    _pending_intervals_lock = threading.RLock()

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
                return (None,
                        "A timeout named '{}' is already awaiting".format(name))


        procedure = Procedure.build(name=name, requests=actions, _async=False)
        self._pending_timeouts[name] = procedure

        def _proc_wrapper(**kwargs):
            procedure.execute(**kwargs)

        with self._pending_timeouts_lock:
            self._pending_timeouts[name] = threading.Timer(seconds,
                                                           _proc_wrapper,
                                                           kwargs=args)
        self._pending_timeouts[name].start()

    @action
    def clear_timeout(self, name):
        timer = None

        with self._pending_timeouts_lock:
            if name not in self._pending_timeouts:
                return
            timer = self._pending_timeouts.pop(name)

        timer.cancel()


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
                name = self._DEFAULT_INTERVAL_PREFIX + \
                    str(self._interval_hndl_idx)

            if name in self._pending_intervals:
                return (None,
                        "An interval named '{}' is already running".format(name))


        procedure = Procedure.build(name=name, requests=actions, _async=False)
        self._pending_intervals[name] = procedure

        def _proc_wrapper(**kwargs):
            while True:
                with self._pending_intervals_lock:
                    if name not in self._pending_intervals:
                        return

                procedure.execute(**kwargs)
                time.sleep(seconds)

        with self._pending_intervals_lock:
            self._pending_intervals[name] = threading.Thread(
                target=_proc_wrapper, kwargs=args)
        self._pending_intervals[name].start()

    @action
    def clear_interval(self, name):
        interval = None

        with self._pending_intervals_lock:
            if name not in self._pending_intervals:
                return
            del self._pending_intervals[name]


# vim:sw=4:ts=4:et:
