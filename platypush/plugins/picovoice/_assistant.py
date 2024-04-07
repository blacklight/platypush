import logging
import os
from threading import Event
from time import time
from typing import Any, Dict, Optional, Sequence

import pvcheetah
import pvleopard
import pvporcupine
import pvrhino

from platypush.message.event.assistant import HotwordDetectedEvent

from ._recorder import AudioRecorder


class Assistant:
    """
    A facade class that wraps the Picovoice engines under an assistant API.
    """

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
    ):
        self.logger = logging.getLogger(__name__)
        self._access_key = access_key
        self._stop_event = stop_event
        self.hotword_enabled = hotword_enabled
        self.stt_enabled = stt_enabled
        self.intent_enabled = intent_enabled
        self.keywords = list(keywords or [])
        self.keyword_paths = None
        self.keyword_model_path = None
        self.frame_expiration = frame_expiration
        self._recorder = None

        if hotword_enabled:
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

    def _create_porcupine(self):
        if not self.hotword_enabled:
            return None

        args: Dict[str, Any] = {'access_key': self._access_key}
        if not (self.keywords or self.keyword_paths):
            raise ValueError(
                'You need to provide either a list of keywords or a list of '
                'keyword paths if the wake-word engine is enabled'
            )

        if self.keywords:
            args['keywords'] = self.keywords
        if self.keyword_paths:
            args['keyword_paths'] = self.keyword_paths
        if self.keyword_model_path:
            args['model_path'] = self.keyword_model_path

        return pvporcupine.create(**args)

    @property
    def porcupine(self) -> Optional[pvporcupine.Porcupine]:
        if not self._porcupine:
            self._porcupine = self._create_porcupine()

        return self._porcupine

    def __enter__(self):
        if self._recorder:
            self.logger.info('A recording stream already exists')
        elif self.porcupine:
            self._recorder = AudioRecorder(
                stop_event=self._stop_event,
                sample_rate=self.porcupine.sample_rate,
                frame_size=self.porcupine.frame_length,
                channels=1,
            )

            self._recorder.__enter__()

        return self

    def __exit__(self, *_):
        if self._recorder:
            self._recorder.__exit__(*_)
            self._recorder = None

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
            if self.porcupine:  # TODO also check current state
                data = self._recorder.read()
                if data is None:
                    continue

                frame, t = data
                if time() - t > self.frame_expiration:
                    self.logger.info(
                        'Skipping audio frame older than %ss', self.frame_expiration
                    )
                    continue  # The audio frame is too old

                keyword_index = self.porcupine.process(frame)
                if keyword_index is None:
                    continue  # No keyword detected

                if keyword_index >= 0 and self.keywords:
                    return HotwordDetectedEvent(hotword=self.keywords[keyword_index])

        raise StopIteration


# vim:sw=4:ts=4:et:
