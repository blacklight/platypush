import json
import os
import requests

from platypush.config import Config
from platypush.message.response import Response
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.media import PlayerState


class MusicTidalPlugin(RunnablePlugin):
    """
    Plugin to interact with the user's Tidal account and library.

    Requires:

        * **tidalapi** (``pip install tidalapi``)

    """

    _base_url = 'https://api.tidalhifi.com/v1/'
    _default_credentials_file = os.path.join(
        str(Config.get('workdir')),
        'tidal', 'credentials.json'
    )

    def __init__(
        self,
        quality: str = 'high',
        credentials_file: str = _default_credentials_file,
        **kwargs
    ):
        """
        :param quality: Default audio quality. Default: ``high``.
            Supported: [``loseless``, ``master``, ``high``, ``low``].
        :param credentials_file: Path to the file where the OAuth session
        parameters will be stored (default:
            ``<WORKDIR>/tidal/credentials.json``).
        """
        from tidalapi import Quality

        super().__init__(self, **kwargs)
        self._credentials_file = credentials_file

        try:
            self._quality = getattr(Quality, quality.lower())
        except AttributeError:
            raise AssertionError(
                f'Invalid quality: {quality}. Supported values: '
                f'{[q.name for q in Quality]}'
            )

        self._session = None

    def _oauth_open_saved_session(self):
        try:
            with open(self._credentials_file, 'r') as f:
                data = json.load(f)
                self._session.load_oauth_session(
                    data['token_type'],
                    data['access_token'],
                    data['refresh_token']
                )
        except Exception as e:
            self.logger.warning('Could not load %s: %s', oauth_file, e)

    def _oauth_create_new_session(self):
        self._session.login_oauth_simple(function=self.logger.warning)
        if self._session.check_login():
            data = {
                'token_type': self._session.token_type,
                'session_id': self._session.session_id,
                'access_token': self._session.access_token,
                'refresh_token': self._session.refresh_token,
            }

            with open(oauth_file, 'w') as outfile:
                json.dump(data, outfile)

    @property
    def session(self):
        from tidalapi import Config, Session
        if self._session and self._session.check_login():
            return self._session

        # Attempt to reload the existing session from file
        # TODO populate Config object
        self._session = Session(config=Config())
        self._oauth_open_saved_session()
        if not self._session.check_login():
            # Create a new session if we couldn't load an existing one
            self._oauth_create_new_session()

        assert self._session.check_login(), 'Could not connect to TIDAL'
        return self._session

    def _api_request(self, url, *args, method='get', **kwargs):
        method = getattr(requests, method.lower())
        url = urljoin(base_url, url)
        kwargs['headers'] = kwargs.get('headers', {})
        kwargs['params'] = kwargs.get('params', {})
        kwargs['params'].update({
            'sessionId': self.session.session_id,
            'countryCode': self.session.country_code,
        })

        rs = None
        kwargs['headers']['Authorization'] = '{type} {token}'.format(
            type=self.session.token_type,
            token=self.session.access_token
        )

        try:
            rs = method(url, *args, **kwargs)
            rs.raise_for_status()
            return rs
        except requests.HTTPError as e:
            if rs:
                self.logger.error(rs.text)
            raise e

