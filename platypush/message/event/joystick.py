from platypush.message.event import Event


class JoystickEvent(Event):
    """
    Event triggered upon joystick event
    """

    def __init__(self, code, state, *args, **kwargs):
        """
        :param code: Event code, usually the code of the source key/handle
        :type code: str

        :param state: State of the triggering element. Can be 0/1 for a button, -1/0/1 for an axis, a discrete integer for an analog input etc.
        :type state: int
        """

        super().__init__(*args, code=code, state=state, **kwargs)


# vim:sw=4:ts=4:et:

