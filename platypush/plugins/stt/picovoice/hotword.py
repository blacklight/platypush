import os
import struct
from typing import Optional, List

from platypush.message.response.stt import SpeechDetectedResponse
from platypush.plugins import action
from platypush.plugins.stt import SttPlugin


class SttPicovoiceHotwordPlugin(SttPlugin):
    """
    This plugin performs hotword detection using `PicoVoice <https://github.com/Picovoice>`_.

    Requires:

        * **pvporcupine** (``pip install pvporcupine``) for hotword detection.

    """

    def __init__(self,
                 library_path: Optional[str] = None,
                 model_file_path: Optional[str] = None,
                 keyword_file_paths: Optional[List[str]] = None,
                 sensitivity: float = 0.5,
                 sensitivities: Optional[List[float]] = None,
                 *args, **kwargs):
        from pvporcupine import Porcupine
        from pvporcupine.resources.util.python.util import LIBRARY_PATH, MODEL_FILE_PATH, KEYWORD_FILE_PATHS
        super().__init__(*args, **kwargs)

        self.hotwords = list(self.hotwords)
        self._hotword_engine: Optional[Porcupine] = None
        self._library_path = os.path.abspath(os.path.expanduser(library_path or LIBRARY_PATH))
        self._model_file_path = os.path.abspath(os.path.expanduser(model_file_path or MODEL_FILE_PATH))

        if not keyword_file_paths:
            hotwords = KEYWORD_FILE_PATHS
            assert all(hotword in hotwords for hotword in self.hotwords), \
                'Not all the hotwords could be found. Available hotwords: {}'.format(list(hotwords.keys()))

            self._keyword_file_paths = [os.path.abspath(os.path.expanduser(hotwords[hotword]))
                                        for hotword in self.hotwords]
        else:
            self._keyword_file_paths = [
                os.path.abspath(os.path.expanduser(p))
                for p in keyword_file_paths
            ]

        self._sensitivities = []
        if sensitivities:
            assert len(self._keyword_file_paths) == len(sensitivities), \
                'Please specify as many sensitivities as the number of configured hotwords'

            self._sensitivities = sensitivities
        else:
            self._sensitivities = [sensitivity] * len(self._keyword_file_paths)

    def convert_frames(self, frames: bytes) -> tuple:
        assert self._hotword_engine, 'The hotword engine is not running'
        return struct.unpack_from("h" * self._hotword_engine.frame_length, frames)

    def on_detection_ended(self) -> None:
        if self._hotword_engine:
            self._hotword_engine.delete()
        self._hotword_engine = None

    def detect_speech(self, frames: tuple) -> str:
        index = self._hotword_engine.process(frames)
        if index < 0:
            return ''

        if index is True:
            index = 0
        return self.hotwords[index]

    @action
    def detect(self, audio_file: str) -> SpeechDetectedResponse:
        """
        Perform speech-to-text analysis on an audio file.

        :param audio_file: Path to the audio file.
        """
        pass

    def recording_thread(self, input_device: Optional[str] = None, *args, **kwargs) -> None:
        assert self._hotword_engine, 'The hotword engine has not yet been initialized'
        super().recording_thread(block_size=self._hotword_engine.frame_length, input_device=input_device)

    @action
    def start_detection(self, *args, **kwargs) -> None:
        from pvporcupine import Porcupine
        self._hotword_engine = Porcupine(
            library_path=self._library_path,
            model_file_path=self._model_file_path,
            keyword_file_paths=self._keyword_file_paths,
            sensitivities=self._sensitivities)

        self.rate = self._hotword_engine.sample_rate
        super().start_detection(*args, **kwargs)


# vim:sw=4:ts=4:et:
