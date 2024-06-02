from logging import getLogger
from queue import Full, Queue
from threading import Event
from time import time
from typing import Optional

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
        self._stop_event = Event()
        self._upstream_stop_event = stop_event
        self._paused_state = PauseState()
        if paused:
            self._paused_state.pause()
        else:
            self._paused_state.resume()

        self.stream = sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype=dtype,
            blocksize=frame_size,
            callback=self._audio_callback,
        )

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
            self._audio_queue.put_nowait(AudioFrame(indata.reshape(-1), time()))
        except Full:
            self.logger.warning('Audio queue is full, dropping audio frame')

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
