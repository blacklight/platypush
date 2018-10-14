import os
import subprocess
import tempfile

from google.cloud import texttospeech

from platypush.plugins import Plugin, action

class TtsGooglePlugin(Plugin):
    """
    Advanced text-to-speech engine that leverages the Google Cloud TTS API.
    See https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python
    for how to enable the API on your account and get your credentials.

    Requires:

        * **google-cloud-texttospeech** - ``pip install google-cloud-texttospeech``
        * **mplayer** - see your distribution docs on how to install the mplayer package
    """

    def __init__(self, language='en-US', voice='en-US-Wavenet-C',
                 gender='FEMALE', credentials_file='~/.credentials/platypush/google/platypush-tts.json'):
        """
        :param language: Language code, see https://cloud.google.com/text-to-speech/docs/basics for supported languages
        :type language: str

        :param voice: Voice type, see https://cloud.google.com/text-to-speech/docs/basics for supported voices
        :type voice: str

        :param gender: Voice gender (MALE, FEMALE or NEUTRAL)
        :type gender: str

        :param credentials_file: Where your GCloud credentials for TTS are stored, see https://cloud.google.com/text-to-speech/docs/basics
        :type credentials_file: str
        """

        super().__init__()
        self.language = language
        self.voice = voice
        self.gender = getattr(texttospeech.enums.SsmlVoiceGender, gender.upper())
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser(credentials_file)

    @action
    def say(self, text, language=None, voice=None, gender=None):
        """
        Say a phrase

        :param text: Text to say
        :type text: str

        :param language: Language code override
        :type language: str

        :param voice: Voice type override
        :type voice: str

        :param gender: Gender override
        :type gender: str
        """

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.types.SynthesisInput(text=text)

        if language is None:
            language = self.language

        if gender is None:
            gender = self.gender
        else:
            gender = getattr(texttospeech.enums.SsmlVoiceGender, gender.upper())

        if voice is None:
            voice = self.voice

        voice = texttospeech.types.VoiceSelectionParams(
            language_code=language, ssml_gender=gender,
            name=voice)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(synthesis_input, voice, audio_config)

        with tempfile.NamedTemporaryFile() as f:
            f.write(response.audio_content)

            output = None
            errors = []
            cmd = ['mplayer -ao alsa -really-quiet -noconsolecontrols {}'
                   .format(f.name)]

            try:
                return subprocess.check_output(
                    cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
            except subprocess.CalledProcessError as e:
                raise RuntimeError(e.output.decode('utf-8'))


# vim:sw=4:ts=4:et:

