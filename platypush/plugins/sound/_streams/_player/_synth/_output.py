from logging import getLogger
from queue import Empty, Queue
from typing import Callable, Optional

import sounddevice as sd

import numpy as np
from numpy.typing import NDArray


# pylint: disable=too-few-public-methods
class AudioOutputCallback:
    """
    The ``AudioSynthOutput`` is a functor that wraps the ``sounddevice.Stream``
    callback and writes raw audio data to the audio device.
    """

    def __init__(
        self,
        *args,
        audio_queue: Queue[NDArray[np.number]],
        channels: int,
        blocksize: int,
        should_stop: Callable[[], bool] = lambda: False,
        is_paused: Callable[[], bool] = lambda: False,
        queue_timeout: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._audio_queue = audio_queue
        self._channels = channels
        self._blocksize = blocksize
        self._should_stop = should_stop
        self._is_paused = is_paused
        self._queue_timeout = queue_timeout
        self.logger = getLogger(__name__)

    def _check_status(self, frames: int, status):
        """
        Checks the current status of the audio callback and raises errors if
        the processing shouldn't continue.
        """
        if self._should_stop():
            raise sd.CallbackStop

        assert frames == self._blocksize, (
            f'Received {frames} frames, expected blocksize is {self._blocksize}',
        )

        assert not status.output_underflow, 'Output underflow: increase blocksize?'
        assert not status, f'Audio callback failed: {status}'

    def _audio_callback(self, outdata: NDArray[np.number], frames: int, status):
        if self._is_paused():
            return

        self._check_status(frames, status)

        try:
            data = self._audio_queue.get_nowait()
        except Empty as e:
            raise (
                sd.CallbackStop
                if self._should_stop()
                else AssertionError('Buffer is empty: increase buffersize?')
            ) from e

        if data.shape[0] == 0:
            raise sd.CallbackStop

        audio_length = min(len(data), len(outdata))
        outdata[:audio_length] = data[:audio_length]

    # _ = time
    def __call__(self, outdata: NDArray[np.number], frames: int, _, status):
        try:
            self._audio_callback(outdata, frames, status)
        except AssertionError as e:
            self.logger.warning(str(e))
