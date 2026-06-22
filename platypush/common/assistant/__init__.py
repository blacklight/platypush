from logging import getLogger
from queue import Empty, Full, Queue
from threading import Event
from time import sleep, time
from typing import Optional, Union

import numpy as np
import sounddevice as sd

from platypush.common.audio import resolve_audio_device
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
        device: Optional[Union[int, str]] = None,
        volume: float = 100,
        paused: bool = False,
        dtype: str = 'int16',
        queue_size: int = 100,
        open_retries: int = 5,
    ):
        if volume < 0:
            raise ValueError('volume must be greater than or equal to 0')

        self.logger = getLogger(__name__)
        self._audio_queue: Queue[AudioFrame] = Queue(maxsize=queue_size)
        self.frame_size = frame_size
        self._target_sample_rate = sample_rate
        self._device = resolve_audio_device(device, 'input')
        self._gain = volume / 100
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
            device=self._device,
            dtype=dtype,
            frame_size=frame_size,
            retries=open_retries,
        )

    def _open_stream(
        self,
        sample_rate: int,
        channels: int,
        device: Optional[Union[int, str]],
        dtype: str,
        frame_size: int,
        retries: int = 5,
        retry_delay: float = 1.0,
    ):
        """
        Try to open the audio stream at the requested sample rate. If the
        device doesn't support it, fall back to the device's default rate and
        resample in software. Retries on transient "device unavailable" errors.
        """
        last_error: Optional[Exception] = None

        for attempt in range(retries):
            if self.should_stop():
                raise RuntimeError('Audio recorder stop requested')

            try:
                return self._try_open_stream(
                    sample_rate=sample_rate,
                    channels=channels,
                    device=device,
                    dtype=dtype,
                    frame_size=frame_size,
                )
            except sd.PortAudioError as e:
                last_error = e
                # Retry only on "Device unavailable" (-9985); other errors
                # (like invalid sample rate) are already handled inside
                # _try_open_stream via the native-rate fallback.
                if attempt < retries - 1:
                    self.logger.debug(
                        'Audio device unavailable, retrying in %.1fs '
                        '(attempt %d/%d)',
                        retry_delay,
                        attempt + 1,
                        retries,
                    )
                    sleep(retry_delay)

        raise last_error  # type: ignore[misc]

    def _try_open_stream(
        self,
        sample_rate: int,
        channels: int,
        device: Optional[Union[int, str]],
        dtype: str,
        frame_size: int,
    ):
        """
        Single attempt to open the stream. Falls back to native sample rate
        if the requested rate is not supported.
        """
        try:
            stream = sd.InputStream(
                samplerate=sample_rate,
                device=device,
                channels=channels,
                dtype=dtype,
                blocksize=frame_size,
                callback=self._audio_callback,
            )
            return stream, sample_rate
        except sd.PortAudioError as e:
            # -9997 = paInvalidSampleRate — fall back to native rate
            if len(e.args) >= 2 and e.args[1] == -9997:
                pass
            else:
                raise

        # Fall back to the device's default sample rate
        device_info = sd.query_devices(device=device, kind='input')
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
            device=device,
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
        Stop and close the audio stream, releasing the device.
        """
        self.stop()
        self.stream.close()

    def _audio_callback(self, indata, *_):
        if self.should_stop() or self.paused:
            return

        try:
            data = indata.reshape(-1)
            if self._actual_sample_rate != self._target_sample_rate:
                data = self._resample(data)
            data = self._apply_gain(data)
            self._audio_queue.put_nowait(AudioFrame(data, time()))
        except Full:
            self.logger.warning('Audio queue is full, dropping audio frame')

    def _apply_gain(self, data: np.ndarray) -> np.ndarray:
        if self._gain == 1:
            return data

        amplified = data.astype(np.float64) * self._gain
        if np.issubdtype(data.dtype, np.integer):
            info = np.iinfo(data.dtype)
            amplified = np.clip(amplified, info.min, info.max)
        elif np.issubdtype(data.dtype, np.floating):
            amplified = np.clip(amplified, -1.0, 1.0)

        return amplified.astype(data.dtype)

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
        except (Empty, TimeoutError):
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
