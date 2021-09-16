import os
import tempfile
from typing import Optional

from platypush.plugins import action
from platypush.plugins.tts import TtsPlugin


class TtsGooglePlugin(TtsPlugin):
    """
    Advanced text-to-speech engine that leverages the Google Cloud TTS API.
    See https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python
    for how to enable the API on your account and get your credentials.

    Requires:

        * **google-cloud-texttospeech** (``pip install google-cloud-texttospeech``)

    """

    def __init__(self,
                 language: str = 'en-US',
                 voice: Optional[str] = None,
                 gender: str = 'FEMALE',
                 credentials_file: str = '~/.credentials/platypush/google/platypush-tts.json',
                 **kwargs):
        """
        :param language: Language code, see https://cloud.google.com/text-to-speech/docs/basics for supported languages
        :param voice: Voice type, see https://cloud.google.com/text-to-speech/docs/basics for supported voices
        :param gender: Voice gender (MALE, FEMALE or NEUTRAL)
        :param credentials_file: Where your GCloud credentials for TTS are stored, see https://cloud.google.com/text-to-speech/docs/basics
        :param kwargs: Extra arguments to be passed to the :class:`platypush.plugins.tts.TtsPlugin` constructor.
        """
        super().__init__(**kwargs)

        self.language = language
        self.voice = voice
        self.language = self._parse_language(language)
        self.voice = self._parse_voice(self.language, voice)
        self.gender = getattr(self._gender, gender.upper())
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser(credentials_file)

    def _parse_language(self, language):
        if language is None:
            language = self.language or 'en-US'

        if len(language) == 2:
            language = language.lower()
            if language == 'en':
                language = 'en-US'
            else:
                language += '-' + language.upper()

        return language

    @staticmethod
    def _parse_voice(language, voice):
        if voice is not None:
            return voice

        if language == 'en-US':
            return language + '-Wavenet-C'
        return language + '-Wavenet-A'

    @property
    def _gender(self):
        from google.cloud import texttospeech
        return texttospeech.enums.SsmlVoiceGender if hasattr(texttospeech, 'enums') else \
            texttospeech.SsmlVoiceGender

    @property
    def _voice_selection_params(self):
        from google.cloud import texttospeech
        return texttospeech.types.VoiceSelectionParams if hasattr(texttospeech, 'types') else \
            texttospeech.VoiceSelectionParams

    @property
    def _synthesis_input(self):
        from google.cloud import texttospeech
        return texttospeech.types.SynthesisInput if hasattr(texttospeech, 'types') else \
            texttospeech.SynthesisInput

    @property
    def _audio_config(self):
        from google.cloud import texttospeech
        return texttospeech.types.AudioConfig if hasattr(texttospeech, 'types') else \
            texttospeech.AudioConfig

    @property
    def _audio_encoding(self):
        from google.cloud import texttospeech
        return texttospeech.enums.AudioEncoding if hasattr(texttospeech, 'enums') else \
            texttospeech.AudioEncoding

    @action
    def say(self,
            text: str,
            language: Optional[str] = None,
            voice: Optional[str] = None,
            gender: Optional[str] = None,
            player_args: Optional[dict] = None):
        """
        Say a phrase.

        :param text: Text to say.
        :param language: Language code override.
        :param voice: Voice type override.
        :param gender: Gender override.
        :param player_args: Optional arguments that should be passed to the player plugin's
            :meth:`platypush.plugins.media.MediaPlugin.play` method.
        """

        from google.cloud import texttospeech
        client = texttospeech.TextToSpeechClient()
        # noinspection PyTypeChecker
        synthesis_input = self._synthesis_input(text=text)

        language = self._parse_language(language)
        voice = self._parse_voice(language, voice)

        if gender is None:
            gender = self.gender
        else:
            gender = getattr(self._gender, gender.upper())

        voice = self._voice_selection_params(language_code=language, ssml_gender=gender, name=voice)
        # noinspection PyTypeChecker
        audio_config = self._audio_config(audio_encoding=self._audio_encoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        player_args = player_args or {}

        with tempfile.NamedTemporaryFile() as f:
            f.write(response.audio_content)
            self.media_plugin.play(f.name, **player_args)


# vim:sw=4:ts=4:et:
