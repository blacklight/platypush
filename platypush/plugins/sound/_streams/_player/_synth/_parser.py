import math
import re
from typing import Optional, Union


class SoundParser:
    """
    A utility mixin with some methods to parse and convert sound information -
    e.g. MIDI notes from strings, MIDI notes to frequencies, and the other way
    around.
    """

    _DEFAULT_A4_FREQUENCY = 440.0
    _MIDI_NOTE_REGEX = re.compile(r'^([A-G])([#b]?)(-?[0-9]+)$')
    _MID_A_MIDI_NOTE = 69
    _NOTE_OFFSETS = {
        'C': 0,
        'C#': 1,
        'Db': 1,
        'D': 2,
        'D#': 3,
        'Eb': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'Gb': 6,
        'G': 7,
        'G#': 8,
        'Ab': 8,
        'A': 9,
        'A#': 10,
        'Bb': 10,
        'B': 11,
    }

    _ALTERATION_OFFSETS = {
        'b': -1,
        '': 0,
        '#': 1,
    }

    def __init__(self, *_, ref_frequency: float = _DEFAULT_A4_FREQUENCY, **__) -> None:
        self._ref_frequency = ref_frequency

    @staticmethod
    def _get_alteration_offset(alt: str) -> int:
        """
        Calculate the MIDI note offset given by its reported sharp/flat alteration.
        """
        if alt == '#':
            return 1
        if alt == 'b':
            return -1
        return 0

    @classmethod
    def get_midi_note(cls, note: Union[str, int]) -> int:
        """
        Convert a MIDI note given as input (either an integer or a string like
        'C4') to a MIDI note number.

        :raise: ValueError
        """

        if isinstance(note, str):
            note = note[:1].upper() + note[1:]
            m = cls._MIDI_NOTE_REGEX.match(note)
            if not m:
                raise ValueError(f'Invalid MIDI note: {note}')

            base_note, alteration, octave = m.groups()
            octave = int(octave)
            note_offset = cls._NOTE_OFFSETS[base_note] + cls._get_alteration_offset(
                alteration
            )

            octave_offset = (octave + 1) * 12
            note = octave_offset + note_offset

        if isinstance(note, int):
            if not 0 <= note <= 127:
                raise ValueError(f'MIDI note out of range: {note}')
            return note

        raise ValueError(f'Invalid MIDI note: {note}')

    def note_to_freq(
        self, midi_note: Union[int, str], ref_frequency: Optional[float] = None
    ):
        """
        Converts a MIDI note to its frequency in Hz

        :param midi_note: MIDI note to convert
        :param ref_frequency: Reference A4 frequency override (default: 440 Hz).
        """

        note = self.get_midi_note(midi_note)
        return (2.0 ** ((note - self._MID_A_MIDI_NOTE) / 12.0)) * (
            ref_frequency or self._ref_frequency
        )

    def freq_to_note(self, frequency: float, ref_frequency: Optional[float] = None):
        """
        Converts a frequency in Hz to its closest MIDI note

        :param frequency: Frequency in Hz
        :param ref_frequency: Reference A4 frequency override (default: 440 Hz).
        """

        std_freq = ref_frequency or self._ref_frequency
        return int(12.0 * math.log(frequency / std_freq, 2) + self._MID_A_MIDI_NOTE)
