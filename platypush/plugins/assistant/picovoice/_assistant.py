import logging
import os
from queue import Full, Queue
from threading import Event, RLock, Thread
from time import time
from typing import Any, Dict, Optional, Sequence

import pvporcupine

from platypush.common.assistant import AudioRecorder
from platypush.context import get_plugin
from platypush.message.event.assistant import (
    AssistantEvent,
    ConversationTimeoutEvent,
    HotwordDetectedEvent,
    IntentRecognizedEvent,
    SpeechRecognizedEvent,
)
from platypush.plugins.tts.picovoice import TtsPicovoicePlugin
from ._speech import SpeechProcessor
from ._state import AssistantState


class Assistant(Thread):
    """
    A facade class that wraps the Picovoice engines under an assistant API.
    """

    @staticmethod
    def _default_callback(*_, **__):
        pass

    def __init__(
        self,
        access_key: str,
        stop_event: Event,
        hotword_enabled: bool = True,
        stt_enabled: bool = True,
        keywords: Optional[Sequence[str]] = None,
        keyword_paths: Optional[Sequence[str]] = None,
        keyword_model_path: Optional[str] = None,
        frame_expiration: float = 3.0,  # Don't process audio frames older than this
        speech_model_path: Optional[str] = None,
        intent_model_path: Optional[str] = None,
        endpoint_duration: Optional[float] = None,
        enable_automatic_punctuation: bool = False,
        start_conversation_on_hotword: bool = False,
        audio_queue_size: int = 100,
        muted: bool = False,
        conversation_timeout: Optional[float] = None,
        on_conversation_start=_default_callback,
        on_conversation_end=_default_callback,
        on_conversation_timeout=_default_callback,
        on_speech_recognized=_default_callback,
        on_intent_matched=_default_callback,
        on_hotword_detected=_default_callback,
    ):
        super().__init__(name='picovoice:Assistant')

        self._access_key = access_key
        self._stop_event = stop_event
        self.logger = logging.getLogger(__name__)
        self.hotword_enabled = hotword_enabled
        self.stt_enabled = stt_enabled
        self.keywords = list(keywords or [])
        self.keyword_paths = None
        self.keyword_model_path = None
        self.frame_expiration = frame_expiration
        self.endpoint_duration = endpoint_duration
        self.enable_automatic_punctuation = enable_automatic_punctuation
        self.start_conversation_on_hotword = start_conversation_on_hotword
        self.audio_queue_size = audio_queue_size
        self._responding = Event()
        self._muted = muted
        self._speech_model_path = speech_model_path
        self._speech_model_path_override = None
        self._intent_model_path = intent_model_path
        self._intent_model_path_override = None
        self._in_ctx = False

        self._speech_processor = SpeechProcessor(
            stop_event=stop_event,
            stt_enabled=stt_enabled,
            intent_enabled=self.intent_enabled,
            conversation_timeout=conversation_timeout,
            model_path=speech_model_path,
            get_cheetah_args=self._get_speech_engine_args,
            get_rhino_args=self._get_intent_engine_args,
        )

        self._on_conversation_start = on_conversation_start
        self._on_conversation_end = on_conversation_end
        self._on_conversation_timeout = on_conversation_timeout
        self._on_speech_recognized = on_speech_recognized
        self._on_intent_matched = on_intent_matched
        self._on_hotword_detected = on_hotword_detected

        self._recorder = None
        self._state = AssistantState.IDLE
        self._state_lock = RLock()
        self._evt_queue = Queue(maxsize=100)

        if hotword_enabled:
            if not keywords:
                raise ValueError(
                    'You need to provide a list of keywords if the wake-word engine is enabled'
                )

            if keyword_paths:
                keyword_paths = [os.path.expanduser(path) for path in keyword_paths]
                missing_paths = [
                    path for path in keyword_paths if not os.path.isfile(path)
                ]
                if missing_paths:
                    raise FileNotFoundError(f'Keyword files not found: {missing_paths}')

                self.keyword_paths = keyword_paths

            if keyword_model_path:
                keyword_model_path = os.path.expanduser(keyword_model_path)
                if not os.path.isfile(keyword_model_path):
                    raise FileNotFoundError(
                        f'Keyword model file not found: {keyword_model_path}'
                    )

                self.keyword_model_path = keyword_model_path

        self._porcupine: Optional[pvporcupine.Porcupine] = None

    @property
    def intent_enabled(self) -> bool:
        return self.intent_model_path is not None

    @property
    def is_responding(self) -> bool:
        return self._responding.is_set()

    @property
    def speech_model_path(self) -> Optional[str]:
        return self._speech_model_path_override or self._speech_model_path

    @property
    def intent_model_path(self) -> Optional[str]:
        return self._intent_model_path_override or self._intent_model_path

    @property
    def tts(self) -> TtsPicovoicePlugin:
        p = get_plugin('tts.picovoice')
        assert p, 'Picovoice TTS plugin not configured/found'
        return p

    def set_responding(self, responding: bool):
        if responding:
            self._responding.set()
        else:
            self._responding.clear()

    def should_stop(self):
        return self._stop_event.is_set()

    def wait_stop(self):
        self._stop_event.wait()

    @property
    def state(self) -> AssistantState:
        with self._state_lock:
            return self._state

    @state.setter
    def state(self, state: AssistantState):
        with self._state_lock:
            prev_state = self._state
            self._state = state
            new_state = self.state

        if prev_state == new_state:
            return

        self.logger.info('Assistant state transition: %s -> %s', prev_state, new_state)
        if prev_state == AssistantState.DETECTING_SPEECH:
            self.tts.stop()
            self._speech_model_path_override = None
            self._intent_model_path_override = None
            self._speech_processor.on_conversation_end()
            self._on_conversation_end()
        elif new_state == AssistantState.DETECTING_SPEECH:
            self._speech_processor.on_conversation_start()
            self._on_conversation_start()

        if new_state == AssistantState.DETECTING_HOTWORD:
            self.tts.stop()
            self._speech_processor.on_conversation_reset()

        # Put a null event on the event queue to unblock next_event
        self._evt_queue.put(None)

    @property
    def porcupine(self) -> Optional[pvporcupine.Porcupine]:
        if not self.hotword_enabled:
            return None

        if not self._porcupine:
            args: Dict[str, Any] = {'access_key': self._access_key}
            if self.keywords:
                args['keywords'] = self.keywords
            if self.keyword_paths:
                args['keyword_paths'] = self.keyword_paths
            if self.keyword_model_path:
                args['model_path'] = self.keyword_model_path

            self._porcupine = pvporcupine.create(**args)

        return self._porcupine

    def _get_speech_engine_args(self) -> dict:
        args: Dict[str, Any] = {'access_key': self._access_key}
        if self.speech_model_path:
            args['model_path'] = self.speech_model_path
        if self.endpoint_duration:
            args['endpoint_duration_sec'] = self.endpoint_duration
        if self.enable_automatic_punctuation:
            args['enable_automatic_punctuation'] = self.enable_automatic_punctuation

        return args

    def _get_intent_engine_args(self) -> dict:
        args: Dict[str, Any] = {'access_key': self._access_key}
        args['context_path'] = self.intent_model_path
        if self.endpoint_duration:
            args['endpoint_duration_sec'] = self.endpoint_duration
        if self.enable_automatic_punctuation:
            args['enable_automatic_punctuation'] = self.enable_automatic_punctuation

        return args

    def __enter__(self):
        """
        Get the assistant ready to start processing audio frames.
        """
        if self.should_stop():
            return self

        assert not self.is_alive(), 'The assistant is already running'
        self._in_ctx = True

        if self._recorder:
            self.logger.info('A recording stream already exists')
        elif self.hotword_enabled or self.stt_enabled or self.intent_enabled:
            sample_rate = (self.porcupine or self._speech_processor).sample_rate
            frame_length = (self.porcupine or self._speech_processor).frame_length
            self._recorder = AudioRecorder(
                stop_event=self._stop_event,
                sample_rate=sample_rate,
                frame_size=frame_length,
                queue_size=self.audio_queue_size,
                paused=self._muted,
                channels=1,
            )

            self._speech_processor.__enter__()
            self._recorder.__enter__()

            if self.porcupine:
                self.state = AssistantState.DETECTING_HOTWORD
            else:
                self.state = AssistantState.DETECTING_SPEECH

        self.start()
        return self

    def __exit__(self, *_):
        """
        Stop the assistant and release all resources.
        """
        self._in_ctx = False
        if self._recorder:
            self._recorder.__exit__(*_)
            self._recorder = None

        self.state = AssistantState.IDLE

        if self._porcupine:
            self._porcupine.delete()
            self._porcupine = None

        self._speech_processor.__exit__(*_)

    def __iter__(self):
        """
        Iterate over processed assistant events.
        """
        return self

    def __next__(self):
        """
        Process the next audio frame and return the corresponding event.
        """
        if self.should_stop() or not self._recorder:
            raise StopIteration

        if self.hotword_enabled and self.state == AssistantState.DETECTING_HOTWORD:
            return self._evt_queue.get()

        evt = None
        if (
            self._speech_processor.enabled
            and self.state == AssistantState.DETECTING_SPEECH
        ):
            evt = self._speech_processor.next_event()

        if isinstance(evt, SpeechRecognizedEvent):
            self._on_speech_recognized(phrase=evt.args['phrase'])
        if isinstance(evt, IntentRecognizedEvent):
            self._on_intent_matched(
                intent=evt.args['intent'], slots=evt.args.get('slots', {})
            )
        if isinstance(evt, ConversationTimeoutEvent):
            self._on_conversation_timeout()

        if evt:
            self._speech_processor.reset()

        if (
            evt
            and self.state == AssistantState.DETECTING_SPEECH
            and self.hotword_enabled
        ):
            self.state = AssistantState.DETECTING_HOTWORD

        return evt

    def mute(self):
        self._muted = True
        if self._recorder:
            self._recorder.pause()

    def unmute(self):
        self._muted = False
        if self._recorder:
            self._recorder.resume()

    def set_mic_mute(self, mute: bool):
        if mute:
            self.mute()
        else:
            self.unmute()

    def toggle_mic_mute(self):
        if self._muted:
            self.unmute()
        else:
            self.mute()

    def _process_hotword(self, frame) -> Optional[HotwordDetectedEvent]:
        if not self.porcupine:
            return None

        keyword_index = self.porcupine.process(frame)
        if keyword_index is None:
            return None  # No keyword detected

        if keyword_index >= 0 and self.keywords:
            if self.start_conversation_on_hotword:
                self.state = AssistantState.DETECTING_SPEECH

            self.tts.stop()  # Stop any ongoing TTS when the hotword is detected
            self._on_hotword_detected(hotword=self.keywords[keyword_index])
            return HotwordDetectedEvent(hotword=self.keywords[keyword_index])

        return None

    def override_speech_model(self, model_path: Optional[str]):
        self._speech_model_path_override = model_path

    def override_intent_model(self, model_path: Optional[str]):
        self._intent_model_path_override = model_path

    def _put_event(self, evt: AssistantEvent):
        try:
            self._evt_queue.put_nowait(evt)
        except Full:
            self.logger.warning('The assistant event queue is full')

    def run(self):
        assert (
            self._in_ctx
        ), 'The assistant can only be started through a context manager'

        super().run()

        while not self.should_stop() and self._recorder:
            self._recorder.wait_start()
            if self.should_stop():
                break

            data = self._recorder.read()
            if data is None:
                continue

            frame, t = data
            if time() - t > self.frame_expiration:
                self.logger.info(
                    'Skipping audio frame older than %ss', self.frame_expiration
                )
                continue  # The audio frame is too old

            if self.hotword_enabled and self.state == AssistantState.DETECTING_HOTWORD:
                evt = self._process_hotword(frame)
                if evt:
                    self._put_event(evt)

                continue

            if (
                self._speech_processor.enabled
                and self.state == AssistantState.DETECTING_SPEECH
            ):
                self._speech_processor.process(frame, block=False)

        self.logger.info('Assistant stopped')


# vim:sw=4:ts=4:et:
