import json
import os
import pathlib
import requests

from datetime import datetime
from urllib.parse import urljoin
from typing import Iterable, Optional

from platypush.config import Config
from platypush.context import Variable, get_bus
from platypush.message.event.music.tidal import TidalPlaylistUpdatedEvent
from platypush.plugins import RunnablePlugin, action


class MusicTidalPlugin(RunnablePlugin):
    """
    Plugin to interact with the user's Tidal account and library.

    Upon the first login, the application will prompt you with a link to
    connect to your Tidal account. Once authorized, you should no longer be
    required to explicitly login.

    Triggers:

        * :class:`platypush.message.event.music.TidalPlaylistUpdatedEvent`: when a user playlist
          is updated.

    Requires:

        * **tidalapi** (``pip install tidalapi``)

    """

    _base_url = 'https://api.tidalhifi.com/v1/'
    _default_credentials_file = os.path.join(
        str(Config.get('workdir')), 'tidal', 'credentials.json'
    )

    def __init__(
        self,
        quality: str = 'high',
        credentials_file: str = _default_credentials_file,
        **kwargs,
    ):
        """
        :param quality: Default audio quality. Default: ``high``.
            Supported: [``loseless``, ``master``, ``high``, ``low``].
        :param credentials_file: Path to the file where the OAuth session
        parameters will be stored (default:
            ``<WORKDIR>/tidal/credentials.json``).
        """
        from tidalapi import Quality

        super().__init__(**kwargs)
        self._credentials_file = credentials_file
        self._user_playlists = {}

        try:
            self._quality = getattr(Quality, quality.lower())
        except AttributeError:
            raise AssertionError(
                f'Invalid quality: {quality}. Supported values: '
                f'{[q.name for q in Quality]}'
            )

        self._session = None

    def _oauth_open_saved_session(self):
        if not self._session:
            return

        try:
            with open(self._credentials_file, 'r') as f:
                data = json.load(f)
                self._session.load_oauth_session(
                    data['token_type'], data['access_token'], data['refresh_token']
                )
        except Exception as e:
            self.logger.warning('Could not load %s: %s', self._credentials_file, e)

    def _oauth_create_new_session(self):
        if not self._session:
            return

        self._session.login_oauth_simple(function=self.logger.warning)  # type: ignore
        if self._session.check_login():
            data = {
                'token_type': self._session.token_type,
                'session_id': self._session.session_id,
                'access_token': self._session.access_token,
                'refresh_token': self._session.refresh_token,
            }

            pathlib.Path(os.path.dirname(self._credentials_file)).mkdir(
                parents=True, exist_ok=True
            )

            with open(self._credentials_file, 'w') as outfile:
                json.dump(data, outfile)

    @property
    def session(self):
        from tidalapi import Config, Session

        if self._session and self._session.check_login():
            return self._session

        # Attempt to reload the existing session from file
        self._session = Session(config=Config(quality=self._quality))
        self._oauth_open_saved_session()
        if not self._session.check_login():
            # Create a new session if we couldn't load an existing one
            self._oauth_create_new_session()

        assert self._session.check_login(), 'Could not connect to TIDAL'
        return self._session

    def _api_request(self, url, *args, method='get', **kwargs):
        method = getattr(requests, method.lower())
        url = urljoin(self._base_url, url)
        kwargs['headers'] = kwargs.get('headers', {})
        kwargs['params'] = kwargs.get('params', {})
        kwargs['params'].update(
            {
                'sessionId': self.session.session_id,
                'countryCode': self.session.country_code,
            }
        )

        rs = None
        kwargs['headers']['Authorization'] = '{type} {token}'.format(
            type=self.session.token_type, token=self.session.access_token
        )

        try:
            rs = method(url, *args, **kwargs)
            rs.raise_for_status()
            return rs
        except requests.HTTPError as e:
            if rs:
                self.logger.error(rs.text)
            raise e

    @action
    def create_playlist(self, name: str, description: Optional[str] = None):
        """
        Create a new playlist.

        :param name: Playlist name.
        :param description: Optional playlist description.
        """
        return self._api_request(
            url=f'users/{self.session.user.id}/playlists',
            method='post',
            data={
                'title': name,
                'description': description,
            },
        )

    @action
    def delete_playlist(self, playlist_id: str):
        """
        Delete a playlist by ID.

        :param playlist_id: ID of the playlist to delete.
        """
        self._api_request(url=f'playlists/{playlist_id}', method='delete')

    @action
    def add_to_playlist(self, playlist_id: str, track_ids: Iterable[str]):
        """
        Append one or more tracks to a playlist.

        :param playlist_id: Target playlist ID.
        :param track_ids: List of track IDs to append.
        """
        return self._api_request(
            url=f'playlists/{playlist_id}/items',
            method='post',
            headers={
                'If-None-Match': None,
            },
            data={
                'onArtifactNotFound': 'SKIP',
                'onDupes': 'SKIP',
                'trackIds': ','.join(map(str, track_ids)),
            },
        )

    def main(self):
        while not self.should_stop():
            playlists = self.session.user.playlists()  # type: ignore

            for pl in playlists:
                last_updated_var = Variable(f'TIDAL_PLAYLIST_LAST_UPDATE[{pl.id}]')
                prev_last_updated = last_updated_var.get()
                if prev_last_updated:
                    prev_last_updated = datetime.fromisoformat(prev_last_updated)
                    if pl.last_updated > prev_last_updated:
                        get_bus().post(TidalPlaylistUpdatedEvent(playlist_id=pl.id))

                if not prev_last_updated or pl.last_updated > prev_last_updated:
                    last_updated_var.set(pl.last_updated.isoformat())

            self.wait_stop(self.poll_interval)
