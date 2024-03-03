from dataclasses import asdict
import multiprocessing
from threading import Timer
from typing import Optional, Type
from time import time

from platypush.context import get_bus
from platypush.message.event.joystick import (
    JoystickConnectedEvent,
    JoystickDisconnectedEvent,
    JoystickEvent,
    JoystickStateEvent,
)
from platypush.schemas.joystick import JoystickDeviceSchema

from ._inputs import GamePad, InputEvent, UnpluggedError
from ._state import ConnectedState, JoystickDeviceState, JoystickState


class JoystickManager(multiprocessing.Process):
    """
    A process that monitors and publishes joystick events.
    """

    MAX_TRIG_VAL = 1 << 8
    MAX_JOY_VAL = 1 << 15
    THROTTLE_INTERVAL = 0.2

    def __init__(
        self,
        device: GamePad,
        poll_interval: Optional[float],
        state_queue: multiprocessing.Queue,
    ):
        super().__init__()
        self.device = device
        self.poll_interval = poll_interval
        self.state = JoystickState()
        self._state_queue = state_queue
        self._connected_state = ConnectedState.UNKNOWN
        self._stop_evt = multiprocessing.Event()
        self._state_throttler: Optional[Timer] = None
        self._state_timestamp: float = 0

    @property
    def should_stop(self):
        return self._stop_evt.is_set()

    def wait_stop(self, timeout: Optional[float] = None):
        self._stop_evt.wait(timeout=timeout or self.poll_interval)

    def _enqueue_state(self):
        now = time()
        self._state_queue.put_nowait(
            JoystickDeviceState(
                device=self.device.get_char_device_path(), state=self.state
            )
        )

        if now - self._state_timestamp >= self.THROTTLE_INTERVAL:
            self._post_state()
            self._state_timestamp = now
            return

        self._state_timestamp = now
        self._state_throttler = Timer(self.THROTTLE_INTERVAL, self._post_state)
        self._state_throttler.start()

    def _stop_state_throrttler(self):
        if self._state_throttler:
            self._state_throttler.cancel()
            self._state_throttler = None

    def _post_state(self):
        self._post_event(JoystickStateEvent, state=asdict(self.state))
        self._stop_state_throrttler()

    def _parse_event(self, event: InputEvent):  # pylint: disable=too-many-branches
        """
        Solution adapted from https://stackoverflow.com/questions/46506850.
        """
        if event.code == "ABS_Y":
            # normalize between -1 and 1
            self.state.left_joystick_y = event.state / self.MAX_JOY_VAL
        elif event.code == "ABS_X":
            # normalize between -1 and 1
            self.state.left_joystick_x = event.state / self.MAX_JOY_VAL
        elif event.code == "ABS_RY":
            # normalize between -1 and 1
            self.state.right_joystick_y = event.state / self.MAX_JOY_VAL
        elif event.code == "ABS_RX":
            # normalize between -1 and 1
            self.state.right_joystick_x = event.state / self.MAX_JOY_VAL
        elif event.code == "ABS_Z":
            # normalize between 0 and 1
            self.state.left_trigger = event.state / self.MAX_TRIG_VAL
        elif event.code == "ABS_RZ":
            # normalize between 0 and 1
            self.state.right_trigger = event.state / self.MAX_TRIG_VAL
        elif event.code == "BTN_TL":
            self.state.left_bumper = event.state
        elif event.code == "BTN_TR":
            self.state.right_bumper = event.state
        elif event.code == "BTN_SOUTH":
            self.state.a = event.state
        elif event.code == "BTN_NORTH":
            # previously switched with X
            self.state.y = event.state
        elif event.code == "BTN_WEST":
            # previously switched with Y
            self.state.x = event.state
        elif event.code == "BTN_EAST":
            self.state.b = event.state
        elif event.code == "BTN_THUMBL":
            self.state.left_thumb = event.state
        elif event.code == "BTN_THUMBR":
            self.state.right_thumb = event.state
        elif event.code == "BTN_SELECT":
            self.state.back = event.state
        elif event.code == "BTN_START":
            self.state.start = event.state
        elif event.code == "BTN_TRIGGER_HAPPY1":
            self.state.left_dir_pad = event.state
        elif event.code == "BTN_TRIGGER_HAPPY2":
            self.state.right_dir_pad = event.state
        elif event.code == "BTN_TRIGGER_HAPPY3":
            self.state.up_dir_pad = event.state
        elif event.code == "BTN_TRIGGER_HAPPY4":
            self.state.down_dir_pad = event.state

    def _post_event(
        self, type: Type[JoystickEvent], **kwargs  # pylint: disable=redefined-builtin
    ):
        get_bus().post(
            type(device=dict(JoystickDeviceSchema().dump(self.device)), **kwargs)
        )

    def _on_connect(self):
        if self._connected_state != ConnectedState.CONNECTED:
            self._connected_state = ConnectedState.CONNECTED
            self._post_event(JoystickConnectedEvent)

    def _on_disconnect(self):
        if self._connected_state != ConnectedState.DISCONNECTED:
            self._connected_state = ConnectedState.DISCONNECTED
            self._post_event(JoystickDisconnectedEvent)

    def _loop(self):
        try:
            for event in self.device.read():
                self._on_connect()
                prev_state = asdict(self.state)
                self._parse_event(event)
                new_state = asdict(self.state)

                if prev_state != new_state:
                    self._enqueue_state()
        except (UnpluggedError, OSError):
            self._on_disconnect()
        finally:
            self.wait_stop(self.poll_interval)

    def run(self):
        try:
            while not self.should_stop:
                try:
                    self._loop()
                except KeyboardInterrupt:
                    break
        finally:
            self._on_disconnect()

    def stop(self):
        self._stop_evt.set()
        self._stop_state_throrttler()
