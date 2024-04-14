import threading
from typing import Callable, Optional, Type


def OrEvent(*events, cls: Type = threading.Event):
    """
    Wrapper for threading.Event that allows to create an event that is
    set if any of the given events are set.

    Adapted from
    https://stackoverflow.com/questions/12317940/python-threading-can-i-sleep-on-two-threading-events-simultaneously#12320352.

    :param events: The events to be checked.
    :param cls: The class to be used for the event. Default: threading.Event.
    """

    or_event = cls()

    def changed():
        bools = [e.is_set() for e in events]
        if any(bools):
            or_event.set()
        else:
            or_event.clear()

    def _to_or(e, changed_callback: Callable[[], None]):
        if not hasattr(e, "_set"):
            e._set = e.set
        if not hasattr(e, "_clear"):
            e._clear = e.clear

        e.changed = changed_callback
        e.set = lambda: _or_set(e)
        e.clear = lambda: _clear_or(e)

    def _clear_or(e):
        e._clear()
        e.changed()

    def _or_set(e):
        try:
            e._set()
            e.changed()
        except RecursionError:
            pass

    for e in events:
        _to_or(e, changed)

    changed()
    return or_event


def wait_for_either(
    *events, timeout: Optional[float] = None, cls: Type = threading.Event
):
    """
    Wait for any of the given events to be set.

    :param events: The events to be checked.
    :param timeout: The maximum time to wait for the event to be set. Default: None.
    :param cls: The class to be used for the event. Default: threading.Event.
    """
    return OrEvent(*events, cls=cls).wait(timeout=timeout)
