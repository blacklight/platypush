import inspect
import os
import platform
import struct
import threading
from typing import Optional

from platypush.message.event.stt import SpeechStartedEvent

from platypush.context import get_bus
from platypush.message.response.stt import SpeechDetectedResponse
from platypush.plugins import action
from platypush.plugins.stt import SttPlugin


class SttPicovoiceSpeechPlugin(SttPlugin):
    """
    This plugin performs speech detection using `PicoVoice <https://github.com/Picovoice>`_.
    NOTE: The PicoVoice product used for real-time speech-to-text (Cheetah) can be used freely for
    personal applications on x86_64 Linux. Other architectures and operating systems require a commercial license.
    You can ask for a license `here <https://picovoice.ai/contact.html>`_.

    Requires:

        * **cheetah** (``pip install git+https://github.com/BlackLight/cheetah``)

    """

    def __init__(self,
                 library_path: Optional[str] = None,
                 acoustic_model_path: Optional[str] = None,
                 language_model_path: Optional[str] = None,
                 license_path: Optional[str] = None,
                 end_of_speech_timeout: int = 1,
                 *args, **kwargs):
        """
        :param library_path: Path to the Cheetah binary library for your OS
            (default: ``CHEETAH_INSTALL_DIR/lib/OS/ARCH/libpv_cheetah.EXT``).
        :param acoustic_model_path: Path to the acoustic speech model
            (default: ``CHEETAH_INSTALL_DIR/lib/common/acoustic_model.pv``).
        :param language_model_path:  Path to the language model
            (default: ``CHEETAH_INSTALL_DIR/lib/common/language_model.pv``).
        :param license_path: Path to your PicoVoice license
            (default: ``CHEETAH_INSTALL_DIR/resources/license/cheetah_eval_linux_public.lic``).
        :param end_of_speech_timeout: Number of seconds of silence during speech recognition before considering
            a phrase over (default: 1).
        """
        from pvcheetah import Cheetah
        super().__init__(*args, **kwargs)

        self._basedir = os.path.abspath(os.path.join(inspect.getfile(Cheetah), '..', '..', '..'))
        if not library_path:
            library_path = self._get_library_path()
        if not language_model_path:
            language_model_path = os.path.join(self._basedir, 'lib', 'common', 'language_model.pv')
        if not acoustic_model_path:
            acoustic_model_path = os.path.join(self._basedir, 'lib', 'common', 'acoustic_model.pv')
        if not license_path:
            license_path = os.path.join(self._basedir, 'resources', 'license', 'cheetah_eval_linux_public.lic')

        self._library_path = library_path
        self._language_model_path = language_model_path
        self._acoustic_model_path = acoustic_model_path
        self._license_path = license_path
        self._end_of_speech_timeout = end_of_speech_timeout
        self._stt_engine: Optional[Cheetah] = None
        self._speech_in_progress = threading.Event()

    def _get_library_path(self) -> str:
        path = os.path.join(self._basedir, 'lib', platform.system().lower(), platform.machine())
        return os.path.join(path, [f for f in os.listdir(path) if f.startswith('libpv_cheetah.')][0])

    def convert_frames(self, frames: bytes) -> tuple:
        assert self._stt_engine, 'The speech engine is not running'
        return struct.unpack_from("h" * self._stt_engine.frame_length, frames)

    def on_detection_ended(self) -> None:
        if self._stt_engine:
            self._stt_engine.delete()
        self._stt_engine = None

    def detect_speech(self, frames: tuple) -> str:
        text, is_endpoint = self._stt_engine.process(frames)
        text = text.strip()

        if text:
            if not self._speech_in_progress.is_set():
                self._speech_in_progress.set()
                get_bus().post(SpeechStartedEvent())

            self._current_text += ' ' + text.strip()

        if is_endpoint:
            text = self._stt_engine.flush().strip().strip()
            if text:
                self._current_text += ' ' + text

            self._speech_in_progress.clear()
            if self._current_text:
                self.on_speech_detected(self._current_text)

            self._current_text = ''

        return self._current_text

    def process_text(self, text: str) -> None:
        pass

    @action
    def detect(self, audio_file: str) -> SpeechDetectedResponse:
        """
        Perform speech-to-text analysis on an audio file.

        :param audio_file: Path to the audio file.
        """
        pass

    def recording_thread(self, input_device: Optional[str] = None, *args, **kwargs) -> None:
        assert self._stt_engine, 'The hotword engine has not yet been initialized'
        super().recording_thread(block_size=self._stt_engine.frame_length, input_device=input_device)

    @action
    def start_detection(self, *args, **kwargs) -> None:
        from pvcheetah import Cheetah
        self._stt_engine = Cheetah(
            library_path=self._library_path,
            acoustic_model_path=self._acoustic_model_path,
            language_model_path=self._language_model_path,
            license_path=self._license_path,
            endpoint_duration_sec=self._end_of_speech_timeout,
        )

        self.rate = self._stt_engine.sample_rate
        self._speech_in_progress.clear()
        super().start_detection(*args, **kwargs)


# vim:sw=4:ts=4:et:
