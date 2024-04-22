from typing import Callable, Optional, Sequence, Union

import pvcheetah

from platypush.message.event.assistant import (
    ConversationTimeoutEvent,
    SpeechRecognizedEvent,
)

from ._base import BaseProcessor


class SttProcessor(BaseProcessor):
    """
    Implementation of the speech-to-text processor using the Picovoice Cheetah
    engine.
    """

    def __init__(
        self, *args, get_cheetah_args: Callable[[], dict] = lambda: {}, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._get_cheetah_args = get_cheetah_args
        # model_path -> Cheetah instance cache
        self._cheetah = {self._model_path: pvcheetah.create(**self._get_cheetah_args())}

    @property
    def _model_path(self) -> Optional[str]:
        return self._get_cheetah_args().get('model_path')

    @property
    def sample_rate(self) -> int:
        return self._get_cheetah().sample_rate

    @property
    def frame_length(self) -> int:
        return self._get_cheetah().frame_length

    def _get_cheetah(self) -> pvcheetah.Cheetah:
        with self._state_lock:
            if not self._cheetah.get(self._model_path):
                self.logger.debug(
                    'Creating Cheetah instance for model %s', self._model_path
                )
                self._cheetah[self._model_path] = pvcheetah.create(
                    **self._get_cheetah_args()
                )
                self.logger.debug(
                    'Cheetah instance created for model %s', self._model_path
                )

            return self._cheetah[self._model_path]

    def process(
        self, audio: Sequence[int]
    ) -> Optional[Union[SpeechRecognizedEvent, ConversationTimeoutEvent]]:
        event = None
        cheetah = self._get_cheetah()
        partial_transcript, self._ctx.is_final = cheetah.process(audio)
        last_transcript = self._ctx.transcript

        # Concatenate the partial transcript to the context
        if partial_transcript:
            self._ctx.transcript += partial_transcript
            self.logger.info(
                'Partial transcript: %s, is_final: %s',
                self._ctx.transcript,
                self._ctx.is_final,
            )

        # If the transcript is final or the conversation timed out, then
        # process and return whatever is available in the context
        if self._ctx.is_final or self._ctx.timed_out:
            phrase = cheetah.flush() or ''
            self._ctx.transcript += phrase
            if self._ctx.transcript and self._ctx.transcript != last_transcript:
                self.logger.debug('Processed STT transcript: %s', self._ctx.transcript)
                last_transcript = self._ctx.transcript

            phrase = self._ctx.transcript
            phrase = (phrase[:1].lower() + phrase[1:]).strip()
            event = (
                SpeechRecognizedEvent(phrase=phrase)
                if phrase
                else ConversationTimeoutEvent()
            )

            self.reset()

        return event

    def reset(self):
        if not self._enabled:
            return

        with self._state_lock:
            super().reset()
            self._get_cheetah().flush()

    def stop(self):
        if not self._enabled:
            return

        super().stop()

        with self._state_lock:
            objs = self._cheetah.copy()
            for key, obj in objs.items():
                obj.delete()
                self._cheetah.pop(key)
