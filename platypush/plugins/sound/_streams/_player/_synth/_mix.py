import json
import logging
from typing import List, Tuple, Union
from typing_extensions import override

import numpy as np
from numpy.typing import DTypeLike, NDArray

from ...._utils import convert_nd_array
from ._base import SoundBase
from ._sound import Sound


class Mix(SoundBase):
    """
    This class models a set of mixed :class:`._sound.Sound` instances that can be played
    through an audio stream to an audio device
    """

    def __init__(self, *sounds, channels: int, dtype: DTypeLike, **kwargs):
        super().__init__(**kwargs)
        self._sounds: List[Sound] = []
        self.logger = logging.getLogger(__name__)
        self.channels = channels
        self.dtype = np.dtype(dtype)

        for sound in sounds:
            self.add(sound)

    def __iter__(self):
        """
        Iterate over the object's attributes and return key-pair values.
        """
        for sound in self._sounds:
            yield dict(sound)

    def __str__(self):
        """
        Return a JSON string representation of the object.
        """
        return json.dumps(list(self))

    def add(self, *sounds: Union[Sound, dict]):
        """
        Add one or more sounds to the mix.
        """
        self._sounds += [Sound.build(sound) for sound in sounds]

    def remove(self, *sound_indices: int):
        """
        Remove one or more sounds from the mix.
        """
        assert self._sounds and all(
            0 <= sound_index < len(sound_indices) for sound_index in sound_indices
        ), f'Sound indices must be between 0 and {len(self._sounds) - 1}'

        for sound_index in sound_indices[::-1]:
            self._sounds.pop(sound_index)

    @override
    def get_wave(
        self,
        sample_rate: float,
        t_start: float = 0,
        t_end: float = 0,
        normalize_range: Tuple[float, float] = (-1.0, 1.0),
        on_clip: str = 'scale',
        **_,
    ) -> NDArray[np.number]:
        wave = None

        for sound in self._sounds:
            sound_wave = sound.get_wave(
                t_start=t_start, t_end=t_end, sample_rate=sample_rate
            )

            if wave is None:
                wave = sound_wave
            else:
                wave += sound_wave

        if wave is not None and len(wave):
            scale_factor = (normalize_range[1] - normalize_range[0]) / (
                wave.max() - wave.min()
            )

            if scale_factor < 1.0:  # Wave clipping
                if on_clip == 'scale':
                    wave = scale_factor * wave
                elif on_clip == 'clip':
                    wave[wave < normalize_range[0]] = normalize_range[0]
                    wave[wave > normalize_range[1]] = normalize_range[1]
                else:
                    raise RuntimeError(
                        'Supported values for "on_clip": ' + '"scale" or "clip"'
                    )

        assert wave is not None
        return convert_nd_array(self.gain * wave, dtype=self.dtype)

    def duration(self):
        """
        :returns: The duration of the mix in seconds as duration of its longest
            sample, or None if the mixed sample have no duration set
        """

        # If any sound has no duration specified, then the resulting mix will
        # have no duration as well.
        if any(sound.duration is None for sound in self._sounds):
            return None

        return max(((sound.duration or 0) + sound.delay for sound in self._sounds))


# vim:sw=4:ts=4:et:
