import logging
import rtmidi
import time

from platypush.message.response import Response
from platypush.plugins import Plugin


class MidiPlugin(Plugin):
    """
    Virtual MIDI controller plugin.
    It requires python-rtmidi - https://pypi.org/project/python-rtmidi/
    """

    _played_notes = set()

    def __init__(self, device_name='Platypush virtual MIDI output',
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.device_name = device_name
        self.midiout = rtmidi.MidiOut()
        available_ports = self.midiout.get_ports()

        if available_ports:
            self.midiout.open_port(0)
            logging.info('Initialized MIDI plugin on port 0')
        else:
            self.open_virtual_port(self.device_name)
            logging.info('Initialized MIDI plugin on virtual device {}'.
                         format(self.device_name))


    def send_message(self, values, *args, **kwargs):
        """
        Values is expected to be a list containing the MIDI command code and
            the command parameters - see reference at
            https://ccrma.stanford.edu/~craig/articles/linuxmidi/misc/essenmidi.html

        Available MIDI commands:
             0x80    Note Off
             0x90    Note On
             0xA0    Aftertouch
             0xB0    Continuous controller
             0xC0    Patch change
             0xD0    Channel Pressure
             0xE0    Pitch bend
             0xF0    Start of system exclusive message
             0xF1    MIDI Time Code Quarter Frame (Sys Common)
             0xF2    Song Position Pointer (Sys Common)
             0xF3    Song Select
             0xF6    Tune Request (Sys Common)
             0xF7    End of system exclusive message
             0xF8    Timing Clock (Sys Realtime)
             0xFA    Start (Sys Realtime)
             0xFB    Continue (Sys Realtime)
             0xFC    Stop (Sys Realtime)
             0xFE    Active Sensing (Sys Realtime)
             0xFF    System Reset (Sys Realtime)
        """

        self.midiout.send_message(values, *args, **kwargs)
        return Response(output={'status':'ok'})


    def play_note(self, note, velocity, duration=0):
        """
        Params:
            - note: MIDI note in range 0-127 with #60 = C4
            - velocity: MIDI note velocity in range 0-127
            - duration: Note duration in (float) seconds. Pass 0 if you don't
              want the note to get off
        """

        self.send_message([0x90, note, velocity])  # Note on
        self._played_notes.add(note)

        if duration:
            time.sleep(duration)
            self.send_message([0x80, note, 0])  # Note off
            self._played_notes.remove(note)


    def release_note(self, note):
        self.send_message([0x80, note, 0])  # Note off
        self._played_notes.remove(note)


    def release_all_notes(self):
        played_notes = self._played_notes.copy()
        for note in played_notes:
            self.release_note(note)

# vim:sw=4:ts=4:et:

