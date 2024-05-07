import logging
from abc import ABC, abstractmethod
from queue import Empty, Queue
from threading import Event, RLock, Thread, get_ident
from typing import Any, Optional, Sequence

from platypush.message.event.assistant import AssistantEvent

from .._context import ConversationContext


class BaseProcessor(ABC, Thread):
    """
    Base speech processor class. It is implemented by the ``SttProcessor`` and
    the ``IntentProcessor`` classes.
    """

    def __init__(
        self,
        *args,
        stop_event: Event,
        enabled: bool = True,
        conversation_timeout: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(*args, name=f'picovoice:{self.__class__.__name__}', **kwargs)

        self.logger = logging.getLogger(self.name)
        self._enabled = enabled
        self._audio_queue = Queue()
        self._stop_event = stop_event
        self._ctx = ConversationContext(timeout=conversation_timeout)
        self._event_queue = Queue()
        # This event is set if the upstream processor is waiting for an event
        # from this processor
        self._event_wait = Event()
        # This event is set when the processor is done with the audio
        # processing and it's ready to accept a new audio frame
        self._processing_done = Event()
        self._processing_done.set()
        self._state_lock = RLock()

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def wait_stop(self, timeout: Optional[float] = None) -> bool:
        return self._stop_event.wait(timeout)

    def enqueue(self, audio: Sequence[int]):
        if not self._enabled:
            return

        self._event_wait.set()
        self._processing_done.clear()
        self._audio_queue.put_nowait(audio)

    def reset(self) -> Optional[Any]:
        """
        Reset any pending context.
        """
        if not self._enabled:
            return

        with self._state_lock:
            self._ctx.reset()
            self._event_queue.queue.clear()
            self._event_wait.clear()
            self._processing_done.set()

    @property
    def processing_done(self) -> Event:
        return self._processing_done

    @property
    @abstractmethod
    def _model_path(self) -> Optional[str]:
        """
        Return the model path.
        """

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """
        :return: The sample rate wanted by Cheetah/Rhino.
        """

    @property
    @abstractmethod
    def frame_length(self) -> int:
        """
        :return: The frame length wanted by Cheetah/Rhino.
        """

    def last_event(self) -> Optional[AssistantEvent]:
        """
        :return: The latest event that was processed by the processor.
        """
        with self._state_lock:
            evt = None
            try:
                while True:
                    evt = self._event_queue.get_nowait()
            except Empty:
                pass

            if evt:
                self._event_wait.clear()

            return evt

    @abstractmethod
    def process(self, audio: Sequence[int]) -> Optional[AssistantEvent]:
        """
        Process speech events from a raw audio input.
        """

    def run(self):
        super().run()
        if not self._enabled:
            self.wait_stop()

        self.reset()
        self._processing_done.clear()
        self.logger.info('Processor started: %s', self.name)

        while not self.should_stop():
            audio = self._audio_queue.get()

            # The thread is stopped when it receives a None object
            if audio is None:
                break

            # Don't process the audio if the upstream processor is not waiting
            # for an event
            if not self._event_wait.is_set():
                continue

            try:
                self._processing_done.clear()
                event = self.process(audio)

                if event:
                    self.logger.debug(
                        'Dispatching event processed from %s: %s', self.name, event
                    )
                    self._event_queue.put_nowait(event)
                    self._processing_done.set()
            except Exception as e:
                self.logger.error(
                    'An error occurred while processing the audio on %s: %s',
                    self.name,
                    e,
                    exc_info=e,
                )
                self.wait_stop(timeout=1)
                self._processing_done.set()
                continue

        self._processing_done.set()
        self.reset()
        self.logger.info('Processor stopped: %s', self.name)

    def stop(self):
        if not self._enabled:
            return

        self._audio_queue.put_nowait(None)
        if self.is_alive() and self.ident != get_ident():
            self.logger.debug('Stopping %s', self.name)
            self.join()

    def on_conversation_start(self):
        self._ctx.start()

    def on_conversation_end(self):
        self.reset()

    def on_conversation_reset(self):
        self.reset()
