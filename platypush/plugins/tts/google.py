import os
import subprocess
import tempfile
from typing import Optional, List

from platypush.plugins import action
from platypush.plugins.tts import TtsPlugin


class TtsGooglePlugin(TtsPlugin):
    """
    Advanced text-to-speech engine that leverages the Google Cloud TTS API.
    See https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python
    for how to enable the API on your account and get your credentials.

    Requires:

        * **google-cloud-texttospeech** - ``pip install google-cloud-texttospeech``
        * **mplayer** - see your distribution docs on how to install the mplayer package
    """

    def __init__(self,
                 language: str ='en-US',
                 voice: Optional[str] = None,
                 gender: str = 'FEMALE',
                 credentials_file: str = '~/.credentials/platypush/google/platypush-tts.json',
                 player_args: Optional[List[str]] = None):
        """
        :param language: Language code, see https://cloud.google.com/text-to-speech/docs/basics for supported languages
        :param voice: Voice type, see https://cloud.google.com/text-to-speech/docs/basics for supported voices
        :param gender: Voice gender (MALE, FEMALE or NEUTRAL)
        :param credentials_file: Where your GCloud credentials for TTS are stored, see https://cloud.google.com/text-to-speech/docs/basics
        :param player_args: Extra options to be passed to the audio player (default: ``mplayer``).
        """
        from google.cloud import texttospeech
        super().__init__()

        self.language = language
        self.voice = voice
        self.player_args = player_args or []

        self.language = self._parse_language(language)
        self.voice = self._parse_voice(self.language, voice)
        self.gender = getattr(texttospeech.enums.SsmlVoiceGender, gender.upper())
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

    @action
    def say(self,
            text: str,
            language: Optional[str] = None,
            voice: Optional[str] = None,
            gender: Optional[str] = None,
            player_args: Optional[List[str]] = None):
        """
        Say a phrase.

        :param text: Text to say.
        :param language: Language code override.
        :param voice: Voice type override.
        :param gender: Gender override.
        :param player_args: Player args override.
        """

        from google.cloud import texttospeech
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.types.SynthesisInput(text=text)

        language = self._parse_language(language)
        voice = self._parse_voice(language, voice)

        if gender is None:
            gender = self.gender
        else:
            gender = getattr(texttospeech.enums.SsmlVoiceGender, gender.upper())

        player_args = player_args or self.player_args
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=language, ssml_gender=gender,
            name=voice)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(synthesis_input, voice, audio_config)

        with tempfile.NamedTemporaryFile() as f:
            f.write(response.audio_content)
            cmd = ['mplayer -ao alsa -really-quiet -noconsolecontrols {} "{}"'.format(
                ' '.join(player_args), f.name)]

            try:
                return subprocess.check_output(
                    cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
            except subprocess.CalledProcessError as e:
                raise RuntimeError(e.output.decode('utf-8'))


# vim:sw=4:ts=4:et:
