import os
from typing import Optional

# noinspection PyPackageRequirements
from google.auth import jwt
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

        2. In the menu navigate to the _Artificial Intelligence_ section and select _Translations_ and enable the API.

        3. From the menu select _APIs & Services_ and create a service account. You can leave role and permissions
           empty.

        4. Create a new private JSON key for the service account and download it. By default platypush will look for the
           credentials file under ~/.credentials/platypush/google/translate.json.

    Requires:

        * **google-cloud-translate** (``pip install google-cloud-translate``)

    """

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

    def _get_credentials(self):
        if self.credentials_file:
            return jwt.Credentials.from_service_account_file(
                self.credentials_file)

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
        credentials = self._get_credentials()
        args = {}

        if target_language:
            args['target_language'] = target_language
        if credentials:
            args['credentials'] = credentials

        client = translate.Client(**args)

        if credentials:
            del args['credentials']
        if source_language:
            args['source_language'] = source_language

        result = client.translate(text, format_=format, **args)
        # noinspection PyUnresolvedReferences
        return TranslateResponse(
            translated_text=result.get('translatedText'),
            source_text=result.get('input'),
            detected_source_language=result.get('detectedSourceLanguage'),
        )


# vim:sw=4:ts=4:et:
