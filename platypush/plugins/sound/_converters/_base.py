from abc import ABC, abstractmethod
import asyncio
from asyncio.subprocess import PIPE
from logging import getLogger
from queue import Empty, Queue
from threading import Event, RLock, Thread
from typing import Any, Callable, Coroutine, Iterable, Optional

from platypush.context import get_or_create_event_loop

_dtype_to_ffmpeg_format = {
    'int8': 's8',
    'uint8': 'u8',
    'int16': 's16le',
    'uint16': 'u16le',
    'int32': 's32le',
    'uint32': 'u32le',
    'float32': 'f32le',
    'float64': 'f64le',
}
"""
Supported raw types:
    'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'float32', 'float64'
"""


class AudioConverter(Thread, ABC):
    """
    Base class for an ffmpeg audio converter instance.
    """

    _format_to_ffmpeg_args = {
        'wav': ('-f', 'wav'),
        'ogg': ('-f', 'ogg'),
        'mp3': ('-f', 'mp3'),
        'aac': ('-f', 'adts'),
        'flac': ('-f', 'flac'),
    }

    def __init__(
        self,
        *args,
        ffmpeg_bin: str,
        sample_rate: int,
        channels: int,
        volume: float,
        dtype: str,
        chunk_size: int,
        format: Optional[str] = None,  # pylint: disable=redefined-builtin
        on_exit: Optional[Callable[[], Any]] = None,
        **kwargs,
    ):
        """
        :param ffmpeg_bin: Path to the ffmpeg binary.
        :param sample_rate: The sample rate of the input/output audio.
        :param channels: The number of channels of the input/output audio.
        :param volume: Audio volume, as a percentage between 0 and 100.
        :param dtype: The (numpy) data type of the raw input/output audio.
        :param chunk_size: Number of bytes that will be read at once from the
            ffmpeg process.
        :param format: Input/output audio format.
        :param on_exit: Function to call when the ffmpeg process exits.
        """
        super().__init__(*args, **kwargs)

        ffmpeg_format = _dtype_to_ffmpeg_format.get(dtype)
        assert ffmpeg_format, (
            f'Unsupported data type: {dtype}. Supported data types: '
            f'{list(_dtype_to_ffmpeg_format.keys())}'
        )

        self._ffmpeg_bin = ffmpeg_bin
        self._ffmpeg_format = ffmpeg_format
        self._ffmpeg_task: Optional[Coroutine] = None
        self._sample_rate = sample_rate
        self._channels = channels
        self._chunk_size = chunk_size
        self._format = format
        self._closed = False
        self._out_queue = Queue()
        self.ffmpeg = None
        self.volume = volume
        self.logger = getLogger(__name__)
        self._loop = None
        self._should_stop = Event()
        self._stop_lock = RLock()
        self._on_exit = on_exit
        self._ffmpeg_terminated = Event()

    def __enter__(self) -> "AudioConverter":
        """
        Audio converter context manager.

        It starts and registers the ffmpeg converter process.
        """
        self.start()
        return self

    def __exit__(self, *_, **__):
        """
        Audio converter context manager.

        It stops and unregisters the ffmpeg converter process.
        """
        self.stop()

    def _check_ffmpeg(self):
        assert not self.terminated, 'The ffmpeg process has already terminated'

    @property
    def gain(self) -> float:
        return self.volume / 100

    @property
    def terminated(self) -> bool:
        return self._ffmpeg_terminated.is_set()

    @property
    def _default_args(self) -> Iterable[str]:
        """
        Set of arguments common to all ffmpeg converter instances.
        """
        return ('-hide_banner', '-loglevel', 'warning', '-y')

    @property
    @abstractmethod
    def _input_format_args(self) -> Iterable[str]:
        """
        Ffmpeg audio input arguments.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def _output_format_args(self):
        """
        Ffmpeg audio output arguments.
        """
        raise NotImplementedError()

    @property
    def _channel_layout_args(self) -> Iterable[str]:
        """
        Set of extra ffmpeg arguments for the channel layout.
        """
        args = ('-ac', str(self._channels))
        if self._channels == 1:
            return args + ('-channel_layout', 'mono')
        if self._channels == 2:
            return args + ('-channel_layout', 'stereo')
        return args

    @property
    def _raw_ffmpeg_args(self) -> Iterable[str]:
        """
        Ffmpeg arguments for raw audio input/output given the current
        configuration.
        """
        return (
            '-f',
            self._ffmpeg_format,
            '-ar',
            str(self._sample_rate),
            *self._channel_layout_args,
        )

    @property
    def _audio_volume_args(self) -> Iterable[str]:
        """
        Ffmpeg audio volume arguments.
        """
        return ('-filter:a', f'volume={self.gain}')

    @property
    def _input_source_args(self) -> Iterable[str]:
        """
        Default arguments for the ffmpeg input source (default: ``-i pipe:``,
        ffmpeg will read from a pipe filled by the application).
        """
        return ('-i', 'pipe:')

    @property
    def _output_target_args(self) -> Iterable[str]:
        """
        Default arguments for the ffmpeg output target (default: ``pipe:``,
        ffmpeg will write the output to a pipe read by the application).
        """
        return ('pipe:',)

    @property
    def _converter_stdin(self) -> Optional[int]:
        """
        Default stdin file descriptor to be used by the ffmpeg converter.

        Default: ``PIPE``, as the ffmpeg process by default reads audio frames
        from the stdin.
        """
        return PIPE

    @property
    def _compressed_ffmpeg_args(self) -> Iterable[str]:
        """
        Ffmpeg arguments for the compressed audio given the current
        configuration.
        """
        if not self._format:
            return ()

        ffmpeg_args = self._format_to_ffmpeg_args.get(self._format)
        assert ffmpeg_args, (
            f'Unsupported output format: {self._format}. Supported formats: '
            f'{list(self._format_to_ffmpeg_args.keys())}'
        )

        return ffmpeg_args

    async def _audio_proxy(self, timeout: Optional[float] = None):
        """
        Proxy the converted audio stream to the output queue for downstream
        consumption.
        """
        ffmpeg_args = (
            self._ffmpeg_bin,
            *self._default_args,
            *self._input_format_args,
            *self._input_source_args,
            *self._output_format_args,
            *self._output_target_args,
        )

        self.ffmpeg = await asyncio.create_subprocess_exec(
            *ffmpeg_args,
            stdin=self._converter_stdin,
            stdout=PIPE,
        )

        self.logger.info('Running ffmpeg: %s', ' '.join(ffmpeg_args))

        try:
            await asyncio.wait_for(self.ffmpeg.wait(), 0.1)
        except asyncio.TimeoutError:
            pass

        while (
            self._loop
            and self.ffmpeg
            and self.ffmpeg.returncode is None
            and not self.should_stop
        ):
            self._check_ffmpeg()
            assert (
                self.ffmpeg and self.ffmpeg.stdout
            ), 'The stdout is closed for the ffmpeg process'

            self._ffmpeg_terminated.clear()

            try:
                reader = asyncio.create_task(self.ffmpeg.stdout.read(self._chunk_size))
                data = await asyncio.wait_for(reader, timeout)
                self._out_queue.put(data)
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                self.logger.warning('Audio proxy error: %s', e)
                break

        self._out_queue.put(b'')

    def write(self, data: bytes):
        """
        Write raw data to the ffmpeg process.
        """
        self._check_ffmpeg()
        assert (
            self.ffmpeg and self._loop and self.ffmpeg.stdin
        ), 'The stdin is closed for the ffmpeg process'

        self._loop.call_soon_threadsafe(self.ffmpeg.stdin.write, data)

    def read(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Read the next chunk of converted audio bytes from the converter queue.
        """
        try:
            return self._out_queue.get(timeout=timeout)
        except Empty:
            return None

    def run(self):
        """
        Main runner. It runs the audio proxy in a loop and cleans up everything
        in case of stop/failure.
        """
        super().run()
        self._loop = get_or_create_event_loop()
        try:
            self._ffmpeg_task = self._audio_proxy(timeout=1)
            self._loop.run_until_complete(self._ffmpeg_task)
        except RuntimeError as e:
            self.logger.warning(e)
        finally:
            self.stop()

    def stop(self):
        """
        Sets the stop event, kills the ffmpeg process and resets the context.
        """
        with self._stop_lock:
            self._should_stop.set()
            if self._ffmpeg_task:
                self._ffmpeg_task.close()
                self._ffmpeg_task = None

            try:
                if self.ffmpeg and self.ffmpeg.returncode is None:
                    self.ffmpeg.kill()
            except ProcessLookupError:
                pass

            self.ffmpeg = None
            self._loop = None

        self._ffmpeg_terminated.set()

        if self._on_exit:
            self._on_exit()

    @property
    def should_stop(self) -> bool:
        """
        Proxy property for the ``_should_stop`` event.
        """
        return self._should_stop.is_set()


# vim:sw=4:ts=4:et:
