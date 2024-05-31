import logging
import os
import re
from threading import RLock
from typing import Optional

import numpy as np
import pvorca
import sounddevice as sd

from platypush.config import Config
from platypush.plugins import action
from platypush.plugins.tts import TtsPlugin


class TextConversionUtils:
    """
    Utility class to convert text to a format that is supported by the Orca TTS
    engine.

    This pre-processing step is necessary until the issue is fixed:
    https://github.com/Picovoice/orca/issues/10.
    """

    _logger = logging.getLogger(__name__)
    _number_re = re.compile(r'(([0-9]+\.[0-9]+)|([0-9]+\,[0-9]+)|([0-9]+))')
    _conversions_map = {
        (re.compile(r'\s*[(){}\[\]<>]'), ', '),
        (re.compile(r'[;]'), '.'),
        (re.compile(r'[@#]'), ' at '),
        (re.compile(r'[$]'), ' dollar '),
        (re.compile(r'[%]'), ' percent '),
        (re.compile(r'[&]'), ' and '),
        (re.compile(r'[+]'), ' plus '),
        (re.compile(r'[=]'), ' equals '),
        (re.compile(r'[|]'), ' or '),
        (re.compile(r'[~]'), ' tilde '),
        (re.compile(r'[`]'), ''),
        (re.compile(r'[*]'), ' star '),
        (re.compile(r'[\\/]'), ' slash '),
        (re.compile(r'[_]'), '  underscore '),
        # Anything that isn't a letter or supported punctuation is replaced with a space
        (re.compile(r'[^a-zA-Z,.:?!\-\'" ]'), ' '),
    }

    @classmethod
    def _convert_digits(cls, text: str) -> str:
        try:
            from num2words import num2words
        except ImportError:
            cls._logger.warning('num2words is not installed, skipping digit conversion')
            return text

        while match := cls._number_re.search(text):
            number = match.group(1)
            text = text.replace(number, num2words(float(number.replace(',', ''))))

        return text

    @classmethod
    def convert(cls, text: str) -> str:
        text = cls._convert_digits(text)

        for pattern, replacement in TextConversionUtils._conversions_map:
            text = pattern.sub(replacement, text)

        return text


class TtsPicovoicePlugin(TtsPlugin):
    """
    This TTS plugin enables you to render text as audio using `Picovoice
    <https://picovoice.ai>`_'s (still experimental) `Orca TTS engine
    <https://github.com/Picovoice/orca>`_.

    Take a look at
    :class:`platypush.plugins.assistant.picovoice.AssistantPicovoicePlugin`
    for details on how to sign up for a Picovoice account and get the API key.

    Also note that using the TTS features requires you to select Orca from the
    list of products available for your account on the `Picovoice console
    <https://console.picovoice.ai>`_.
    """

    def __init__(
        self,
        access_key: Optional[str] = None,
        model_path: Optional[str] = None,
        **kwargs,
    ):
        """
        :param access_key: Picovoice access key. If it's not specified here,
            then it must be specified on the configuration of
            :class:`platypush.plugins.assistant.picovoice.AssistantPicovoicePlugin`.
        :param model_path: Path of the TTS model file (default: use the default
            English model).
        """
        super().__init__(**kwargs)
        if not access_key:
            access_key = Config.get('assistant.picovoice', {}).get('access_key')
            assert (
                access_key
            ), 'No access key specified and no assistant.picovoice plugin found'

        self.model_path = model_path
        self.access_key = access_key
        if model_path:
            model_path = os.path.expanduser(model_path)

        self._stream: Optional[sd.OutputStream] = None
        self._stream_lock = RLock()

    def _play_audio(self, orca: pvorca.Orca, pcm: np.ndarray):
        with self._stream_lock:
            self.stop()
            self._stream = sd.OutputStream(
                samplerate=orca.sample_rate,
                channels=1,
                dtype='int16',
            )

        try:
            self._stream.start()
            self._stream.write(pcm)
        except Exception as e:
            self.logger.warning('Error playing audio: %s: %s', type(e), str(e))
        finally:
            try:
                self.stop()
                self._stream.close()
            except Exception as e:
                self.logger.warning(
                    'Error stopping audio stream: %s: %s', type(e), str(e)
                )
            finally:
                if self._stream:
                    self._stream = None

    def get_orca(self, model_path: Optional[str] = None):
        if not model_path:
            model_path = self.model_path
        if model_path:
            model_path = os.path.expanduser(model_path)

        return pvorca.create(access_key=self.access_key, model_path=model_path)

    @action
    def say(
        self,
        text: str,
        *_,
        output_file: Optional[str] = None,
        speech_rate: Optional[float] = None,
        model_path: Optional[str] = None,
        **__,
    ):
        """
        Say some text.

        :param text: Text to say.
        :param output_file: If set, save the audio to the specified file.
            Otherwise play it.
        :param speech_rate: Speech rate (default: None).
        :param model_path: Path of the TTS model file (default: use the default
            configured model).
        """
        # This is a temporary workaround until this issue is fixed:
        # https://github.com/Picovoice/orca/issues/10.
        text = TextConversionUtils.convert(text)
        orca = self.get_orca(model_path=model_path)

        if output_file:
            orca.synthesize_to_file(
                text, os.path.expanduser(output_file), speech_rate=speech_rate
            )
            return

        self._play_audio(
            orca=orca,
            pcm=np.array(
                orca.synthesize(text, speech_rate=speech_rate)[0],
                dtype='int16',
            ),
        )

    @action
    def stop(self):
        """
        Stop the currently playing audio.
        """
        with self._stream_lock:
            if not self._stream:
                return

            self._stream.stop()


# vim:sw=4:ts=4:et:
