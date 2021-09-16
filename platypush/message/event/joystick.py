from abc import ABCMeta
from typing import Optional, Iterable, Union

from platypush.message.event import Event


class JoystickEvent(Event):
    """
    Generic joystick event.
    """

    def __init__(self, code, state, *args, **kwargs):
        """
        :param code: Event code, usually the code of the source key/handle
        :type code: str

        :param state: State of the triggering element. Can be 0/1 for a button, -1/0/1 for an axis, a discrete integer
            for an analog input etc.
        :type state: int
        """

        super().__init__(*args, code=code, state=state, **kwargs)


class _JoystickEvent(Event, ABCMeta):
    """
    Base joystick event class.
    """

    def __init__(self, device: str, **kwargs):
        super().__init__(device=device, **kwargs)


class JoystickConnectedEvent(_JoystickEvent):
    """
    Event triggered upon joystick connection.
    """
    def __init__(self,
                 *args,
                 name: Optional[str] = None,
                 axes: Optional[Iterable[Union[int, str]]] = None,
                 buttons: Optional[Iterable[Union[int, str]]] = None,
                 **kwargs):
        """
        :param name: Device name.
        :param axes: List of the device axes, as indices or names.
        :param buttons: List of the device buttons, as indices or names.
        """
        super().__init__(*args, name=name, axes=axes, buttons=buttons, **kwargs)


class JoystickDisconnectedEvent(_JoystickEvent):
    """
    Event triggered upon joystick disconnection.
    """


class JoystickStateEvent(_JoystickEvent):
    """
    Event triggered when the state of the joystick changes.
    """

    def __init__(self, *args, axes: Iterable[int], buttons: Iterable[bool], **kwargs):
        """
        :param axes: Joystick axes values, as a list of integer values.
        :param buttons: Joystick buttons values, as a list of boolean values (True for pressed, False for released).
        """
        super().__init__(*args, axes=axes, buttons=buttons, **kwargs)


class JoystickButtonPressedEvent(_JoystickEvent):
    """
    Event triggered when a joystick button is pressed.
    """

    def __init__(self, *args, button: Union[int, str], **kwargs):
        """
        :param button: Button index or name.
        """
        super().__init__(*args, button=button, **kwargs)


class JoystickButtonReleasedEvent(_JoystickEvent):
    """
    Event triggered when a joystick button is released.
    """

    def __init__(self, *args, button: Union[int, str], **kwargs):
        """
        :param button: Button index or name.
        """
        super().__init__(*args, button=button, **kwargs)


class JoystickAxisEvent(_JoystickEvent):
    """
    Event triggered when an axis value of the joystick changes.
    """

    def __init__(self, *args, axis: Union[int, str], value: int, **kwargs):
        """
        :param axis: Axis index or name.
        :param value: Axis value.
        """
        super().__init__(*args, axis=axis, value=value, **kwargs)


# vim:sw=4:ts=4:et:
