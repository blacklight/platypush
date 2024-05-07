from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Sequence, Union

import rtmidi

from platypush.context import get_bus
from platypush.message.event.midi import (
    MidiDeviceAddedEvent,
    MidiDeviceConnectedEvent,
    MidiDeviceDisconnectedEvent,
    MidiDeviceRemovedEvent,
)


class MidiDeviceType(Enum):
    """
    Enum for MIDI device types.
    """

    INPUT = 'input'
    OUTPUT = 'output'


@dataclass
class MidiDevice:
    """
    Data class for MIDI devices.
    """

    name: str
    port: int
    device_type: MidiDeviceType
    midi_in: Optional[rtmidi.MidiIn] = None  # type: ignore
    midi_out: Optional[rtmidi.MidiOut] = None  # type: ignore
    callback: Optional[
        Callable[
            [Optional["MidiDevice"]],
            Callable[[Sequence[int], Optional[Any]], Optional[Any]],
        ]
    ] = None

    def open(self):
        """
        Open the MIDI device.
        """
        if self.device_type == MidiDeviceType.INPUT and not self.midi_in:
            get_bus().post(MidiDeviceConnectedEvent(device=self.name, port=self.port))
            self.midi_in = rtmidi.MidiIn()  # type: ignore
            self.midi_in.open_port(self.port)
            if self.callback:
                self.midi_in.set_callback(self.callback(self))
        elif self.device_type == MidiDeviceType.OUTPUT and not self.midi_out:
            self.midi_out = rtmidi.MidiOut()  # type: ignore
            self.midi_out.open_port(self.port)

    def close(self):
        """
        Close the MIDI device.
        """
        if self.midi_in:
            self.midi_in.close_port()
            self.midi_in = None
            get_bus().post(
                MidiDeviceDisconnectedEvent(device=self.name, port=self.port)
            )

        if self.midi_out:
            self.midi_out.close_port()
            self.midi_out = None
            get_bus().post(
                MidiDeviceDisconnectedEvent(device=self.name, port=self.port)
            )

    def is_open(self) -> bool:
        """
        Check if the MIDI device is open.

        :returns: True if the MIDI device is open, False otherwise.
        """
        return (self.midi_in is not None and self.midi_in.is_port_open()) or (
            self.midi_out is not None and self.midi_out.is_port_open()
        )


class MidiDevices:
    """
    Class to manage MIDI devices.
    """

    def __init__(self):
        self._devices_by_port = {}
        self._devices_by_name = {}
        self._devices_by_type = {MidiDeviceType.INPUT: {}, MidiDeviceType.OUTPUT: {}}

    def add(self, device: MidiDevice):
        """
        Add a MIDI device to the list of available devices.

        :param device: The MIDI device to add.
        """
        if (
            device.port not in self._devices_by_port
            or self._devices_by_port[device.port].name != device.name
        ):
            self._devices_by_port[device.port] = device

        if device.name not in self._devices_by_name:
            get_bus().post(MidiDeviceAddedEvent(device=device.name, port=device.port))
            self._devices_by_name[device.name] = device

        if device.port not in self._devices_by_type[device.device_type]:
            self._devices_by_type[device.device_type][device.name] = device

    def remove(self, device: MidiDevice):
        """
        Remove a MIDI device from the list of available devices.

        :param device: The MIDI device to remove.
        """
        device.close()
        del self._devices_by_port[device.port]
        del self._devices_by_name[device.name]
        del self._devices_by_type[device.device_type][device.name]
        get_bus().post(MidiDeviceRemovedEvent(device=device.name, port=device.port))

    def by_port(self, port: int) -> Optional[MidiDevice]:
        """
        Get a MIDI device by port.

        :param port: The port of the MIDI device.
        :returns: The MIDI device if found, None otherwise.
        """
        return self._devices_by_port.get(port)

    def by_name(self, name: str) -> Optional[MidiDevice]:
        """
        Get a MIDI device by name.

        :param name: The name of the MIDI device.
        :returns: The MIDI device if found, None otherwise.
        """
        return self._devices_by_name.get(name)

    def by_type(self, device_type: MidiDeviceType) -> Dict[str, MidiDevice]:
        """
        Get all MIDI devices of a certain type.

        :param device_type: The type of the MIDI devices.
        :returns: A list of MIDI devices of the specified type.
        """
        return self._devices_by_type[device_type]

    def get(self, device: Union[str, int]) -> Optional[MidiDevice]:
        """
        Get a MIDI device by name or port.

        :param device: The name or port of the MIDI device.
        :returns: The MIDI device if found, None otherwise.
        """
        if isinstance(device, str):
            return self.by_name(device)
        if isinstance(device, int):
            return self.by_port(device)
        return None

    def close(self):
        """
        Close and clear all MIDI devices.
        """
        devices = list(self._devices_by_port.values())
        for dev in devices:
            self.remove(dev)

        self._devices_by_port.clear()
        self._devices_by_name.clear()
        self._devices_by_type = {MidiDeviceType.INPUT: {}, MidiDeviceType.OUTPUT: {}}


# vim:sw=4:ts=4:et:
