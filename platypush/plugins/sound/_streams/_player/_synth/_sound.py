from enum import Enum
import json
from typing import Final, Optional, Tuple, Union
from typing_extensions import override

import numpy as np
from numpy.typing import NDArray

from ._base import SoundBase


class WaveShape(Enum):
    """
    Supported audio wave shapes.
    """

    SIN = 'sin'
    SQUARE = 'square'
    SAWTOOTH = 'sawtooth'
    TRIANG = 'triang'


class Sound(SoundBase):
    """
    Models a basic synthetic sound that can be played through an audio device
    """

    _DEFAULT_MID_A_FREQUENCY: Final[float] = 440.0

    def __init__(
        self,
        *args,
        midi_note: Optional[Union[str, int]] = None,
        frequency: Optional[float] = None,
        phase: float = 0,
        duration: Optional[float] = None,
        delay: float = 0,
        shape: WaveShape = WaveShape.SIN,
        **kwargs,
    ):
        """
        You can construct a sound either from a MIDI note or a base frequency,
        as well as the shape of the output wave.

        :param midi_note: MIDI note code, see `this chart
            <https://newt.phys.unsw.edu.au/jw/graphics/notes.GIF>`_.
        :param frequency: Sound base frequency in Hz
        :param phase: Wave phase shift as a multiple of pi (default: 0.0)
        :param duration: Note duration in seconds. Default: keep until
            release/pause/stop
        :param delay: Sound delay in seconds, calculated from the moment the
            command execution starts. Default: 0.
        :param shape: Wave shape. Possible values: "``sin``", "``square``",
            "``sawtooth``" or "``triang``" (see :class:`WaveShape`).
            Default: "``sin``"
        """

        super().__init__(*args, **kwargs)
        invalid_request = RuntimeError(
            'Please specify either a MIDI note or a base frequency'
        )

        if midi_note and frequency:
            raise invalid_request

        if midi_note:
            self.midi_note = self.get_midi_note(midi_note)
            self.frequency = self.note_to_freq(midi_note=midi_note)
        elif frequency:
            self.frequency = frequency
            self.midi_note = self.freq_to_note(frequency=frequency)
        else:
            raise invalid_request

        self.phase = phase
        self.duration = duration
        self.delay = delay
        self.shape = WaveShape(shape)

    def _get_left_audio_pad(
        self, sample_rate: float, t_start: float, t_end: float
    ) -> int:
        """
        Get the size of the audio wave left zero-pad given in function of its
        ``delay``, ``sample_rate``, ``t_start`` and ``t_end``.
        """
        return round(max(0, min(t_end, self.delay) - t_start) * sample_rate)

    def _get_right_audio_pad(
        self, sample_rate: float, t_start: float, t_end: float
    ) -> int:
        """
        Get the size of the audio wave right zero-pad given its declared
        ``delay`` in function of ``t_start`` and ``t_end``.
        """
        if not self.duration:
            return 0

        duration = self.delay + self.duration
        if t_end <= duration:
            return 0

        return round((t_end - max(t_start, duration)) * sample_rate)

    def _get_audio_pad(
        self, sample_rate: float, t_start: float, t_end: float
    ) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
        """
        Return the left and right audio pads for a given audio length as a
        ``(left, right)`` tuple of numpy zero-filled arrays.
        """
        return tuple(
            np.zeros([pad_size, 1])
            for pad_size in (
                self._get_left_audio_pad(
                    sample_rate=sample_rate, t_start=t_start, t_end=t_end
                ),
                self._get_right_audio_pad(
                    sample_rate=sample_rate, t_start=t_start, t_end=t_end
                ),
            )
        )

    def _generate_wave(self, x: NDArray[np.floating]):
        """
        Generate a raw audio wave as a numpy array of floating between -1 and 1
        given ``x`` as a set of timestamp samples.
        """
        if self.shape in (WaveShape.SIN, WaveShape.SQUARE):
            wave = np.sin((2 * np.pi * self.frequency * x) + np.pi * self.phase)

            if self.shape == WaveShape.SQUARE:
                wave[wave < 0] = -0.95
                wave[wave >= 0] = 0.95
        elif self.shape in (WaveShape.SAWTOOTH, WaveShape.TRIANG):
            wave = 2 * (self.frequency * x - np.floor(0.5 + self.frequency * x))
            if self.shape == WaveShape.TRIANG:
                wave = 2 * np.abs(wave) - 1
        else:
            raise RuntimeError(
                f'Unsupported wave shape: {self.shape}. '
                f'Supported values: {[s.value for s in WaveShape]}'
            )

        return wave

    @override
    def get_wave(
        self,
        sample_rate: float,
        t_start: float = 0,
        t_end: float = 0,
        **_,
    ) -> NDArray[np.floating]:
        """
        Get the wave binary data associated to this sound

        :param t_start: Start offset for the wave in seconds. Default: 0
        :param t_end: End offset for the wave in seconds. Default: 0
        :param sample_rate: Audio sample rate. Default: 44100 Hz
        :returns: A ``numpy.ndarray[(t_end-t_start)*sample_rate, 1]``
            with the raw float values
        """

        assert self.frequency is not None, 'The sound has no associated base frequency'
        if t_start > t_end:
            return np.array([])

        left_pad, right_pad = self._get_audio_pad(
            sample_rate=sample_rate, t_start=t_start, t_end=t_end
        )
        t_start = min(t_end, t_start + (left_pad.shape[0] / sample_rate))
        t_end = max(t_start, t_end - (right_pad.shape[0] / sample_rate))
        actual_n_samples = abs(round((t_end - t_start) * sample_rate))
        wave_length = max(t_start, self.delay - t_start)

        if self.duration is not None:
            wave_length = min(wave_length, self.duration - self.delay)

        x = np.linspace(
            max(t_start, self.delay - t_start),
            t_end,
            actual_n_samples,
        ).reshape(-1, 1)

        return self.gain * np.array(
            (
                *left_pad,
                *self._generate_wave(x),
                *right_pad,
            )
        )

    def __iter__(self):
        """
        Iterates over the sound's attributes and returns key-value pairs.
        """
        for attr in ['midi_note', 'frequency', 'volume', 'duration', 'ref_frequency']:
            yield attr, getattr(self, attr)

    def __str__(self):
        """
        :return: A JSON-string representation of the sound dictionary.
        """
        return json.dumps(dict(self))

    @classmethod
    def build(cls, *args, **kwargs) -> "Sound":
        """
        Construct a sound object either from a JSON representation or a
        key-value representation
        """

        if args:
            if isinstance(args[0], cls):
                return args[0]
            if isinstance(args[0], str):
                kwargs = json.loads(args[0])
            elif isinstance(args[0], dict):
                kwargs = args[0]

        if kwargs:
            return Sound(**kwargs)

        raise RuntimeError(f'Usage: {__doc__}')
