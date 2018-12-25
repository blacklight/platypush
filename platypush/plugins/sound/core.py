"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import json
import math


class Sound(object):
    """
    Models a basic synthetic sound that can be played through an audio device
    """

    STANDARD_A_FREQUENCY = 440.0
    STANDARD_A_MIDI_NOTE = 69
    _DEFAULT_BLOCKSIZE = 2048
    _DEFAULT_BUFSIZE = 20
    _DEFAULT_SAMPLERATE = 44100

    midi_note = None
    frequency = None
    phase = 0.0
    gain = 1.0
    duration = None

    def __init__(self, midi_note=midi_note, frequency=None, phase=phase,
                 gain=gain, duration=duration, A_frequency=STANDARD_A_FREQUENCY):
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

        :returns: A numpy.ndarray[n,1] with the raw float values
        """

        import numpy as np
        x = np.linspace(t_start, t_end, int((t_end-t_start)*samplerate))

        x = x.reshape(len(x), 1)
        return self.gain * np.sin((2*np.pi*self.frequency*x) + np.pi*self.phase)


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

    _sounds = []

    def __init__(self, *sounds):
        for sound in sounds:
            self.add(sound)


    def __iter__(self):
        for sound in self._sounds:
            yield dict(sound)


    def __str__(self):
        return json.dumps(list(self))


    def add(self, sound):
        self._sounds.append(Sound.build(sound))


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

        if normalize_range:
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


# vim:sw=4:ts=4:et:
