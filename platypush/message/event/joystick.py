from abc import ABC

from platypush.message.event import Event


class JoystickEvent(Event, ABC):
    """
    Base joystick event class.
    """

    def __init__(self, device: dict, *args, **kwargs):
        """
        :param device: Joystick device info as a dictionary:

            .. schema:: joystick.JoystickDeviceSchema
        """
        super().__init__(*args, device=device, **kwargs)


class JoystickConnectedEvent(JoystickEvent):
    """
    Event triggered upon joystick connection.
    """


class JoystickDisconnectedEvent(JoystickEvent):
    """
    Event triggered upon joystick disconnection.
    """


class JoystickStateEvent(JoystickEvent):
    """
    Base joystick state event class.
    """

    def __init__(self, *args, state: dict, **kwargs):
        """
        :param state: Joystick state as a dictionary:

            .. schema:: joystick.JoystickStateSchema
        """
        super().__init__(*args, state=state, **kwargs)


# vim:sw=4:ts=4:et:
