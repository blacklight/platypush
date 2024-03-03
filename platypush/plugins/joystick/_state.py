from dataclasses import dataclass
from enum import Enum


class ConnectedState(Enum):
    """
    Enum to represent the connection state of a joystick.
    """

    UNKNOWN = 0
    CONNECTED = 1
    DISCONNECTED = 2


@dataclass
class JoystickState:
    """
    Dataclass that holds the joystick state properties.
    """

    left_joystick_y: float = 0
    left_joystick_x: float = 0
    right_joystick_y: float = 0
    right_joystick_x: float = 0
    left_trigger: float = 0
    right_trigger: float = 0
    left_bumper: int = 0
    right_bumper: int = 0
    a: int = 0
    x: int = 0
    y: int = 0
    b: int = 0
    left_thumb: int = 0
    right_thumb: int = 0
    back: int = 0
    start: int = 0
    left_dir_pad: int = 0
    right_dir_pad: int = 0
    up_dir_pad: int = 0
    down_dir_pad: int = 0


@dataclass
class JoystickDeviceState:
    """
    Dataclass that holds the joystick device state properties.
    """

    device: str
    state: JoystickState
