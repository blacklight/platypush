from typing import Union

from platypush.message.event import Event


class GPIOEvent(Event):
    """
    Event triggered when the value on a GPIO PIN changes.
    """

    def __init__(self, pin: Union[int, str], value: int, *args, **kwargs):
        """
        :param pin: PIN number or name.
        :param value: Current value of the PIN.
        """
        super().__init__(*args, pin=pin, value=value, **kwargs)

