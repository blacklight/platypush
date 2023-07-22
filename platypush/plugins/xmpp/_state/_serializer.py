from dataclasses import asdict
import json
from logging import getLogger
import pathlib
from threading import Event, RLock, Timer
from typing import Final, Optional

from .._mixins import XmppConfigMixin
from ._model import SerializedState, XmppState


class StateSerializer(XmppConfigMixin):
    """
    Serializes to file the state of the client upon new events through a
    timer-based mechanism.
    """

    _DEFAULT_FLUSH_TIMEOUT: Final[float] = 2
    _EMPTY_STATE: Final[SerializedState] = SerializedState()

    def __init__(self, *args, flush_timeout: float = _DEFAULT_FLUSH_TIMEOUT, **kwargs):
        """
        :param flush_timeout: How long the scheduler should wait before
            flushing the state.
        """
        super().__init__(*args, **kwargs)
        self.flush_timeout = flush_timeout
        self._timer: Optional[Timer] = None
        self._state_lock: Final[RLock] = RLock()
        self._state: Optional[XmppState] = None
        self._flush_scheduled: Final[Event] = Event()
        self.logger = getLogger(__name__)

    def _writer_inner(self, filename: str):
        if not self._state:
            return

        self.logger.debug("Serializing state to file: %s", filename)
        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as f:
            json.dump(asdict(self._state.serialize()), f)

    def _writer(self):
        """
        Write the current state to the file.
        """

        state_file = self._config.state_file
        if not state_file:
            return

        with self._state_lock:
            try:
                self._writer_inner(state_file)
            finally:
                self._reset()

    def _reset(self):
        """
        Reset the timer state after normal termination, error or cancellation.
        """
        self._flush_scheduled.clear()
        self._timer = None

    def load(self) -> SerializedState:
        """
        :return: The previous state read from the configured state file.
        """
        state_file = self._config.state_file
        if not (state_file and self._config.restore_state):
            return self._EMPTY_STATE

        try:
            with open(state_file, "r") as f:
                return SerializedState.load(json.load(f))
        except FileNotFoundError:
            self.logger.info("No previous state file found at %s", state_file)
            return self._EMPTY_STATE
        except ValueError:
            self.logger.warning(
                "Invalid or corrupt state file found at %s, it will be reset",
                state_file,
            )
            return self._EMPTY_STATE

    def enqueue(self, state: XmppState):
        """
        Schedule an update of the stored state.
        """
        with self._state_lock:
            self._state = state

            if not self.is_pending():
                self.logger.debug(
                    "Serialization writer scheduled in %f seconds", self.flush_timeout
                )
                self._timer = Timer(self.flush_timeout, self._writer)
                self._timer.name = "xmpp:StateSerializer"
                self._timer.start()

            self._flush_scheduled.set()

    def flush(self):
        """
        Flush the state immediately, without waiting for the next schedule.
        """
        with self._state_lock:
            self._writer()

    def is_pending(self) -> bool:
        """
        :return: ``True`` if there is a pending serialization task, ``False``
            otherwise.
        """
        return self._timer is not None and self._flush_scheduled.is_set()

    def wait(self, timeout: Optional[float] = None):
        """
        If a serialization task is pending or running, wait for it to terminate.
        """
        if self._timer and self.is_pending():
            self._timer.join(timeout)

            with self._state_lock:
                if self._timer and self.is_pending():
                    self.logger.warning(
                        "The state serialization task did not terminate in time"
                    )

                    self.cancel()

    def cancel(self):
        """
        Cancel the timer, if it is running.
        """
        if self._timer:
            self._timer.cancel()

        self._reset()
