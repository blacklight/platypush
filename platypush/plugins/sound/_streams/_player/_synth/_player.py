from contextlib import contextmanager
from queue import Queue
from threading import Event
from typing import Any, Generator, Iterable, Optional, Type
from typing_extensions import override

import numpy as np
import sounddevice as sd
from numpy.typing import DTypeLike, NDArray

from ...._model import AudioState
from ..._player import AudioPlayer
from ._generator import AudioGenerator
from ._mix import Mix
from ._output import AudioOutputCallback
from ._sound import Sound


class AudioSynthPlayer(AudioPlayer):
    """
    The ``AudioSynthPlayer`` can play synthetic sounds (specified either by MIDI
    note or raw frequency) to an audio device.
    """

    def __init__(
        self,
        *args,
        volume: float,
        channels: int,
        dtype: DTypeLike,
        sounds: Optional[Iterable[Sound]] = None,
        **kwargs
    ):
        sounds = sounds or []
        self.mix = Mix(*sounds, volume=volume, channels=channels, dtype=dtype)

        super().__init__(*args, volume=volume, channels=channels, dtype=dtype, **kwargs)
        self._generator_stopped = Event()
        self._completed_callback_event = Event()
        self._audio_queue: Queue[NDArray[np.number]] = Queue(
            maxsize=self.queue_size or 0
        )

    @property
    @override
    def _stream_type(self) -> Type[sd.OutputStream]:
        return sd.OutputStream

    @property
    @override
    def _audio_converter_type(self) -> None:
        pass

    def __setattr__(self, __name: str, __value: Any):
        """
        Make sure that the relevant attributes are synchronized to the mix
        object upon set/update.
        """
        if __name == 'volume':
            # Propagate the volume changes to the mix object.
            self.mix.volume = __value
        return super().__setattr__(__name, __value)

    @override
    def _on_converter_timeout(self, *_, **__) -> bool:
        """
        Don't break the audio stream if the output converter failed
        """
        return True

    @property
    @override
    def _stream_args(self) -> dict:
        """
        Register an :class:`.AudioOutputCallback` to fill up the audio buffers.
        """
        return {
            'callback': AudioOutputCallback(
                audio_queue=self._audio_queue,
                channels=self.channels,
                blocksize=self.blocksize,
                queue_timeout=self._queue_timeout,
                should_stop=lambda: self.should_stop
                or self._generator_stopped.is_set(),
                is_paused=lambda: self.state == AudioState.PAUSED,
            ),
            'finished_callback': self._completed_callback_event.set,
            **super()._stream_args,
        }

    @property
    def _queue_timeout(self) -> float:
        """
        Estimated max read/write timeout on the audio queue.
        """
        return self.blocksize * (self.queue_size or 5) / self.sample_rate

    @override
    @contextmanager
    def _audio_generator(self) -> Generator[AudioGenerator, None, None]:
        stop_generator = Event()
        gen = AudioGenerator(
            audio_queue=self._audio_queue,
            mix=self.mix,
            blocksize=self.blocksize,
            sample_rate=self.sample_rate,
            queue_timeout=self._queue_timeout,
            should_stop=lambda: self.should_stop or stop_generator.is_set(),
            wait_running=self._wait_running,
            on_stop=self._on_stop,
        )

        self._generator_stopped.clear()
        gen.start()
        yield gen

        stop_generator.set()
        gen.join()

    def _on_stop(self):
        self._generator_stopped.set()
        self.notify_stop()


# vim:sw=4:ts=4:et:
