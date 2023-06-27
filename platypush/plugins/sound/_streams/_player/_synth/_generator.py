from logging import getLogger
from queue import Full, Queue
from threading import Thread
from time import time
from typing import Any, Callable, Optional

import numpy as np
from numpy.typing import NDArray

from ._mix import Mix


class AudioGenerator(Thread):
    """
    The ``AudioGenerator`` class is a thread that generates synthetic raw audio
    waves and dispatches them to a queue that can be consumed by other players,
    streamers and converters.
    """

    def __init__(
        self,
        *args,
        audio_queue: Queue[NDArray[np.number]],
        mix: Mix,
        blocksize: int,
        sample_rate: int,
        queue_timeout: Optional[float] = None,
        should_stop: Callable[[], bool] = lambda: False,
        wait_running: Callable[[], Any] = lambda: None,
        on_stop: Callable[[], Any] = lambda: None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._audio_queue = audio_queue
        self._t_start: float = 0
        self._blocksize: int = blocksize
        self._sample_rate: int = sample_rate
        self._blocktime = self._blocksize / self._sample_rate
        self._should_stop = should_stop
        self._queue_timeout = queue_timeout
        self._wait_running = wait_running
        self._on_stop = on_stop
        self.mix = mix
        self.logger = getLogger(__name__)

    def _next_t(self, t: float) -> float:
        """
        Calculates the next starting time for the wave function.
        """
        return (
            min(t + self._blocktime, self._duration)
            if self._duration is not None
            else t + self._blocktime
        )

    def should_stop(self) -> bool:
        """
        Stops if the upstream dependencies have signalled to stop or if the
        duration is set and we have reached it.
        """
        return self._should_stop() or (
            self._duration is not None and time() - self._t_start >= self._duration
        )

    @property
    def _duration(self) -> Optional[float]:
        """
        Proxy to the mix object's duration.
        """
        return self.mix.duration()

    def run(self):
        super().run()
        self._t_start = time()
        t = 0

        while not self.should_stop():
            self._wait_running()
            if self.should_stop():
                break

            next_t = self._next_t(t)

            try:
                data = self.mix.get_wave(
                    t_start=t, t_end=next_t, sample_rate=self._sample_rate
                )
            except Exception as e:
                self.logger.warning('Could not generate the audio wave: %s', e)
                break

            try:
                self._audio_queue.put(data, timeout=self._queue_timeout)
                t = next_t
            except Full:
                self.logger.warning(
                    'The processing queue is full: either the audio consumer is stuck, '
                    'or you may want to increase queue_size'
                )

        self._on_stop()
