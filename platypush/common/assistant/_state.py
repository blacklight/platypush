from collections import namedtuple
from dataclasses import dataclass, field
from threading import Event, RLock
from typing import Optional

AudioFrame = namedtuple('AudioFrame', ['data', 'timestamp'])


@dataclass
class PauseState:
    """
    Data class to hold the boilerplate (state + synchronization events) for the
    audio recorder pause API.
    """

    _paused_event: Event = field(default_factory=Event)
    _recording_event: Event = field(default_factory=Event)
    _state_lock: RLock = field(default_factory=RLock)

    @property
    def paused(self):
        with self._state_lock:
            return self._paused_event.is_set()

    def pause(self):
        """
        Pause the audio recorder.
        """
        with self._state_lock:
            self._paused_event.set()
            self._recording_event.clear()

    def resume(self):
        """
        Resume the audio recorder.
        """
        with self._state_lock:
            self._paused_event.clear()
            self._recording_event.set()

    def toggle(self):
        """
        Toggle the audio recorder pause state.
        """
        with self._state_lock:
            if self.paused:
                self.resume()
            else:
                self.pause()

    def wait_paused(self, timeout: Optional[float] = None):
        """
        Wait until the audio recorder is paused.
        """
        self._paused_event.wait(timeout=timeout)

    def wait_recording(self, timeout: Optional[float] = None):
        """
        Wait until the audio recorder is resumed.
        """
        self._recording_event.wait(timeout=timeout)
