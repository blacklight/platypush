import asyncio
from asyncio.subprocess import PIPE
from logging import getLogger
from queue import Empty

from queue import Queue
from threading import Event, RLock, Thread
from typing import Optional, Self

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
Supported input types:
    'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'float32', 'float64'
"""

_output_format_to_ffmpeg_args = {
    'wav': ('-f', 'wav'),
    'ogg': ('-f', 'ogg'),
    'mp3': ('-f', 'mp3'),
    'aac': ('-f', 'adts'),
    'flac': ('-f', 'flac'),
}


class ConverterProcess(Thread):
    """
    Wrapper for an ffmpeg converter instance.
    """

    def __init__(
        self,
        ffmpeg_bin: str,
        sample_rate: int,
        channels: int,
        dtype: str,
        chunk_size: int,
        output_format: str,
        *args,
        **kwargs,
    ):
        """
        :param ffmpeg_bin: Path to the ffmpeg binary.
        :param sample_rate: The sample rate of the input audio.
        :param channels: The number of channels of the input audio.
        :param dtype: The (numpy) data type of the raw input audio.
        :param chunk_size: Number of bytes that will be read at once from the
            ffmpeg process.
        :param output_format: Output audio format.
        """
        super().__init__(*args, **kwargs)

        ffmpeg_format = _dtype_to_ffmpeg_format.get(dtype)
        assert ffmpeg_format, (
            f'Unsupported data type: {dtype}. Supported data types: '
            f'{list(_dtype_to_ffmpeg_format.keys())}'
        )

        self._ffmpeg_bin = ffmpeg_bin
        self._ffmpeg_format = ffmpeg_format
        self._sample_rate = sample_rate
        self._channels = channels
        self._chunk_size = chunk_size
        self._output_format = output_format
        self._closed = False
        self._out_queue = Queue()
        self.ffmpeg = None
        self.logger = getLogger(__name__)
        self._loop = None
        self._should_stop = Event()
        self._stop_lock = RLock()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, *_, **__):
        self.stop()

    def _check_ffmpeg(self):
        assert (
            self.ffmpeg and self.ffmpeg.returncode is None
        ), 'The ffmpeg process has already terminated'

    def _get_format_args(self):
        ffmpeg_args = _output_format_to_ffmpeg_args.get(self._output_format)
        assert ffmpeg_args, (
            f'Unsupported output format: {self._output_format}. Supported formats: '
            f'{list(_output_format_to_ffmpeg_args.keys())}'
        )

        return ffmpeg_args

    async def _audio_proxy(self, timeout: Optional[float] = None):
        self.ffmpeg = await asyncio.create_subprocess_exec(
            self._ffmpeg_bin,
            '-f',
            self._ffmpeg_format,
            '-ar',
            str(self._sample_rate),
            '-ac',
            str(self._channels),
            '-i',
            'pipe:',
            *self._get_format_args(),
            'pipe:',
            stdin=PIPE,
            stdout=PIPE,
        )

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

            try:
                data = await asyncio.wait_for(
                    self.ffmpeg.stdout.read(self._chunk_size), timeout
                )
                self._out_queue.put(data)
            except asyncio.TimeoutError:
                self._out_queue.put(b'')

    def write(self, data: bytes):
        self._check_ffmpeg()
        assert (
            self.ffmpeg and self._loop and self.ffmpeg.stdin
        ), 'The stdin is closed for the ffmpeg process'

        self._loop.call_soon_threadsafe(self.ffmpeg.stdin.write, data)

    def read(self, timeout: Optional[float] = None) -> Optional[bytes]:
        try:
            return self._out_queue.get(timeout=timeout)
        except Empty:
            return None

    def run(self):
        super().run()
        self._loop = get_or_create_event_loop()
        try:
            self._loop.run_until_complete(self._audio_proxy(timeout=1))
        except RuntimeError as e:
            self.logger.warning(e)
        finally:
            self.stop()

    def stop(self):
        with self._stop_lock:
            self._should_stop.set()
            if self.ffmpeg:
                self.ffmpeg.kill()

            self.ffmpeg = None
            self._loop = None

    @property
    def should_stop(self) -> bool:
        return self._should_stop.is_set()


# vim:sw=4:ts=4:et:
