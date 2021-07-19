import json
import logging
import os
import pathlib
import re
from base64 import b64encode
from datetime import datetime, timedelta
from random import randint
from typing import Optional, Iterable
from urllib import parse

import requests

from platypush.config import Config
from platypush.context import get_backend
from platypush.exceptions import PlatypushException
from platypush.schemas.spotify import SpotifyTrackSchema
from platypush.utils import get_ip_or_hostname, get_redis


class MissingScopesException(PlatypushException):
    """
    Exception raised in case of insufficient access scopes for an API call.
    """
    def __init__(self, scopes: Optional[Iterable[str]] = None):
        super().__init__('Missing scopes for the required API call')
        self.scopes = scopes

    def __str__(self):
        return f'{self._msg}: {self.scopes}'


class SpotifyMixin:
    """
    This mixin provides a common interface to access the Spotify API.
    """

    spotify_auth_redis_prefix = 'platypush/music/spotify/auth'
    spotify_required_scopes = [
        'user-read-playback-state',
        'user-modify-playback-state',
        'user-read-currently-playing',
        'user-read-recently-played',
        'app-remote-control',
        'streaming',
        'playlist-modify-public',
        'playlist-modify-private',
        'playlist-read-private',
        'playlist-read-collaborative',
        'user-library-modify',
        'user-library-read',
    ]

    def __init__(self, *, client_id: Optional[str] = None, client_secret: Optional[str] = None, **kwargs):
        """
        :param client_id: Spotify client ID.
        :param client_secret: Spotify client secret.
        """
        self._spotify_data_dir = os.path.join(os.path.expanduser(Config.get('workdir')), 'spotify')
        self._spotify_credentials_file = os.path.join(self._spotify_data_dir, 'credentials.json')
        self._spotify_api_token: Optional[str] = None
        self._spotify_api_token_expires_at: Optional[datetime] = None
        self._spotify_user_token: Optional[str] = None
        self._spotify_user_token_expires_at: Optional[datetime] = None
        self._spotify_user_scopes = set()
        self._spotify_refresh_token: Optional[str] = None

        if not (client_id and client_secret) and Config.get('backend.music.spotify'):
            client_id, client_secret = (
                Config.get('backend.music.spotify').get('client_id'),
                Config.get('backend.music.spotify').get('client_secret'),
            )

        if not (client_id and client_secret) and Config.get('music.spotify'):
            client_id, client_secret = (
                Config.get('music.spotify').get('client_id'),
                Config.get('music.spotify').get('client_secret'),
            )

        self._spotify_api_credentials = (client_id, client_secret) if client_id and client_secret else ()
        self._spotify_logger = logging.getLogger(__name__)
        pathlib.Path(self._spotify_data_dir).mkdir(parents=True, exist_ok=True)

    def _spotify_assert_keys(self):
        assert self._spotify_api_credentials, \
            'No Spotify API credentials provided. ' + \
            'Please register an app on https://developers.spotify.com'

    def _spotify_authorization_header(self) -> dict:
        self._spotify_assert_keys()
        return {
            'Authorization': 'Basic ' + b64encode(
                    f'{self._spotify_api_credentials[0]}:{self._spotify_api_credentials[1]}'.encode()
                ).decode()
        }

    def _spotify_load_user_credentials(self, scopes: Optional[Iterable[str]] = None):
        if not os.path.isfile(self._spotify_credentials_file):
            return

        with open(self._spotify_credentials_file, 'r') as f:
            credentials = json.load(f)

        access_token, refresh_token, expires_at, saved_scopes = (
            credentials.get('access_token'),
            credentials.get('refresh_token'),
            credentials.get('expires_at'),
            set(credentials.get('scopes', [])),
        )

        self._spotify_refresh_token = refresh_token
        self._spotify_user_scopes = self._spotify_user_scopes.union(saved_scopes)

        if not expires_at:
            self._spotify_user_token = None
            self._spotify_user_token_expires_at = None
            return

        expires_at = datetime.fromisoformat(expires_at)
        if expires_at <= datetime.now():
            self._spotify_user_token = None
            self._spotify_user_token_expires_at = None
            return

        missing_scopes = [scope for scope in (scopes or []) if scope not in saved_scopes]
        if missing_scopes:
            self._spotify_user_token = None
            self._spotify_user_token_expires_at = None
            raise MissingScopesException(scopes=missing_scopes)

        self._spotify_user_token = access_token
        self._spotify_user_token_expires_at = expires_at

    def _spotify_save_user_credentials(self, access_token: str, refresh_token: str, expires_at: datetime,
                                       scopes: Optional[Iterable[str]] = None):
        self._spotify_user_token = access_token
        self._spotify_user_token_expires_at = expires_at
        self._spotify_refresh_token = refresh_token
        self._spotify_user_scopes = self._spotify_user_scopes.union(set(scopes or []))

        with open(self._spotify_credentials_file, 'w') as f:
            os.chmod(self._spotify_credentials_file, 0o600)
            json.dump({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': datetime.isoformat(expires_at),
                'scopes': list(self._spotify_user_scopes),
            }, f)

    def spotify_api_authenticate(self):
        """
        Authenticate to the Spotify API for requests that don't require access to user data.
        """
        if not (self._spotify_api_token or self._spotify_user_token):
            self._spotify_load_user_credentials()

        self._spotify_assert_keys()
        if (self._spotify_user_token and self._spotify_user_token_expires_at > datetime.now()) or \
                (self._spotify_api_token and self._spotify_api_token_expires_at > datetime.now()):
            # Already authenticated
            return

        rs = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                **self._spotify_authorization_header(),
            },
            data={
                'grant_type': 'client_credentials',
            }
        )

        rs.raise_for_status()
        rs = rs.json()
        self._spotify_api_token = rs.get('access_token')
        self._spotify_api_token_expires_at = datetime.now() + timedelta(seconds=rs.get('expires_in'))

    def spotify_user_authenticate(self, scopes: Optional[Iterable[str]] = None):
        """
        Authenticate to the Spotify API for requests that require access to user data.
        """
        if self._spotify_user_token:
            return

        try:
            self._spotify_load_user_credentials(scopes=scopes or self.spotify_required_scopes)
            if self._spotify_user_token:
                return

            if self._spotify_refresh_token:
                try:
                    self._spotify_refresh_user_token()
                    return
                except Exception as e:
                    self._spotify_logger.error(f'Unable to refresh the user access token: {e}')
        except MissingScopesException as e:
            self._spotify_logger.warning(e)

        http = get_backend('http')
        assert http, 'HTTP backend not configured'
        callback_url = '{scheme}://{host}:{port}/spotify/auth_callback'.format(
            scheme="https" if http.ssl_context else "http",
            host=get_ip_or_hostname(),
            port=http.port,
        )

        state = b64encode(bytes([randint(0, 255) for _ in range(18)])).decode()
        self._spotify_logger.warning('\n\nUnauthenticated Spotify session or scopes not provided by the user. Please '
                                     'open the following URL in a browser to authenticate:\n'
                                     'https://accounts.spotify.com/authorize?client_id='
                                     f'{self._spotify_api_credentials[0]}&'
                                     f'response_type=code&redirect_uri={parse.quote(callback_url, safe="")}'
                                     f'&scope={parse.quote(" ".join(scopes))}&state={state}.\n'
                                     'Replace the host in the callback URL with the IP/hostname of this machine '
                                     f'accessible to your browser if required, and make sure to add {callback_url} '
                                     'to the list of whitelisted callbacks on your Spotify application page.\n')

        redis = get_redis()
        msg = json.loads(redis.blpop(self.get_spotify_queue_for_state(state))[1].decode())
        assert not msg.get('error'), f'Authentication error: {msg["error"]}'
        self._spotify_user_authenticate_phase_2(code=msg['code'], callback_url=callback_url, scopes=scopes)

    def _spotify_user_authenticate_phase_2(self, code: str, callback_url: str, scopes: Iterable[str]):
        rs = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                **self._spotify_authorization_header(),
            },
            data={
                'code': code,
                'redirect_uri': callback_url,
                'grant_type': 'authorization_code',
            }
        )

        rs.raise_for_status()
        rs = rs.json()
        self._spotify_save_user_credentials(access_token=rs.get('access_token'),
                                            refresh_token=rs.get('refresh_token'),
                                            scopes=scopes,
                                            expires_at=datetime.now() + timedelta(seconds=rs['expires_in']))

    def _spotify_refresh_user_token(self):
        self._spotify_logger.debug('Refreshing user access token')
        rs = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                **self._spotify_authorization_header(),
            },
            data={
                'refresh_token': self._spotify_refresh_token,
                'grant_type': 'refresh_token',
            }
        )

        rs.raise_for_status()
        rs = rs.json()
        self._spotify_save_user_credentials(access_token=rs.get('access_token'),
                                            refresh_token=rs.get('refresh_token', self._spotify_refresh_token),
                                            expires_at=datetime.now() + timedelta(seconds=rs['expires_in']))

    @classmethod
    def get_spotify_queue_for_state(cls, state: str):
        return cls.spotify_auth_redis_prefix + '/' + state

    def spotify_user_call(self, url: str, method='get', scopes: Optional[Iterable[str]] = None, **kwargs) -> dict:
        """
        Shortcut for ``spotify_api_call`` that requires all the application scopes if none are passed.
        """
        return self.spotify_api_call(url, method=method, scopes=scopes or self.spotify_required_scopes, **kwargs)

    def spotify_api_call(self, url: str, method='get', scopes: Optional[Iterable[str]] = None, **kwargs) -> dict:
        """
        Send an API request to a Spotify endpoint.

        :param url: URL to be requested.
        :param method: HTTP method (default: ``get``).
        :param scopes: List of scopes required by the call.
        :param kwargs: Extra keyword arguments to be passed to the request.
        :return: The response payload.
        """
        if scopes:
            self.spotify_user_authenticate(scopes=scopes)
        else:
            self.spotify_api_authenticate()

        method = getattr(requests, method.lower())
        rs = method(
            f'https://api.spotify.com{url}',
            headers={
                'Authorization': f'Bearer {self._spotify_user_token or self._spotify_api_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            **kwargs
        )

        rs.raise_for_status()
        if rs.status_code != 204 and rs.text:
            return rs.json()

    def spotify_get_track(self, track_id: str):
        """
        Get information about a Spotify track ID.
        """
        if self._spotify_api_credentials:
            info = self.spotify_api_call(f'/v1/tracks/{track_id}')
        else:
            info = json.loads(
                [
                    re.match(r'^\s*Spotify.Entity\s*=\s*(.*);\s*$', line).group(1)
                    for line in requests.get(f'https://open.spotify.com/track/{track_id}').text.split('\n')
                    if 'Spotify.Entity' in line
                ].pop()
            )

        return SpotifyTrackSchema().dump({
            **info,
            'file': info['uri'],
            'time': info['duration_ms']/1000. if info.get('duration_ms') is not None else None,
            'artist': '; '.join([
                artist['name'] for artist in info.get('artists', [])
            ]),
            'album': info.get('album', {}).get('name'),
            'name': info.get('name'),
            'title': info.get('name'),
            'date': int(info.get('album', {}).get('release_date', '').split('-')[0]),
            'track': info.get('track_number'),
            'id': info['id'],
            'x-albumuri': info.get('album', {}).get('uri'),
        })

    # noinspection PyShadowingBuiltins
    def _spotify_paginate_results(self, url: str, limit: Optional[int] = None, offset: Optional[int] = None,
                                  type: Optional[str] = None, **kwargs) -> Iterable:
        results = []

        while url and (limit is None or len(results) < limit):
            url = parse.urlparse(url)
            kwargs['params'] = {
                **kwargs.get('params', {}),
                **({'limit': min(limit, 50)} if limit is not None else {}),
                **({'offset': offset} if offset is not None else {}),
                **parse.parse_qs(url.query),
            }

            page = self.spotify_user_call(url.path, **kwargs)
            if type:
                page = page.pop(type + 's')
            results.extend(page.pop('items', []) if isinstance(page, dict) else page)
            url = page.pop('next', None) if isinstance(page, dict) else None

        return results[:limit]
