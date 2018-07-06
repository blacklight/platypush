import rtmidi
import time

from platypush.plugins import Plugin, action


class MidiPlugin(Plugin):
    """
    Virtual MIDI controller plugin. It allows you to send custom MIDI messages
    to any connected devices.

    Requires:

        * **python-rtmidi** (``pip install python-rtmidi``)
    """

    _played_notes = set()

    def __init__(self, device_name='Platypush virtual MIDI output',
                 *args, **kwargs):
        """
        :param device_name: MIDI virtual device name (default: *Platypush virtual MIDI output*)
        :type device_name: str
        """

        super().__init__(*args, **kwargs)

        self.device_name = device_name
        self.midiout = rtmidi.MidiOut()
        available_ports = self.midiout.get_ports()

        if available_ports:
            self.midiout.open_port(0)
            self.logger.info('Initialized MIDI plugin on port 0')
        else:
            self.open_virtual_port(self.device_name)
            self.logger.info('Initialized MIDI plugin on virtual device {}'.
                         format(self.device_name))


    @action
    def send_message(self, values, *args, **kwargs):
        """
        :param values: Values is expected to be a list containing the MIDI command code and the command parameters - see reference at https://ccrma.stanford.edu/~craig/articles/linuxmidi/misc/essenmidi.html
        :type values: list[int]

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

        :param args: Extra args that will be passed to ``rtmidi.send_message``
        :param kwargs: Extra kwargs that will be passed to ``rtmidi.send_message``
        """

        self.midiout.send_message(values, *args, **kwargs)


    @action
    def play_note(self, note, velocity, duration=0):
        """
        Play a note with selected velocity and duration.

        :param note: MIDI note in range 0-127 with #60 = C4
        :type note: int

        :param velocity: MIDI note velocity in range 0-127
        :type velocity: int

        :param duration: Note duration in seconds. Pass 0 if you don't want the note to get off
        :type duration: float
        """

        self.send_message([0x90, note, velocity])  # Note on
        self._played_notes.add(note)

        if duration:
            time.sleep(duration)
            self.send_message([0x80, note, 0])  # Note off
            self._played_notes.remove(note)


    @action
    def release_note(self, note):
        """
        Release a played note.

        :param note: MIDI note in range 0-127 with #60 = C4
        :type note: int
        """

        self.send_message([0x80, note, 0])  # Note off
        self._played_notes.remove(note)


    @action
    def release_all_notes(self):
        """
        Release all the notes being played.
        """

        played_notes = self._played_notes.copy()
        for note in played_notes:
            self.release_note(note)


# vim:sw=4:ts=4:et:

