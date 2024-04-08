import logging
import os
from threading import Event, RLock
from time import time
from typing import Any, Dict, Optional, Sequence

import pvcheetah
import pvleopard
import pvporcupine
import pvrhino

from platypush.message.event.assistant import (
    ConversationTimeoutEvent,
    HotwordDetectedEvent,
    SpeechRecognizedEvent,
)

from ._context import ConversationContext
from ._recorder import AudioRecorder
from ._state import AssistantState


class Assistant:
    """
    A facade class that wraps the Picovoice engines under an assistant API.
    """

    def _default_callback(*_, **__):
        pass

    def __init__(
        self,
        access_key: str,
        stop_event: Event,
        hotword_enabled: bool = True,
        stt_enabled: bool = True,
        intent_enabled: bool = False,
        keywords: Optional[Sequence[str]] = None,
        keyword_paths: Optional[Sequence[str]] = None,
        keyword_model_path: Optional[str] = None,
        frame_expiration: float = 3.0,  # Don't process audio frames older than this
        speech_model_path: Optional[str] = None,
        endpoint_duration: Optional[float] = None,
        enable_automatic_punctuation: bool = False,
        start_conversation_on_hotword: bool = False,
        audio_queue_size: int = 100,
        conversation_timeout: Optional[float] = None,
        on_conversation_start=_default_callback,
        on_conversation_end=_default_callback,
        on_conversation_timeout=_default_callback,
        on_speech_recognized=_default_callback,
        on_hotword_detected=_default_callback,
    ):
        self._access_key = access_key
        self._stop_event = stop_event
        self.logger = logging.getLogger(__name__)
        self.hotword_enabled = hotword_enabled
        self.stt_enabled = stt_enabled
        self.intent_enabled = intent_enabled
        self.keywords = list(keywords or [])
        self.keyword_paths = None
        self.keyword_model_path = None
        self.frame_expiration = frame_expiration
        self.speech_model_path = speech_model_path
        self.endpoint_duration = endpoint_duration
        self.enable_automatic_punctuation = enable_automatic_punctuation
        self.start_conversation_on_hotword = start_conversation_on_hotword
        self.audio_queue_size = audio_queue_size

        self._on_conversation_start = on_conversation_start
        self._on_conversation_end = on_conversation_end
        self._on_conversation_timeout = on_conversation_timeout
        self._on_speech_recognized = on_speech_recognized
        self._on_hotword_detected = on_hotword_detected

        self._recorder = None
        self._state = AssistantState.IDLE
        self._state_lock = RLock()
        self._ctx = ConversationContext(timeout=conversation_timeout)

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

        self._cheetah: Optional[pvcheetah.Cheetah] = None
        self._leopard: Optional[pvleopard.Leopard] = None
        self._porcupine: Optional[pvporcupine.Porcupine] = None
        self._rhino: Optional[pvrhino.Rhino] = None

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

        if prev_state == AssistantState.DETECTING_SPEECH:
            self._ctx.stop()
            self._on_conversation_end()
        elif new_state == AssistantState.DETECTING_SPEECH:
            self._ctx.start()
            self._on_conversation_start()

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

    @property
    def cheetah(self) -> Optional[pvcheetah.Cheetah]:
        if not self.stt_enabled:
            return None

        if not self._cheetah:
            args: Dict[str, Any] = {'access_key': self._access_key}
            if self.speech_model_path:
                args['model_path'] = self.speech_model_path
            if self.endpoint_duration:
                args['endpoint_duration_sec'] = self.endpoint_duration
            if self.enable_automatic_punctuation:
                args['enable_automatic_punctuation'] = self.enable_automatic_punctuation

            self._cheetah = pvcheetah.create(**args)

        return self._cheetah

    def __enter__(self):
        if self.should_stop():
            return self

        if self._recorder:
            self.logger.info('A recording stream already exists')
        elif self.porcupine or self.cheetah:
            sample_rate = (self.porcupine or self.cheetah).sample_rate  # type: ignore
            frame_length = (self.porcupine or self.cheetah).frame_length  # type: ignore

            self._recorder = AudioRecorder(
                stop_event=self._stop_event,
                sample_rate=sample_rate,
                frame_size=frame_length,
                queue_size=self.audio_queue_size,
                channels=1,
            )

            self._recorder.__enter__()

            if self.porcupine:
                self.state = AssistantState.DETECTING_HOTWORD
            else:
                self.state = AssistantState.DETECTING_SPEECH

        return self

    def __exit__(self, *_):
        if self._recorder:
            self._recorder.__exit__(*_)
            self._recorder = None

        self.state = AssistantState.IDLE

        if self._cheetah:
            self._cheetah.delete()
            self._cheetah = None

        if self._leopard:
            self._leopard.delete()
            self._leopard = None

        if self._porcupine:
            self._porcupine.delete()
            self._porcupine = None

        if self._rhino:
            self._rhino.delete()
            self._rhino = None

    def __iter__(self):
        return self

    def __next__(self):
        has_data = False
        if self.should_stop() or not self._recorder:
            raise StopIteration

        while not (self.should_stop() or has_data):
            data = self._recorder.read()
            if data is None:
                continue

            frame, t = data
            if time() - t > self.frame_expiration:
                self.logger.info(
                    'Skipping audio frame older than %ss', self.frame_expiration
                )
                continue  # The audio frame is too old

            if self.porcupine and self.state == AssistantState.DETECTING_HOTWORD:
                return self._process_hotword(frame)

            if self.cheetah and self.state == AssistantState.DETECTING_SPEECH:
                return self._process_speech(frame)

        raise StopIteration

    def _process_hotword(self, frame):
        if not self.porcupine:
            return None

        keyword_index = self.porcupine.process(frame)
        if keyword_index is None:
            return None  # No keyword detected

        if keyword_index >= 0 and self.keywords:
            if self.start_conversation_on_hotword:
                self.state = AssistantState.DETECTING_SPEECH

            self._on_hotword_detected(hotword=self.keywords[keyword_index])
            return HotwordDetectedEvent(hotword=self.keywords[keyword_index])

        return None

    def _process_speech(self, frame):
        if not self.cheetah:
            return None

        event = None
        partial_transcript, self._ctx.is_final = self.cheetah.process(frame)

        if partial_transcript:
            self._ctx.partial_transcript += partial_transcript
            self.logger.info(
                'Partial transcript: %s, is_final: %s',
                self._ctx.partial_transcript,
                self._ctx.is_final,
            )

        if self._ctx.is_final or self._ctx.timed_out:
            phrase = ''
            if self.cheetah:
                phrase = self.cheetah.flush()

            self._ctx.partial_transcript += phrase
            phrase = self._ctx.partial_transcript
            phrase = phrase[:1].lower() + phrase[1:]

            if self._ctx.is_final or phrase:
                event = SpeechRecognizedEvent(phrase=phrase)
                self._on_speech_recognized(phrase=phrase)
            else:
                event = ConversationTimeoutEvent()
                self._on_conversation_timeout()

            self._ctx.reset()
            if self.hotword_enabled:
                self.state = AssistantState.DETECTING_HOTWORD

        return event


# vim:sw=4:ts=4:et:
