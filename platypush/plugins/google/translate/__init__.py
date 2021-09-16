import os
from typing import Optional, List

# noinspection PyPackageRequirements
from google.cloud import translate_v2 as translate

from platypush.message.response.translate import TranslateResponse
from platypush.plugins import action, Plugin


class GoogleTranslatePlugin(Plugin):
    """
    Plugin to interact with the Google Translate API.
    You'll need a Google Cloud active project and a set of credentials to use this plugin:

        1. Create a project on the `Google Cloud console <https://console.cloud.google.com/projectcreate>`_ if
           you don't have one already.

        2. In the menu navigate to the *Artificial Intelligence* section and select *Translations* and enable the API.

        3. From the menu select *APIs & Services* and create a service account. You can leave role and permissions
           empty.

        4. Create a new private JSON key for the service account and download it. By default platypush will look for the
           credentials file under ``~/.credentials/platypush/google/translate.json``.

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
        * **oauth2client** (``pip install oauth2client``)
        * **google-cloud-translate** (``pip install google-cloud-translate``)

    """

    _maximum_text_length = 2000
    default_credentials_file = os.path.join(os.path.expanduser('~'), '.credentials', 'platypush', 'google',
                                            'translate.json')

    def __init__(self, target_language: str = 'en', credentials_file: Optional[str] = None, **kwargs):
        """
        :param target_language: Default target language (default: 'en').
        :param credentials_file: Google service account JSON credentials file. If none is specified then the plugin will
            search for the credentials file in the following order:

            1. ``~/.credentials/platypush/google/translate.json``
            2. Context from the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable.
        """
        super().__init__(**kwargs)
        self.target_language = target_language
        self.credentials_file = None

        if credentials_file:
            self.credentials_file = os.path.abspath(os.path.expanduser(credentials_file))
        elif os.path.isfile(self.default_credentials_file):
            self.credentials_file = self.default_credentials_file

        if self.credentials_file:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_file

    @staticmethod
    def _nearest_delimiter_index(text: str, pos: int) -> int:
        for i in range(min(pos, len(text)-1), -1, -1):
            if text[i] in [' ', '\t', ',', '.', ')', '>']:
                return i
            elif text[i] in ['(', '<']:
                return i-1 if i > 0 else 0

        return 0

    @classmethod
    def _split_text(cls, text: str, length: int = _maximum_text_length) -> List[str]:
        parts = []

        while text:
            i = cls._nearest_delimiter_index(text, length)
            if i == 0:
                parts.append(text)
                text = ''
            else:
                part = text[:i+1]
                if part:
                    parts.append(part.strip())
                text = text[i+1:]

        return parts

    # noinspection PyShadowingBuiltins
    @action
    def translate(self, text: str, target_language: Optional[str] = None, source_language: Optional[str] = None,
                  format: Optional[str] = None) -> TranslateResponse:
        """
        Translate a piece of text or HTML.

        :param text: Input text.
        :param target_language: target_language override.
        :param source_language: source_language (default: auto-detect).
        :param format: Input format (available formats: ``text``, ``html``).
        :return: :class:`platypush.message.response.translate.TranslateResponse`.
        """
        target_language = target_language or self.target_language
        args = {}
        if target_language:
            args['target_language'] = target_language

        client = translate.Client(**args)
        if source_language:
            args['source_language'] = source_language

        inputs = self._split_text(text)
        result = {}

        for input in inputs:
            response = client.translate(input, format_=format, **args)
            if not result:
                result = response
            else:
                # noinspection PyTypeChecker
                result['translatedText'] += ' ' + response['translatedText']

        return TranslateResponse(
            translated_text=result.get('translatedText'),
            source_text=text,
            detected_source_language=result.get('detectedSourceLanguage'),
        )


# vim:sw=4:ts=4:et:
