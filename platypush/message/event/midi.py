from abc import ABC
from typing import Any, List, Optional

from platypush.message.event import Event


class MidiEvent(Event, ABC):
    """
    Base class for MIDI events.
    """

    def __init__(self, *args, device: Optional[str], port: Optional[int], **kwargs):
        """
        :param device: The MIDI device name.
        :param port: The MIDI device port number.
        """
        super().__init__(*args, device=device, port=port, **kwargs)


class MidiMessageEvent(MidiEvent):
    """
    Event triggered upon received MIDI message.
    """

    def __init__(self, *args, message: List[int], data: Optional[Any] = None, **kwargs):
        """
        :param message: The received MIDI message.
        :param data: Additional data associated to the event.
        """
        super().__init__(*args, message=message, data=data, **kwargs)


class MidiDeviceConnectedEvent(MidiEvent):
    """
    Event triggered when a MIDI device is connected.
    """


class MidiDeviceDisconnectedEvent(MidiEvent):
    """
    Event triggered when a MIDI device is disconnected.
    """


class MidiDeviceAddedEvent(MidiEvent):
    """
    Event triggered when a MIDI device is added to the list of available devices.
    """


class MidiDeviceRemovedEvent(MidiEvent):
    """
    Event triggered when a MIDI device is removed from the list of available devices.
    """


# vim:sw=4:ts=4:et:
