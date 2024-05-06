import time
import re
from threading import RLock, Timer
from typing import Optional, Sequence, Union

import rtmidi

from platypush.message.event.midi import MidiMessageEvent
from platypush.plugins import RunnablePlugin, action

from ._model import MidiDevice, MidiDeviceType, MidiDevices


class MidiPlugin(RunnablePlugin):
    """
    Virtual MIDI controller plugin. It allows you to send custom MIDI messages
    to any connected MIDI devices and listen for MIDI events.
    """

    _played_notes = set()

    def __init__(
        self,
        device_name: str = 'Platypush MIDI plugin',
        midi_devices: Optional[Sequence[Union[str, int]]] = None,
        poll_interval: Optional[float] = 5.0,
        event_resolution: Optional[float] = None,
        **kwargs,
    ):
        """
        :param device_name: Name of the MIDI device associated to this plugin.
        :param midi_devices: List of MIDI devices to open and monitor for
            events, by name or by port number. If set, and ``poll_interval``
            is set, then the plugin will only listen for events from these
            devices. If not set, and ``poll_interval`` is set, then the plugin
            will listen for events from all available MIDI devices (default).
        :param poll_interval: How often the plugin should scan for new MIDI
            devices. Set this to 0 or null to disable polling.
        :param event_resolution: If set, then the plugin will throttle
            MIDI events to the specified time resolution. If an event is
            triggered within the specified time resolution, then the event will
            be throttled and the last event will be discarded. This is useful
            to avoid sending too many MIDI messages in a short time frame.
            Default: no throttling.
        """
        super().__init__(poll_interval=poll_interval, **kwargs)

        self._devices = MidiDevices()
        self.device_name = device_name
        self._devices_to_monitor = {
            self._to_device_id(dev) for dev in (midi_devices or [])
        }
        self._midi_out = None
        self._midi_in = None
        self._last_midi_event = None
        self._last_event_trigger_time = None
        self._event_timer = None
        self._event_timer_lock = RLock()
        self._event_resolution = event_resolution
        self.logger.info(
            'Initialized MIDI plugin on virtual device %s', self.device_name
        )

    @staticmethod
    def _to_device_id(device: Union[str, int]) -> Union[str, int]:
        try:
            device = int(device)
        except ValueError:
            pass

        return device

    @property
    def midi_in(self) -> rtmidi.MidiIn:  # type: ignore
        if not self._midi_in:
            self._midi_in = rtmidi.MidiIn()  # type: ignore
            self._midi_in.open_port()

        return self._midi_in

    @property
    def midi_out(self) -> rtmidi.MidiOut:  # type: ignore
        if not self._midi_out:
            self._midi_out = rtmidi.MidiOut()  # type: ignore
            self._midi_out.open_port()

        return self._midi_out

    def start_event_timer(self):
        def flush_last_event():
            self._last_event_trigger_time = time.time()

            if not self._last_midi_event:
                return

            self._bus.post(self._last_midi_event)

        with self._event_timer_lock:
            if not self._event_timer:
                self._event_timer = Timer(self._event_resolution or 0, flush_last_event)

                self._event_timer.start()

            return self._event_timer

    def _on_midi_message(self, device: Optional[MidiDevice] = None):
        def callback(message, data):
            # rtmidi will provide a tuple in the format
            # (midi_message, time_since_last_event)
            # delay = message[1]
            message = message[0]
            self._last_midi_event = event = MidiMessageEvent(
                message=message,
                data=data,
                device=device.name if device else None,
                port=device.port if device else None,
            )

            if self._event_resolution and self._last_event_trigger_time:
                event_delta = time.time() - self._last_event_trigger_time
                if event_delta < self._event_resolution:
                    self.start_event_timer()
                    self.logger.debug('Skipping throttled message: %s', message)
                    return

            self._last_event_trigger_time = time.time()
            self._bus.post(event)

        return callback

    @action
    def send_message(
        self, values: Sequence[int], device: Optional[Union[int, str]] = None
    ):
        """
        :param values: Values is expected to be a list containing the MIDI
            command code and the command parameters - `see reference
            <https://ccrma.stanford.edu/~craig/articles/linuxmidi/misc/essenmidi.html>`_.

            Available MIDI commands:

                 * ``0x80``    Note Off
                 * ``0x90``    Note On
                 * ``0xA0``    Aftertouch
                 * ``0xB0``    Continuous controller
                 * ``0xC0``    Patch change
                 * ``0xD0``    Channel Pressure
                 * ``0xE0``    Pitch bend
                 * ``0xF0``    Start of system exclusive message
                 * ``0xF1``    MIDI Time Code Quarter Frame (Sys Common)
                 * ``0xF2``    Song Position Pointer (Sys Common)
                 * ``0xF3``    Song Select
                 * ``0xF6``    Tune Request (Sys Common)
                 * ``0xF7``    End of system exclusive message
                 * ``0xF8``    Timing Clock (Sys Realtime)
                 * ``0xFA``    Start (Sys Realtime)
                 * ``0xFB``    Continue (Sys Realtime)
                 * ``0xFC``    Stop (Sys Realtime)
                 * ``0xFE``    Active Sensing (Sys Realtime)
                 * ``0xFF``    System Reset (Sys Realtime)

        :param device: MIDI port to send the message to, by number or by name.
            If None then the message will be sent to the default port allocated
            for the plugin.
        """
        if isinstance(device, (str, int)):
            if isinstance(device, str):
                dev = self._devices.by_type(MidiDeviceType.OUTPUT).get(device)
            else:
                dev = self._devices.by_port(device)

            assert dev, f'Could not find device by name {device}'
            assert (
                dev.device_type == MidiDeviceType.OUTPUT
            ), f'The device {device} is not an output device'

            midi_out = dev.midi_out
            if not (midi_out and midi_out.is_port_open()):
                dev.open()
        else:
            midi_out = self.midi_out

        assert midi_out and midi_out.is_port_open(), 'No MIDI output port available'
        midi_out.send_message(values)

    @action
    def play(self, note: int, velocity: int, duration: float = 0):
        """
        Play a note with selected velocity and duration.

        :param note: MIDI note in range 0-127 with #60 = C4
        :param velocity: MIDI note velocity in range 0-127
        :param duration: Note duration in seconds. Pass 0 if you don't want the note to get off
        """
        self.send_message([0x90, note, velocity])  # Note on
        self._played_notes.add(note)

        if duration:
            time.sleep(duration)
            self.send_message([0x80, note, 0])  # Note off
            self._played_notes.remove(note)

    @action
    def release(self, note: int):
        """
        Release a played note.

        :param note: MIDI note in range 0-127 with #60 = C4
        """
        self.send_message([0x80, note, 0])  # Note off
        self._played_notes.remove(note)

    @action
    def release_all(self):
        """
        Release all the notes being played.
        """
        played_notes = self._played_notes.copy()
        for note in played_notes:
            self.release(note)

    @action
    def query(self):
        """
        :returns: dict: A list of the available MIDI ports with index and name.
            Format: ``port_index: device_name``.

              .. code-block:: json

                {
                  "in": {
                    0: "Midi Through:Midi Through Port-0 14:0",
                    1: "MPK mini 3:MPK mini 3 MIDI 1 32:0",
                    2: "X-TOUCH MINI:X-TOUCH MINI MIDI 1 36:0",
                    3: "RtMidiOut Client:Platypush MIDI plugin 129:0"
                  },
                  "out": {
                    0: "Midi Through:Midi Through Port-0 14:0",
                    1: "MPK mini 3:MPK mini 3 MIDI 1 32:0",
                    2: "X-TOUCH MINI:X-TOUCH MINI MIDI 1 36:0"
                  }
                }

        """
        in_ports = {int(port): dev for port, dev in enumerate(self.midi_in.get_ports())}
        out_ports = {
            int(port): dev for port, dev in enumerate(self.midi_out.get_ports())
        }

        for device_type, devices in (
            (MidiDeviceType.INPUT, in_ports),
            (MidiDeviceType.OUTPUT, out_ports),
        ):
            for port, name in devices.items():
                dev = MidiDevice(
                    name=name,
                    port=port,
                    device_type=device_type,
                    callback=self._on_midi_message,
                )

                self._devices.add(dev)
                dev = self._devices.by_port(port)
                assert dev, f'Could not find device by port {port}'

                if not self._is_self(dev) and (
                    not self._devices_to_monitor
                    or port in self._devices_to_monitor
                    or name in self._devices_to_monitor
                ):
                    dev.open()

        return {
            'in': in_ports,
            'out': out_ports,
        }

    def _is_self(self, device: MidiDevice):
        return device.name == self.device_name or re.search(
            r'^RtMidi(In|Out) Client:', device.name
        )

    def cleanup(self):
        self.release_all()
        if self._midi_in:
            self._midi_in.close_port()
            self._midi_in = None

        if self._midi_out:
            self._midi_out.close_port()
            self._midi_out = None

        self._devices.close()

    def main(self):
        # Don't run the polling logic if the poll_interval is not set
        if not self.poll_interval:
            self.wait_stop()
            return

        while not self.should_stop():
            self.query()
            self.wait_stop(self.poll_interval)

    def stop(self):
        self.cleanup()
        super().stop()


# vim:sw=4:ts=4:et:
