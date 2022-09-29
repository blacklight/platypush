import json
import os
import pathlib
import requests
import time

from datetime import datetime, timedelta
from typing import Iterable, List, Optional
from urllib.parse import urljoin

from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.schemas.wallabag import WallabagEntrySchema


class WallabagPlugin(Plugin):
    """
    Plugin to interact with Wallabag (https://wallabag.it),
    an open-source alternative to Instapaper and Pocket.
    """

    _default_credentials_file = os.path.join(
        str(Config.get('workdir')), 'wallabag', 'credentials.json'
    )

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        server_url: str = 'https://wallabag.it',
        username: Optional[str] = None,
        password: Optional[str] = None,
        credentials_file: str = _default_credentials_file,
        **kwargs,
    ):
        """
        :param client_id: Client ID for your application - you can create one
            at ``<server_url>/developer``.
        :param client_secret: Client secret for your application - you can
            create one at ``<server_url>/developer``.
        :param server_url: Base URL of the Wallabag server (default: ``https://wallabag.it``).
        :param username: Wallabag username. Only needed for the first login,
            you can remove it afterwards. Alternatively, you can provide it
            on the :meth:`.login` method.
        :param password: Wallabag password. Only needed for the first login,
            you can remove it afterwards. Alternatively, you can provide it
            on the :meth:`.login` method.
        :param credentials_file: Path to the file where the OAuth session
            parameters will be stored (default:
            ``<WORKDIR>/wallabag/credentials.json``).
        """
        super().__init__(**kwargs)
        self._client_id = client_id
        self._client_secret = client_secret
        self._server_url = server_url
        self._username = username
        self._password = password
        self._credentials_file = os.path.expanduser(credentials_file)
        self._session = {}

    def _oauth_open_saved_session(self):
        try:
            with open(self._credentials_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.logger.warning('Could not load %s: %s', self._credentials_file, e)
            return

        self._session = {
            'username': data['username'],
            'client_id': data.get('client_id', self._client_id),
            'client_secret': data.get('client_secret', self._client_secret),
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
        }

        if data.get('expires_at') and time.time() > data['expires_at']:
            self.logger.info('OAuth token expired, refreshing it')
            self._oauth_refresh_token()

    def _oauth_refresh_token(self):
        url = urljoin(self._server_url, '/oauth/v2/token')
        rs = requests.post(
            url,
            json={
                'grant_type': 'refresh_token',
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'access_token': self._session['access_token'],
                'refresh_token': self._session['refresh_token'],
            },
        )

        rs.raise_for_status()
        rs = rs.json()
        self._session.update(
            {
                'access_token': rs['access_token'],
                'refresh_token': rs['refresh_token'],
                'expires_at': (
                    int(
                        (
                            datetime.now() + timedelta(seconds=rs['expires_in'])
                        ).timestamp()
                    )
                    if rs.get('expires_in')
                    else None
                ),
            }
        )

        self._oauth_flush_session()

    def _oauth_create_new_session(self, username: str, password: str):
        url = urljoin(self._server_url, '/oauth/v2/token')
        rs = requests.post(
            url,
            json={
                'grant_type': 'password',
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'username': username,
                'password': password,
            },
        )

        rs.raise_for_status()
        rs = rs.json()
        self._session = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'username': username,
            'access_token': rs['access_token'],
            'refresh_token': rs['refresh_token'],
            'expires_at': (
                int((datetime.now() + timedelta(seconds=rs['expires_in'])).timestamp())
                if rs.get('expires_in')
                else None
            ),
        }

        self._oauth_flush_session()

    def _oauth_flush_session(self):
        pathlib.Path(self._credentials_file).parent.mkdir(parents=True, exist_ok=True)

        pathlib.Path(self._credentials_file).touch(mode=0o600, exist_ok=True)
        with open(self._credentials_file, 'w') as f:
            f.write(json.dumps(self._session))

    @action
    def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Create a new user session if not logged in.

        :param username: Default ``username`` override.
        :param password: Default ``password`` override.
        """
        self._oauth_open_saved_session()
        if self._session:
            return

        username = username or self._username
        password = password or self._password
        assert (
            username and password
        ), 'No stored user session and no username/password provided'

        self._oauth_create_new_session(username, password)

    def _request(self, url: str, method: str, *args, as_json=True, **kwargs):
        url = urljoin(self._server_url, f'api/{url}')
        func = getattr(requests, method.lower())
        self.login()
        kwargs['headers'] = {
            **kwargs.get('headers', {}),
            'Authorization': f'Bearer {self._session["access_token"]}',
        }

        rs = func(url, *args, **kwargs)
        rs.raise_for_status()
        return rs.json() if as_json else rs.text

    @action
    def list(
        self,
        archived: bool = True,
        starred: bool = False,
        sort: str = 'created',
        descending: bool = False,
        page: int = 1,
        limit: int = 30,
        tags: Optional[Iterable[str]] = None,
        since: Optional[int] = None,
        full: bool = True,
    ) -> List[dict]:
        """
        List saved links.

        :param archived: Include archived items (default: ``True``).
        :param starred: Include only starred items (default: ``False``).
        :param sort: Timestamp sort criteria. Supported: ``created``,
            ``updated``, ``archived`` (default: ``created``).
        :param descending: Sort in descending order (default: ``False``).
        :param page: Results page to be retrieved (default: ``1``).
        :param limit: Maximum number of entries per page (default: ``30``).
        :param tags: Filter by a list of tags.
        :param since: Return entries created after this timestamp (as a UNIX
            timestamp).
        :param full: Include the full parsed body of the saved entry.
        :return: .. schema:: wallabag.WallabagEntrySchema(many=True)
        """
        rs = self._request(
            '/entries.json',
            method='get',
            params={
                'archived': int(archived),
                'starred': int(starred),
                'sort': sort,
                'order': 'desc' if descending else 'asc',
                'page': page,
                'perPage': limit,
                'tags': ','.join(tags or []),
                'since': since or 0,
                'detail': 'full' if full else 'metadata',
            },
        )

        return WallabagEntrySchema().dump(
            rs.get('_embedded', {}).get('items', []), many=True
        )

    @action
    def search(
        self,
        term: str,
        page: int = 1,
        limit: int = 30,
    ) -> List[dict]:
        """
        Search links by some text.

        :param term: Term to be searched.
        :param page: Results page to be retrieved (default: ``1``).
        :param limit: Maximum number of entries per page (default: ``30``).
        :return: .. schema:: wallabag.WallabagEntrySchema(many=True)
        """
        rs = self._request(
            '/search.json',
            method='get',
            params={
                'term': term,
                'page': page,
                'perPage': limit,
            },
        )

        return WallabagEntrySchema().dump(
            rs.get('_embedded', {}).get('items', []), many=True
        )

    @action
    def get(self, id: int) -> Optional[dict]:
        """
        Get the content and metadata of a link by ID.

        :param id: Entry ID.
        :return: .. schema:: wallabag.WallabagEntrySchema
        """
        rs = self._request(f'/entries/{id}.json', method='get')
        return WallabagEntrySchema().dump(rs)  # type: ignore

    @action
    def export(self, id: int, file: str, format: str = 'txt'):
        """
        Export a saved entry to a file in the specified format.

        :param id: Entry ID.
        :param file: Output filename.
        :param format: Output format. Supported: ``txt``, ``xml``, ``csv``,
            ``pdf``, ``epub`` and ``mobi`` (default: ``txt``).
        """
        rs = self._request(
            f'/entries/{id}/export.{format}', method='get', as_json=False
        )

        if isinstance(rs, str):
            rs = rs.encode()
        with open(os.path.expanduser(file), 'wb') as f:
            f.write(rs)

    @action
    def save(
        self,
        url: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        authors: Optional[Iterable[str]] = None,
        archived: bool = False,
        starred: bool = False,
        public: bool = False,
        language: Optional[str] = None,
        preview_picture: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Save a link to Wallabag.

        :param url: URL to be saved.
        :param title: Entry title (default: parsed from the page content).
        :param content: Entry content (default: parsed from the entry itself).
        :param tags: List of tags to attach to the entry.
        :param authors: List of authors of the entry (default: parsed from the
            page content).
        :param archived: Whether the entry should be created in the archive
            (default: ``False``).
        :param starred: Whether the entry should be starred (default:
            ``False``).
        :param public: Whether the entry should be publicly available. If so, a
            public URL will be generated (default: ``False``).
        :param language: Language of the entry.
        :param preview_picture: URL of a picture to be used for the preview
            (default: parsed from the page itself).
        :return: .. schema:: wallabag.WallabagEntrySchema
        """
        rs = self._request(
            '/entries.json',
            method='post',
            json={
                'url': url,
                'title': title,
                'content': content,
                'tags': ','.join(tags or []),
                'authors': ','.join(authors or []),
                'archive': int(archived),
                'starred': int(starred),
                'public': int(public),
                'language': language,
                'preview_picture': preview_picture,
            },
        )

        return WallabagEntrySchema().dump(rs)  # type: ignore

    @action
    def update(
        self,
        id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        authors: Optional[Iterable[str]] = None,
        archived: bool = False,
        starred: bool = False,
        public: bool = False,
        language: Optional[str] = None,
        preview_picture: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Update a link entry saved to Wallabag.

        :param id: Entry ID.
        :param title: New entry title.
        :param content: New entry content.
        :param tags: List of tags to attach to the entry.
        :param authors: List of authors of the entry.
        :param archived: Archive/unarchive the entry.
        :param starred: Star/unstar the entry.
        :param public: Mark the entry as public/private.
        :param language: Change the language of the entry.
        :param preview_picture: Change the preview picture URL.
        :return: .. schema:: wallabag.WallabagEntrySchema
        """
        rs = self._request(
            f'/entries/{id}.json',
            method='patch',
            json={
                'title': title,
                'content': content,
                'tags': ','.join(tags or []),
                'authors': ','.join(authors or []),
                'archive': int(archived),
                'starred': int(starred),
                'public': int(public),
                'language': language,
                'preview_picture': preview_picture,
            },
        )

        return WallabagEntrySchema().dump(rs)  # type: ignore

    @action
    def delete(self, id: int) -> Optional[dict]:
        """
        Delete an entry by ID.

        :param id: Entry ID.
        :return: .. schema:: wallabag.WallabagEntrySchema
        """
        rs = self._request(
            f'/entries/{id}.json',
            method='delete',
        )

        return WallabagEntrySchema().dump(rs)  # type: ignore
