from logging import getLogger
from queue import Full, Queue
from threading import Event
from time import time
from typing import Optional

import numpy as np
import sounddevice as sd

from platypush.utils import wait_for_either

from ._state import AudioFrame, PauseState


class AudioRecorder:
    """
    Audio recorder component that uses the sounddevice library to record audio
    from the microphone.
    """

    def __init__(
        self,
        stop_event: Event,
        sample_rate: int,
        frame_size: int,
        channels: int,
        paused: bool = False,
        dtype: str = 'int16',
        queue_size: int = 100,
    ):
        self.logger = getLogger(__name__)
        self._audio_queue: Queue[AudioFrame] = Queue(maxsize=queue_size)
        self.frame_size = frame_size
        self._target_sample_rate = sample_rate
        self._dtype = dtype
        self._stop_event = Event()
        self._upstream_stop_event = stop_event
        self._paused_state = PauseState()
        if paused:
            self._paused_state.pause()
        else:
            self._paused_state.resume()

        self.stream, self._actual_sample_rate = self._open_stream(
            sample_rate=sample_rate,
            channels=channels,
            dtype=dtype,
            frame_size=frame_size,
        )

    def _open_stream(
        self,
        sample_rate: int,
        channels: int,
        dtype: str,
        frame_size: int,
    ):
        """
        Try to open the audio stream at the requested sample rate. If the
        device doesn't support it, fall back to the device's default rate and
        resample in software.
        """
        try:
            stream = sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                dtype=dtype,
                blocksize=frame_size,
                callback=self._audio_callback,
            )
            return stream, sample_rate
        except sd.PortAudioError:
            pass

        # Fall back to the device's default sample rate
        device_info = sd.query_devices(kind='input')
        native_rate = int(device_info['default_samplerate'])  # type: ignore
        # Adjust blocksize to produce the equivalent duration at the native rate
        native_block = int(frame_size * native_rate / sample_rate)
        self.logger.warning(
            'Audio device does not support %d Hz; '
            'using native rate %d Hz with software resampling',
            sample_rate,
            native_rate,
        )

        stream = sd.InputStream(
            samplerate=native_rate,
            channels=channels,
            dtype=dtype,
            blocksize=native_block,
            callback=self._audio_callback,
        )
        return stream, native_rate

    @property
    def paused(self):
        return self._paused_state.paused

    def __enter__(self):
        """
        Start the audio stream.
        """
        return self.start()

    def __exit__(self, *_):
        """
        Stop the audio stream.
        """
        self.stop()

    def _audio_callback(self, indata, *_):
        if self.should_stop() or self.paused:
            return

        try:
            data = indata.reshape(-1)
            if self._actual_sample_rate != self._target_sample_rate:
                data = self._resample(data)
            self._audio_queue.put_nowait(AudioFrame(data, time()))
        except Full:
            self.logger.warning('Audio queue is full, dropping audio frame')

    def _resample(self, data: np.ndarray) -> np.ndarray:
        """Resample audio data from the actual device rate to the target rate."""
        target_len = int(
            len(data) * self._target_sample_rate / self._actual_sample_rate
        )
        indices = np.linspace(0, len(data) - 1, target_len)
        resampled = np.interp(indices, np.arange(len(data)), data.astype(np.float64))
        return resampled.astype(self._dtype)

    def read(self, timeout: Optional[float] = None):
        """
        Read an audio frame from the queue.

        :param timeout: Timeout in seconds. If None, the method will block until
            an audio frame is available.
        :return: Audio frame or None if the timeout has expired.
        """
        try:
            return self._audio_queue.get(timeout=timeout)
        except TimeoutError:
            self.logger.debug('Audio queue is empty')
            return None

    def start(self):
        """
        Start the audio stream.
        """
        self._stop_event.clear()
        self.stream.start()
        return self

    def stop(self):
        """
        Stop the audio stream.
        """
        self._stop_event.set()
        self.stream.stop()

    def pause(self):
        """
        Pause the audio stream.
        """
        self._paused_state.pause()

    def resume(self):
        """
        Resume the audio stream.
        """
        self._paused_state.resume()

    def toggle(self):
        """
        Toggle the audio stream pause state.
        """
        self._paused_state.toggle()

    def should_stop(self):
        return self._stop_event.is_set() or self._upstream_stop_event.is_set()

    def wait(self, timeout: Optional[float] = None):
        """
        Wait until the audio stream is stopped.
        """
        wait_for_either(self._stop_event, self._upstream_stop_event, timeout=timeout)

    def wait_start(self, timeout: Optional[float] = None):
        """
        Wait until the audio stream is started.
        """
        wait_for_either(
            self._stop_event,
            self._upstream_stop_event,
            self._paused_state._recording_event,  # pylint: disable=protected-access
            timeout=timeout,
        )
