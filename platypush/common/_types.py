from abc import ABC
from threading import Event, Thread
from typing import Optional


class StoppableThread(Thread, ABC):
    """
    Base interface for stoppable threads.
    """

    def __init__(self, *args, stop_event: Optional[Event] = None, **kwargs):
        """
        :param stop_event: Event used to signal the thread to stop.
        """
        super().__init__(*args, **kwargs)
        self._stop_event = stop_event or Event()

    def should_stop(self) -> bool:
        """
        :return: ``True`` if the thread should be stopped, ``False`` otherwise.
        """
        return self._stop_event.is_set()

    def wait_stop(self, timeout: Optional[float] = None):
        """
        Wait for the stop event to be set.

        :param timeout: Timeout in seconds (default: no timeout).
        """
        self._stop_event.wait(timeout)

    def stop(self):
        """
        Signal the thread to stop by setting the stop event.
        """
        self._stop_event.set()
