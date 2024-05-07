from typing import Callable, Optional, Sequence, Union

import pvrhino

from platypush.message.event.assistant import (
    ConversationTimeoutEvent,
    IntentRecognizedEvent,
)

from ._base import BaseProcessor


class IntentProcessor(BaseProcessor):
    """
    Implementation of the speech-to-intent processor using the Picovoice Rhino
    engine.
    """

    def __init__(
        self, *args, get_rhino_args: Callable[[], dict] = lambda: {}, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._get_rhino_args = get_rhino_args
        # model_path -> Rhino instance cache
        self._rhino = {}

    @property
    def _model_path(self) -> Optional[str]:
        return self._get_rhino_args().get('model_path')

    @property
    def sample_rate(self) -> int:
        return self._get_rhino().sample_rate

    @property
    def frame_length(self) -> int:
        return self._get_rhino().frame_length

    def _get_rhino(self) -> pvrhino.Rhino:
        if not self._rhino.get(self._model_path):
            self._rhino[self._model_path] = pvrhino.create(**self._get_rhino_args())

        return self._rhino[self._model_path]

    def process(
        self, audio: Sequence[int]
    ) -> Optional[Union[IntentRecognizedEvent, ConversationTimeoutEvent]]:
        """
        Process the audio and return an ``IntentRecognizedEvent`` if the intent was
        understood, or a ``ConversationTimeoutEvent`` if the conversation timed
        out, or ``None`` if the intent processing is not yet finalized.
        """
        event = None
        rhino = self._get_rhino()
        self._ctx.is_final = rhino.process(audio)

        if self._ctx.is_final:
            inference = rhino.get_inference()
            self.logger.debug(
                'Intent detection finalized. Inference understood: %s',
                inference.is_understood,
            )

            if inference.is_understood:
                event = IntentRecognizedEvent(
                    intent=inference.intent,
                    slots=dict(inference.slots),
                )

        if not event and self._ctx.timed_out:
            event = ConversationTimeoutEvent()

        return event

    def reset(self) -> None:
        if not self._enabled:
            return

        with self._state_lock:
            self._get_rhino().reset()
            super().reset()

    def stop(self):
        if not self._enabled:
            return

        super().stop()

        with self._state_lock:
            objs = self._rhino.copy()
            for key, obj in objs.items():
                obj.delete()
                self._rhino.pop(key)
