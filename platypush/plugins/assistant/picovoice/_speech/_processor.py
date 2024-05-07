import logging
from queue import Queue
from threading import Event
from typing import Callable, Optional, Sequence

from platypush.message.event.assistant import AssistantEvent, ConversationTimeoutEvent
from platypush.utils import wait_for_either

from ._intent import IntentProcessor
from ._stt import SttProcessor


class SpeechProcessor:
    """
    Speech processor class that wraps the STT and Intent processors under the
    same interface.
    """

    def __init__(
        self,
        stop_event: Event,
        model_path: Optional[str] = None,
        stt_enabled: bool = True,
        intent_enabled: bool = False,
        conversation_timeout: Optional[float] = None,
        get_cheetah_args: Callable[[], dict] = lambda: {},
        get_rhino_args: Callable[[], dict] = lambda: {},
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._stt_enabled = stt_enabled
        self._intent_enabled = intent_enabled
        self._model_path = model_path
        self._conversation_timeout = conversation_timeout
        self._audio_queue = Queue()
        self._stop_event = stop_event
        self._get_cheetah_args = get_cheetah_args
        self._get_rhino_args = get_rhino_args

        self._stt_processor = SttProcessor(
            conversation_timeout=conversation_timeout,
            stop_event=stop_event,
            enabled=stt_enabled,
            get_cheetah_args=get_cheetah_args,
        )

        self._intent_processor = IntentProcessor(
            conversation_timeout=conversation_timeout,
            stop_event=stop_event,
            enabled=intent_enabled,
            get_rhino_args=get_rhino_args,
        )

    @property
    def enabled(self) -> bool:
        """
        The processor is enabled if either the STT or the Intent processor are
        enabled.
        """
        return self._stt_enabled or self._intent_enabled

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def next_event(self, timeout: Optional[float] = None) -> Optional[AssistantEvent]:
        evt = None

        # Wait for either the STT or Intent processor to finish processing the audio
        completed = wait_for_either(
            self._stt_processor.processing_done,
            self._intent_processor.processing_done,
            self._stop_event,
            timeout=timeout,
        )

        if not completed:
            self.logger.warning('Timeout while waiting for the processors to finish')

        # Immediately return if the stop event is set
        if self.should_stop():
            return evt

        with self._stt_processor._state_lock, self._intent_processor._state_lock:
            # Priority to the intent processor event, if the processor is enabled
            if self._intent_enabled:
                evt = self._intent_processor.last_event()

            # If the intent processor didn't return any event, then return the STT
            # processor event
            if (
                not evt or isinstance(evt, ConversationTimeoutEvent)
            ) and self._stt_enabled:
                # self._stt_processor.processing_done.wait(timeout=timeout)
                evt = self._stt_processor.last_event()

            if evt:
                self._stt_processor.reset()
                self._intent_processor.reset()

            return evt

    def process(
        self, audio: Sequence[int], block: bool = True, timeout: Optional[float] = None
    ) -> Optional[AssistantEvent]:
        """
        Process an audio frame.

        The audio frame is enqueued to both the STT and Intent processors, if
        enabled. The function waits for either processor to finish processing
        the audio, and returns the event from the first processor that returns
        a result.

        Priority is given to the Intent processor if enabled, otherwise the STT
        processor is used.
        """
        # Enqueue the audio to both the STT and Intent processors if enabled
        if self._stt_enabled:
            self._stt_processor.enqueue(audio)

        if self._intent_enabled:
            self._intent_processor.enqueue(audio)

        if not block:
            return None

        return self.next_event(timeout=timeout)

    def __enter__(self):
        """
        Context manager entry point - it wraps :meth:`start`.
        """
        self.start()

    def __exit__(self, *_, **__):
        """
        Context manager exit point - it wraps :meth:`stop`.
        """
        self.stop()

    def start(self):
        """
        Start the STT and Intent processors.
        """
        if self._stt_enabled:
            self._stt_processor.start()

        if self._intent_enabled:
            self._intent_processor.start()

    def stop(self):
        """
        Stop the STT and Intent processors.
        """
        self._stt_processor.stop()
        self._intent_processor.stop()

    def on_conversation_start(self):
        if self._stt_enabled:
            self._stt_processor.on_conversation_start()

        if self._intent_enabled:
            self._intent_processor.on_conversation_start()

    def on_conversation_end(self):
        if self._stt_enabled:
            self._stt_processor.on_conversation_end()

        if self._intent_enabled:
            self._intent_processor.on_conversation_end()

    def on_conversation_reset(self):
        if self._stt_enabled:
            self._stt_processor.on_conversation_reset()

        if self._intent_enabled:
            self._intent_processor.on_conversation_reset()

    def reset(self):
        """
        Reset the state of the STT and Intent processors.
        """
        self._stt_processor.reset()
        self._intent_processor.reset()

    @property
    def sample_rate(self) -> int:
        """
        The sample rate of the audio frames.
        """
        if self._intent_enabled:
            return self._intent_processor.sample_rate

        if self._stt_enabled:
            return self._stt_processor.sample_rate

        raise ValueError('No processor enabled')

    @property
    def frame_length(self) -> int:
        """
        The frame length of the audio frames.
        """
        if self._intent_enabled:
            return self._intent_processor.frame_length

        if self._stt_enabled:
            return self._stt_processor.frame_length

        raise ValueError('No processor enabled')
