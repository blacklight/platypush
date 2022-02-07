from typing import Optional, Iterable, Any

from platypush.message.event import Event


class DbusSignalEvent(Event):
    """
    Event triggered when a signal is received on the D-Bus.
    """
    def __init__(
        self, bus: str, interface: str, sender: str, path: str, signal: str,
        params: Optional[Iterable[Any]] = None, **kwargs
    ):
        """
        :param bus: Bus type (``session`` or ``system``).
        :param interface: Name of the interface associated to the signal.
        :param sender: D-Bus name of the sender of the signal.
        :param path: Path of the object associated to the signal.
        :param signal: Signal name.
        :param params: Signal payload.
        """
        super().__init__(bus=bus, interface=interface, sender=sender,
                         path=path, signal=signal, params=params, **kwargs)
