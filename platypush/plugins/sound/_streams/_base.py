from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from logging import getLogger
import os
import queue
from threading import Event, RLock, Thread
import time
from typing import IO, Callable, Final, Generator, Optional, Tuple, Type, Union
from typing_extensions import override

import sounddevice as sd

from platypush.context import get_bus
from platypush.message.event.sound import SoundEvent
from platypush.utils import get_redis

from .._converters import AudioConverter
from .._model import AudioState, StreamType

_StreamType = Union[sd.Stream, sd.OutputStream]


class AudioThread(Thread, ABC):
    """
    Base class for audio play/record stream threads.
    """

    _DEFAULT_FILE: Final[str] = os.devnull
    """Unless otherwise specified, the audio streams will be sent to /dev/null"""
    _DEFAULT_CONVERTER_TIMEOUT: Final[float] = 1

    def __init__(
        self,
        device: Union[str, Tuple[str, str]],
        channels: int,
        volume: float,
        sample_rate: int,
        dtype: str,
        blocksize: int,
        ffmpeg_bin: str = 'ffmpeg',
        stream: bool = False,
        audio_pass_through: bool = False,
        infile: Optional[str] = None,
        outfile: Optional[str] = None,
        duration: Optional[float] = None,
        latency: Union[float, str] = 'high',
        redis_queue: Optional[str] = None,
        should_stop: Optional[Event] = None,
        converter_timeout: Optional[float] = None,
        stream_name: Optional[str] = None,
        queue_size: Optional[int] = None,
        **kwargs,
    ):
        """
        :param device: Audio device to use.
        :param channels: Number of channels to use.
        :param volume: Input/output volume, between 0 and 100.
        :param sample_rate: Sample rate to use.
        :param dtype: Data type to use.
        :param blocksize: Block size to use.
        :param ffmpeg_bin: Path to the ffmpeg binary.
        :param stream: Whether to stream the audio to Redis consumers.
        :param audio_pass_through: Whether to pass the audio through to the
            application's output stream.
        :param infile: Path to the input file or URL, if this is an output
            stream.
        :param outfile: Path to the output file.
        :param duration: Duration of the audio stream.
        :param latency: Latency to use.
        :param redis_queue: Redis queue to use.
        :param should_stop: Synchronize with upstream stop events.
        :param converter_timeout: How long to wait for the converter to finish.
        :param stream_name: Name of the stream.
        :param queue_size: Maximum size of the audio queue.
        """
        super().__init__(**kwargs)

        self.device = device
        self.outfile = os.path.expanduser(outfile or self._DEFAULT_FILE)
        self.infile = os.path.expanduser(infile or self._DEFAULT_FILE)
        self.ffmpeg_bin = ffmpeg_bin
        self.channels = channels
        self.volume = volume
        self.sample_rate = sample_rate
        self.dtype = dtype
        self.stream = stream
        self.duration = duration
        self.blocksize = blocksize * channels
        self.latency = latency
        self._redis_queue = redis_queue
        self.audio_pass_through = audio_pass_through
        self.queue_size = queue_size
        self._stream_name = stream_name
        self.logger = getLogger(__name__)

        self._state = AudioState.STOPPED
        self._state_lock = RLock()
        self._started_time: Optional[float] = None
        self._converter: Optional[AudioConverter] = None
        self._should_stop = should_stop or Event()
        self._converter_timeout = converter_timeout or self._DEFAULT_CONVERTER_TIMEOUT
        self.audio_stream: Optional[_StreamType] = None
        self.stream_index: Optional[int] = None
        self.paused_changed = Event()
        self._converter_terminated = Event()

    @property
    def should_stop(self) -> bool:
        """
        Proxy for `._should_stop.is_set()`.
        """
        return self._should_stop.is_set() or bool(
            self.state == AudioState.STOPPED and self._started_time
        )

    @property
    def gain(self) -> float:
        return self.volume / 100

    def wait_stop(self, timeout: Optional[float] = None):
        """
        Wait for the stop signal to be received.
        """
        return self._should_stop.wait(timeout=timeout)

    def _audio_callback(self) -> Callable:
        """
        Returns a callback to handle the raw frames captures from the audio device.
        """

        def empty_callback(*_, **__):
            pass

        return empty_callback

    @property
    def stream_name(self) -> str:
        if self._stream_name:
            return self._stream_name

        ret = f'platypush:audio:{self.direction.value}'
        if self.stream_index is not None:
            ret += f':{self.stream_index}'
        return ret

    @stream_name.setter
    def stream_name(self, value: Optional[str]):
        self._stream_name = value

    @property
    @abstractmethod
    def direction(self) -> StreamType:
        """
        The default direction for this stream - input or output.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def _audio_converter_type(self) -> Optional[Type[AudioConverter]]:
        """
        This property indicates the type that should be used for the audio
        converter.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def _started_event_type(self) -> Type[SoundEvent]:
        """
        Event type that will be emitted when the audio starts.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def _stopped_event_type(self) -> Type[SoundEvent]:
        """
        Event type that will be emitted when the audio stops.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def _paused_event_type(self) -> Type[SoundEvent]:
        """
        Event type that will be emitted when the audio is paused.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def _resumed_event_type(self) -> Type[SoundEvent]:
        """
        Event type that will be emitted when the audio is resumed.
        """
        raise NotImplementedError()

    @property
    def _stream_type(self) -> Union[Type[sd.Stream], Type[sd.OutputStream]]:
        """
        The type of stream this thread is mapped to.
        """
        return sd.Stream

    @property
    def _converter_args(self) -> dict:
        """
        Extra arguments to pass to the audio converter.
        """
        return {}

    @property
    def _stream_args(self) -> dict:
        """
        Extra arguments to pass to the stream constructor.
        """
        return {}

    @property
    def redis_queue(self) -> str:
        """
        Redis queue for audio streaming.
        """
        if self._redis_queue:
            return self._redis_queue

        dev = (
            self.device
            if isinstance(self.device, (str, int))
            else '-'.join(map(str, self.device))
        )

        name = f'platypush-audio-stream-{self.__class__.__name__}-{dev}'
        if self.stream_index is not None:
            name = f'{name}-{self.stream_index}'

        return name

    def _on_audio_converted(self, data: bytes, out_f: Optional[IO] = None):
        """
        This callback will be called when the audio data has been converted.
        """
        if out_f:
            out_f.write(data)

        if self.stream:
            get_redis().publish(self.redis_queue, data)

    def _wait_running(self):
        """
        If the stream is in paused state, wait for the state to change.
        """
        while self.state == AudioState.PAUSED:
            self.paused_changed.wait()

    def main(
        self,
        converter: Optional[AudioConverter] = None,
        out_f: Optional[IO] = None,
    ):
        """
        Main loop.
        """
        self.notify_start()

        self.logger.info(
            'Started %s on device [%s]', self.__class__.__name__, self.device
        )
        self._started_time = time.time()

        while not self.should_stop and (
            self.duration is None or time.time() - self._started_time < self.duration
        ):
            self._wait_running()
            if not converter:
                self.wait_stop(0.1)
                continue

            if self.should_stop:
                break

            timeout = (
                max(
                    0,
                    min(
                        self.duration - (time.time() - self._started_time),
                        self._converter_timeout,
                    ),
                )
                if self.duration is not None
                else self._converter_timeout
            )

            should_continue = self._process_converted_audio(
                converter, timeout=timeout, out_f=out_f
            )

            if not should_continue:
                break

    def _process_converted_audio(
        self, converter: AudioConverter, timeout: float, out_f: Optional[IO]
    ) -> bool:
        """
        It reads the converted audio from the converter and passes it downstream.

        :return: True if the process should continue, False if it should terminate.
        """
        data = converter.read(timeout=timeout)
        if not data:
            return self._on_converter_timeout(converter)

        self._on_audio_converted(data, out_f)
        return True

    def _on_converter_timeout(self, converter: AudioConverter) -> bool:
        """
        Callback logic invoked if the converter times out.

        :return: ``True`` (default) if the thread is supposed to continue,
            ``False`` if it should terminate.
        """
        self.logger.debug('Timeout on converter %s', converter.__class__.__name__)
        # Continue only if the converter hasn't terminated
        return not self._converter_terminated.is_set()

    @override
    def run(self):
        """
        Wrapper for the main loop that initializes the converter and the stream.
        """
        super().run()
        self.paused_changed.clear()

        try:
            with self.open_converter() as converter, self._stream_type(
                samplerate=self.sample_rate,
                device=self.device,
                channels=self.channels,
                dtype=self.dtype,
                latency=self.latency,
                blocksize=self.blocksize,
                **self._stream_args,
            ) as self.audio_stream, open(
                self.outfile, 'wb'
            ) as out_f, self._audio_generator():
                self.main(converter=converter, out_f=out_f)
        except queue.Empty:
            self.logger.warning(
                'Audio callback timeout for %s', self.__class__.__name__
            )
        finally:
            self.notify_stop()

    @contextmanager
    def _audio_generator(self) -> Generator[Optional[Thread], None, None]:
        """
        :yield: A <Thread, Queue> pair where the thread generates raw audio
            frames (as numpy arrays) that are sent to the specified queue.
        """
        yield None

    @contextmanager
    def open_converter(self) -> Generator[Optional[AudioConverter], None, None]:
        """
        Context manager for the converter process.
        """
        if self._audio_converter_type is None:
            yield None
            return

        assert not self._converter, 'A converter process is already running'
        self._converter = self._audio_converter_type(
            ffmpeg_bin=self.ffmpeg_bin,
            sample_rate=self.sample_rate,
            channels=self.channels,
            volume=self.volume,
            dtype=self.dtype,
            chunk_size=self.blocksize,
            on_exit=self._converter_terminated.set,
            **self._converter_args,
        )

        self._converter.start()
        yield self._converter

        self._converter.stop()
        self._converter.join(timeout=2)
        self._converter = None

    @contextmanager
    def _change_state(self, state: AudioState, event_type: Type[SoundEvent]):
        """
        Changes the state and it emits the specified event if the state has
        actually changed.

        It uses a context manager pattern, and everything in between will be
        executed before the events are dispatched.
        """
        with self._state_lock:
            prev_state = self.state
            self.state = state

        yield
        if prev_state != state:
            self._notify(event_type)

    def _notify(self, event_type: Type[SoundEvent], **kwargs):
        """
        Notifies the specified event.
        """
        get_bus().post(event_type(device=self.device, **kwargs))

    def notify_start(self):
        """
        Notifies the start event.
        """
        with self._change_state(AudioState.RUNNING, self._started_event_type):
            pass

    def notify_stop(self):
        """
        Notifies the stop event.
        """
        with self._change_state(AudioState.STOPPED, self._stopped_event_type):
            if self._converter:
                self._converter.stop()
                self.paused_changed.set()
                self.paused_changed.clear()

    def notify_pause(self):
        """
        Notifies a pause toggle event.
        """
        states = {
            AudioState.PAUSED: AudioState.RUNNING,
            AudioState.RUNNING: AudioState.PAUSED,
        }

        with self._state_lock:
            new_state = states.get(self.state)
            if not new_state:
                return

            event_type = (
                self._paused_event_type
                if new_state == AudioState.PAUSED
                else self._resumed_event_type
            )

            with self._change_state(new_state, event_type):
                self.paused_changed.set()
                self.paused_changed.clear()

    @property
    def state(self):
        """
        Thread-safe wrapper for the stream state.
        """
        with self._state_lock:
            return self._state

    @state.setter
    def state(self, value: AudioState):
        """
        Thread-safe setter for the stream state.
        """
        with self._state_lock:
            self._state = value

    def asdict(self) -> dict:
        """
        Serialize the thread information.
        """
        return {
            'device': self.device,
            'outfile': self.outfile,
            'infile': self.infile,
            'direction': self.direction,
            'ffmpeg_bin': self.ffmpeg_bin,
            'channels': self.channels,
            'sample_rate': self.sample_rate,
            'dtype': self.dtype,
            'streaming': self.stream,
            'duration': self.duration,
            'blocksize': self.blocksize,
            'latency': self.latency,
            'redis_queue': self.redis_queue,
            'audio_pass_through': self.audio_pass_through,
            'state': self._state.value,
            'volume': self.volume,
            'started_time': datetime.fromtimestamp(self._started_time)
            if self._started_time
            else None,
            'stream_index': self.stream_index,
            'stream_name': self.stream_name,
        }


# vim:sw=4:ts=4:et:
