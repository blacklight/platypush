"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import enum
import json
import math


class WaveShape(enum.Enum):
    SIN='sin'
    SQUARE='square'
    SAWTOOTH='sawtooth'
    TRIANG='triang'


class Sound(object):
    """
    Models a basic synthetic sound that can be played through an audio device
    """

    STANDARD_A_FREQUENCY = 440.0
    STANDARD_A_MIDI_NOTE = 69
    _DEFAULT_BLOCKSIZE = 1024
    _DEFAULT_SYNTH_BUFSIZE = 2
    _DEFAULT_FILE_BUFSIZE = 20
    _DEFAULT_SAMPLERATE = 44100

    midi_note = None
    frequency = None
    phase = 0.0
    gain = 1.0
    duration = None
    shape = None

    def __init__(self, midi_note=midi_note, frequency=None, phase=phase,
                 gain=gain, duration=duration, shape=WaveShape.SIN,
                 A_frequency=STANDARD_A_FREQUENCY):
        """
        You can construct a sound either from a MIDI note or a base frequency

        :param midi_note: MIDI note code, see
            https://newt.phys.unsw.edu.au/jw/graphics/notes.GIF
        :type midi_note: int

        :param frequency: Sound base frequency in Hz
        :type frequency: float

        :param phase: Wave phase shift as a multiple of pi (default: 0.0)
        :type phase: float

        :param gain: Note gain/volume between 0.0 and 1.0 (default: 1.0)
        :type gain: float

        :param duration: Note duration in seconds. Default: keep until
            release/pause/stop
        :type duration: float

        :param shape: Wave shape. Possible values: "``sin``", "``square``",
            "``sawtooth``" or "``triang``" (see :class:`WaveSound`).
            Default: "``sin``"
        :type shape: str

        :param A_frequency: Reference A4 frequency (default: 440 Hz)
        :type A_frequency: float
        """

        if midi_note and frequency:
            raise RuntimeError('Please specify either a MIDI note or a base ' +
                               'frequency')

        if midi_note:
            self.midi_note = midi_note
            self.frequency = self.note_to_freq(midi_note=midi_note,
                                               A_frequency=A_frequency)
        elif frequency:
            self.frequency = frequency
            self.midi_note = self.freq_to_note(frequency=frequency,
                                               A_frequency=A_frequency)
        else:
            raise RuntimeError('Please specify either a MIDI note or a base ' +
                               'frequency')

        self.phase = phase
        self.gain = gain
        self.duration = duration
        self.shape = WaveShape(shape)

    @classmethod
    def note_to_freq(cls, midi_note, A_frequency=STANDARD_A_FREQUENCY):
        """
        Converts a MIDI note to its frequency in Hz

        :param midi_note: MIDI note to convert
        :type midi_note: int

        :param A_frequency: Reference A4 frequency (default: 440 Hz)
        :type A_frequency: float
        """

        return (2.0 ** ((midi_note - cls.STANDARD_A_MIDI_NOTE) / 12.0)) \
            * A_frequency

    @classmethod
    def freq_to_note(cls, frequency, A_frequency=STANDARD_A_FREQUENCY):
        """
        Converts a frequency in Hz to its closest MIDI note

        :param frequency: Frequency in Hz
        :type midi_note: float

        :param A_frequency: Reference A4 frequency (default: 440 Hz)
        :type A_frequency: float
        """

        # TODO return also the offset in % between the provided frequency
        # and the standard MIDI note frequency
        return int(12.0 * math.log(frequency/A_frequency, 2)
                   + cls.STANDARD_A_MIDI_NOTE)

    def get_wave(self, t_start=0., t_end=0., samplerate=_DEFAULT_SAMPLERATE):
        """
        Get the wave binary data associated to this sound

        :param t_start: Start offset for the wave in seconds. Default: 0
        :type t_start: float

        :param t_end: End offset for the wave in seconds. Default: 0
        :type t_end: float

        :param samplerate: Audio sample rate. Default: 44100 Hz
        :type samplerate: int

        :returns: A ``numpy.ndarray[(t_end-t_start)*samplerate, 1]``
            with the raw float values
        """

        import numpy as np
        x = np.linspace(t_start, t_end, int((t_end-t_start)*samplerate))

        x = x.reshape(len(x), 1)

        if self.shape == WaveShape.SIN or self.shape == WaveShape.SQUARE:
            wave = np.sin((2*np.pi*self.frequency*x) + np.pi*self.phase)

            if self.shape == WaveShape.SQUARE:
                wave[wave < 0] = -1
                wave[wave >= 0] = 1
        elif self.shape == WaveShape.SAWTOOTH or self.shape == WaveShape.TRIANG:
            wave = 2 * (self.frequency*x -
                        np.floor(0.5 + self.frequency*x))
            if self.shape == WaveShape.TRIANG:
                wave = 2 * np.abs(wave) - 1
        else:
            raise RuntimeError('Unsupported wave shape: {}'.format(self.shape))

        return self.gain * wave


    def fft(self, t_start=0., t_end=0., samplerate=_DEFAULT_SAMPLERATE,
            freq_range=None, freq_buckets=None):
        """
        Get the real part of the Fourier transform associated to a time-bounded
            sample of this sound

        :param t_start: Start offset for the wave in seconds. Default: 0
        :type t_start: float

        :param t_end: End offset for the wave in seconds. Default: 0
        :type t_end: float

        :param samplerate: Audio sample rate. Default: 44100 Hz
        :type samplerate: int

        :param freq_range: FFT frequency range. Default: ``(0, samplerate/2)``
            (see `Nyquist-Shannon sampling theorem <https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem>`_)
        :type freq_range: list or tuple with 2 int elements (range)

        :param freq_buckets: Number of buckets to subdivide the frequency range.
            Default: None
        :type freq_buckets: int

        :returns: A numpy.ndarray[freq_range,1] with the raw float values
        """

        import numpy as np

        if not freq_range:
            freq_range = (0, int(samplerate/2))

        wave = self.get_wave(t_start=t_start, t_end=t_end, samplerate=samplerate)
        fft = np.fft.fft(wave.reshape(len(wave)))
        fft = fft.real[freq_range[0]:freq_range[1]]

        if freq_buckets is not None:
            fft = np.histogram(fft, bins=freq_buckets)

        return fft

    def __iter__(self):
        for attr in ['midi_note', 'frequency', 'gain', 'duration']:
            yield (attr, getattr(self, attr))


    def __str__(self):
        return json.dumps(dict(self))


    @classmethod
    def build(cls, *args, **kwargs):
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

        raise RuntimeError('Usage: {}'.format(__doc__))


class Mix(object):
    """
    This class models a set of mixed :class:`Sound` instances that can be played
    through an audio stream to an audio device
    """

    _sounds = None

    def __init__(self, *sounds):
        self._sounds = []

        for sound in sounds:
            self.add(sound)


    def __iter__(self):
        for sound in self._sounds:
            yield dict(sound)


    def __str__(self):
        return json.dumps(list(self))


    def add(self, sound):
        self._sounds.append(Sound.build(sound))


    def remove(self, sound_index):
        if sound_index >= len(self._sounds):
            self.logger.error('No such sound index: {} in mix {}'.format(
                sound_index, list(self)))
            return

        self._sounds.pop(sound_index)


    def get_wave(self, t_start=0., t_end=0., normalize_range=(-1.0, 1.0),
                 on_clip='scale', samplerate=Sound._DEFAULT_SAMPLERATE):
        """
        Get the wave binary data associated to this mix

        :param t_start: Start offset for the wave in seconds. Default: 0
        :type t_start: float

        :param t_end: End offset for the wave in seconds. Default: 0
        :type t_end: float

        :param normalize_range: Normalization range. If set the gain values of the
            wave will be normalized to fit into the specified range if it
            "clips" above or below.  Default: ``(-1.0, 1.0)``
        :type normalize_range: list[float]

        :param on_clip: Action to take on wave clipping if ``normalize_range``
            is set. Possible values: "``scale``" (scale down the frame to remove
            the clipping) or "``clip``" (saturate the values above/below range).
            Default: "``scale``".
        :type on_clip: str

        :param samplerate: Audio sample rate. Default: 44100 Hz
        :type samplerate: int

        :returns: A numpy.ndarray[n,1] with the raw float values
        """

        wave = None

        for sound in self._sounds:
            sound_wave = sound.get_wave(t_start=t_start, t_end=t_end,
                                        samplerate=samplerate)

            if wave is None:
                wave = sound_wave
            else:
                wave += sound_wave

        if normalize_range and len(wave):
            scale_factor = (normalize_range[1]-normalize_range[0]) / \
                (wave.max()-wave.min())

            if scale_factor < 1.0:  # Wave clipping
                if on_clip == 'scale':
                    wave = scale_factor * wave
                elif on_clip == 'clip':
                    wave[wave < normalize_range[0]] = normalize_range[0]
                    wave[wave > normalize_range[1]] = normalize_range[1]
                else:
                    raise RuntimeError('Supported values for "on_clip": ' +
                                       '"scale" or "clip"')

        return wave


    def fft(self, t_start=0., t_end=0., samplerate=Sound._DEFAULT_SAMPLERATE,
            freq_range=None, freq_buckets=None):
        """
        Get the real part of the Fourier transform associated to a time-bounded
            sample of this mix

        :param t_start: Start offset for the wave in seconds. Default: 0
        :type t_start: float

        :param t_end: End offset for the wave in seconds. Default: 0
        :type t_end: float

        :param samplerate: Audio sample rate. Default: 44100 Hz
        :type samplerate: int

        :param freq_range: FFT frequency range. Default: ``(0, samplerate/2)``
            (see `Nyquist-Shannon sampling theorem <https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem>`_)
        :type freq_range: list or tuple with 2 int elements (range)

        :param freq_buckets: Number of buckets to subdivide the frequency range.
            Default: None
        :type freq_buckets: int

        :returns: A numpy.ndarray[freq_range,1] with the raw float values
        """

        import numpy as np

        if not freq_range:
            freq_range = (0, int(samplerate/2))

        wave = self.get_wave(t_start=t_start, t_end=t_end, samplerate=samplerate)
        fft = np.fft.fft(wave.reshape(len(wave)))
        fft = fft.real[freq_range[0]:freq_range[1]]

        if freq_buckets is not None:
            fft = np.histogram(fft, bins=freq_buckets)

        return fft


    def duration(self):
        """
        :returns: The duration of the mix in seconds as duration of its longest
            sample, or None if the mixed sample have no duration set
        """

        duration = 0

        for sound in self._sounds:
            if sound.duration is None:
                return None

            duration = max(duration, sound.duration)

        return duration


# vim:sw=4:ts=4:et:
