from contextlib import contextmanager
import queue
import time

from abc import ABC, abstractmethod
from logging import getLogger
from threading import Event, RLock, Thread
from typing import IO, Generator, Optional, Tuple, Union
from typing_extensions import override

import sounddevice as sd

from .._converter import ConverterProcess
from .._model import AudioState


class AudioThread(Thread, ABC):
    """
    Base class for audio play/record threads.
    """

    _STREAM_NAME_PREFIX = 'platypush-stream-'

    def __init__(
        self,
        plugin,
        device: Union[str, Tuple[str, str]],
        outfile: str,
        output_format: str,
        channels: int,
        sample_rate: int,
        dtype: str,
        stream: bool,
        audio_pass_through: bool,
        duration: Optional[float] = None,
        blocksize: Optional[int] = None,
        latency: Union[float, str] = 'high',
        redis_queue: Optional[str] = None,
        should_stop: Optional[Event] = None,
        **kwargs,
    ):
        from .. import SoundPlugin

        super().__init__(**kwargs)

        self.plugin: SoundPlugin = plugin
        self.device = device
        self.outfile = outfile
        self.output_format = output_format
        self.channels = channels
        self.sample_rate = sample_rate
        self.dtype = dtype
        self.stream = stream
        self.duration = duration
        self.blocksize = blocksize
        self.latency = latency
        self.redis_queue = redis_queue
        self.audio_pass_through = audio_pass_through
        self.logger = getLogger(__name__)

        self._state = AudioState.STOPPED
        self._state_lock = RLock()
        self._started_time: Optional[float] = None
        self._converter: Optional[ConverterProcess] = None
        self._should_stop = should_stop or Event()
        self.paused_changed = Event()

    @property
    def should_stop(self) -> bool:
        """
        Proxy for `._should_stop.is_set()`.
        """
        return self._should_stop.is_set()

    @abstractmethod
    def _audio_callback(self, audio_converter: ConverterProcess):
        """
        Returns a callback to handle the raw frames captures from the audio device.
        """
        raise NotImplementedError()

    @abstractmethod
    def _on_audio_converted(self, data: bytes, out_f: IO):
        """
        This callback will be called when the audio data has been converted.
        """
        raise NotImplementedError()

    def main(
        self,
        converter: ConverterProcess,
        audio_stream: sd.Stream,
        out_stream_index: Optional[int],
        out_f: IO,
    ):
        """
        Main loop.
        """
        self.notify_start()
        if out_stream_index:
            self.plugin.start_playback(
                stream_index=out_stream_index, stream=audio_stream
            )

        self.logger.info(
            'Started %s on device [%s]', self.__class__.__name__, self.device
        )
        self._started_time = time.time()

        while (
            self.state != AudioState.STOPPED
            and not self.should_stop
            and (
                self.duration is None
                or time.time() - self._started_time < self.duration
            )
        ):
            while self.state == AudioState.PAUSED:
                self.paused_changed.wait()

            if self.should_stop:
                break

            timeout = (
                max(
                    0,
                    self.duration - (time.time() - self._started_time),
                )
                if self.duration is not None
                else 1
            )

            data = converter.read(timeout=timeout)
            if not data:
                continue

            self._on_audio_converted(data, out_f)

    @override
    def run(self):
        super().run()
        self.paused_changed.clear()

        try:
            stream_index = (
                self.plugin._allocate_stream_index()  # pylint: disable=protected-access
                if self.audio_pass_through
                else None
            )

            with self.open_converter() as converter, sd.Stream(
                samplerate=self.sample_rate,
                device=self.device,
                channels=self.channels,
                callback=self._audio_callback(converter),
                dtype=self.dtype,
                latency=self.latency,
                blocksize=self.blocksize,
            ) as audio_stream, open(self.outfile, 'wb') as f:
                self.main(
                    out_stream_index=stream_index,
                    converter=converter,
                    audio_stream=audio_stream,
                    out_f=f,
                )
        except queue.Empty:
            self.logger.warning(
                'Audio callback timeout for %s', self.__class__.__name__
            )
        finally:
            self.notify_stop()

    @contextmanager
    def open_converter(self) -> Generator[ConverterProcess, None, None]:
        assert not self._converter, 'A converter process is already running'
        self._converter = ConverterProcess(
            ffmpeg_bin=self.plugin.ffmpeg_bin,
            sample_rate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            chunk_size=self.plugin.input_blocksize,
            output_format=self.output_format,
        )

        self._converter.start()
        yield self._converter

        self._converter.stop()
        self._converter.join(timeout=2)
        self._converter = None

    def notify_start(self):
        self.state = AudioState.RUNNING

    def notify_stop(self):
        self.state = AudioState.STOPPED
        if self._converter:
            self._converter.stop()

    def notify_pause(self):
        states = {
            AudioState.PAUSED: AudioState.RUNNING,
            AudioState.RUNNING: AudioState.PAUSED,
        }

        with self._state_lock:
            new_state = states.get(self.state)
            if new_state:
                self.state = new_state
            else:
                return

        self.logger.info('Paused state toggled for %s', self.__class__.__name__)
        self.paused_changed.set()

    @property
    def state(self):
        with self._state_lock:
            return self._state

    @state.setter
    def state(self, value: AudioState):
        with self._state_lock:
            self._state = value


# vim:sw=4:ts=4:et:
