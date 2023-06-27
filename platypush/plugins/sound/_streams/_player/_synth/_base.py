from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from ._parser import SoundParser


class SoundBase(SoundParser, ABC):
    """
    Base class for synthetic sounds and mixes.
    """

    def __init__(self, *args, volume: float = 100, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.volume = volume

    @property
    def gain(self) -> float:
        return self.volume / 100

    @gain.setter
    def gain(self, value: float):
        self.volume = value * 100

    @abstractmethod
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
        raise NotImplementedError()

    def fft(
        self,
        sample_rate: float,
        t_start: float = 0.0,
        t_end: float = 0.0,
        freq_range: Optional[Tuple[float, float]] = None,
        freq_buckets: Optional[int] = None,
    ) -> NDArray[np.floating]:
        """
        Get the real part of the Fourier transform associated to a time-bounded
            sample of this sound.

        :param t_start: Start offset for the wave in seconds. Default: 0
        :param t_end: End offset for the wave in seconds. Default: 0
        :param sample_rate: Audio sample rate. Default: 44100 Hz
        :param freq_range: FFT frequency range. Default: ``(0, sample_rate/2)``
            (see`Nyquist-Shannon sampling theorem
            <https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem>`_)
        :param freq_buckets: Number of buckets to subdivide the frequency range.
            Default: None
        :returns: A numpy.ndarray[freq_range,1] with the raw float values
        """

        if not freq_range:
            freq_range = (0, int(sample_rate / 2))

        wave = self.get_wave(t_start=t_start, t_end=t_end, sample_rate=sample_rate)
        fft = np.fft.fft(wave.reshape(len(wave)))
        fft = fft.real[freq_range[0] : freq_range[1]]

        if freq_buckets is not None:
            fft = np.histogram(fft, bins=freq_buckets)[0]

        return fft
