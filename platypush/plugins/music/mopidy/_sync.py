from dataclasses import dataclass, field
from threading import Event, RLock
from typing import Optional


@dataclass
class PlaylistSync:
    """
    Object used to synchronize playlist load/change events between threads.
    """

    _loading_lock: RLock = field(default_factory=RLock)
    _loading: Event = field(default_factory=Event)
    _loaded: Event = field(default_factory=Event)

    def wait_for_loading(self, timeout: Optional[float] = None):
        """
        Wait for the playlist to be loaded.

        :param timeout: The maximum time to wait for the playlist to be loaded.
        """
        # If the loading event is not set, no playlist change - we can proceed
        # with notifying the event.
        if not self._loading.is_set():
            return True

        # Wait for the full playlist to be loaded.
        return self._loaded.wait(timeout)

    def __enter__(self):
        """
        Called when entering a context manager to handle a playlist loading
        session.
        """
        self._loading_lock.acquire()
        self._loading.set()
        self._loaded.clear()

    def __exit__(self, *_):
        """
        Called when exiting a context manager to handle a playlist loading
        session.
        """
        self._loading.clear()
        self._loaded.set()

        try:
            self._loading_lock.release()
        except RuntimeError:
            pass
