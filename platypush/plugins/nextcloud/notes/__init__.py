import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urljoin, urlparse

import dateutil.parser
import requests

from platypush.common.notes import Note, NoteCollection
from platypush.config import Config
from platypush.plugins.notes import ApiSettings, BaseNotePlugin, Results
from platypush.utils import utcnow


@dataclass(kw_only=True)
class Settings:
    """
    Plugin settings for Nextcloud Notes.
    """

    notes_path: str = 'Notes'
    file_suffix: str = '.md'


class NextcloudNotesPlugin(BaseNotePlugin):
    r"""
    Plugin to interact with `Nextcloud Notes
    <https://apps.nextcloud.com/apps/notes>`_,
    """

    _api_settings = ApiSettings(
        supports_notes_limit=True,
        supports_notes_offset=False,
        supports_collections_limit=False,
        supports_collections_offset=False,
        supports_search_limit=False,
        supports_search_offset=False,
        supports_search=False,
    )

    def __init__(
        self,
        *args,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
        """
        If the :class:`platypush.plugins.nextcloud.NextcloudPlugin` is
        installed and configured, and you intend to use the same instance, then
        you can skip this configuration.

        :param url: The URL of the Nextcloud instance (e.g.,
            `https://nextcloud.example.com`).
        :param username: The username to authenticate with.
        :param password: The password to authenticate with. It is advised to
            use a dedicated app password instead of your main account password
            (this is actually a requirement if you have enabled 2FA).
        """
        super().__init__(*args, **kwargs)
        nc_config = Config.get('nextcloud') or {}
        self.url = url or nc_config.get('url', '')
        self.username = username or nc_config.get('username', '')
        self.password = password or nc_config.get('password', '')

        assert (
            self.url
        ), 'Nextcloud URL is required, either in this plugin or in the Nextcloud plugin configuration'

        assert (
            self.username
        ), 'Nextcloud username is required, either in this plugin or in the Nextcloud plugin configuration'

        assert (
            self.password
        ), 'Nextcloud password is required, either in this plugin or in the Nextcloud plugin configuration'

        self.settings = self._get_settings()

    def _get_settings(self) -> Settings:
        settings = Settings()

        try:
            response = self._api_exec('GET', 'settings').json()
            settings.notes_path = response.get('notesPath', settings.notes_path)
            settings.file_suffix = response.get('fileSuffix', settings.file_suffix)
        except requests.RequestException:
            # Notes API versions <1.2 don't have the settings endpoint.
            # Use default settings in that case.
            ...

        return settings

    def _api_url(self, path: str = '') -> str:
        return '/'.join(
            [
                self.url.rstrip('/'),
                f'index.php/apps/notes/api/v1/{path.lstrip("/")}'.rstrip('/'),
            ]
        )

    @property
    def _webdav_path(self):
        """
        Base WebDAV path for the notes folder in Nextcloud.
        """
        url = urlparse(self.url)
        return '/'.join(
            [
                url.path.rstrip('/'),
                f'remote.php/dav/files/{self.username}/{self.settings.notes_path}/',
            ]
        )

    @property
    def _webdav_url(self):
        """
        Base WebDAV URL for the notes folder in Nextcloud.
        """
        return '/'.join(
            [
                self.url.rstrip('/'),
                f'remote.php/dav/files/{self.username}/{self.settings.notes_path}/',
            ]
        )

    def _api_exec(
        self,
        method: str,
        path: str = '',
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Execute a request to the Nextcloud Notes API.
        """
        url = self._api_url(path)
        auth = kwargs.pop('auth', (self.username, self.password))
        self.logger.debug(
            'Calling Nextcloud Notes API: %s %s with params: %s',
            method,
            url,
            params,
        )

        response = requests.request(
            method, url, params=params, auth=auth, timeout=self._timeout, **kwargs
        )

        try:
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(
                'Failed to execute request %s %s: status=%s, error=%s, body=%s',
                method,
                url,
                response.status_code if response else 'N/A',
                e,
                response.text if response else 'N/A',
            )
            raise RuntimeError(f'Failed to execute request {method} {url}: {e}') from e

        return response

    def _to_note(self, data: dict) -> Note:
        dt = datetime.fromtimestamp(data['modified']) if data.get('modified') else None
        return Note(
            **{
                'id': str(data.get('id', '')),
                'plugin': self._plugin_name,
                'title': data.get('title', ''),
                'content': data.get('content'),
                'parent': (
                    self._to_collection(data['category'])
                    if data.get('category')
                    else None
                ),
                # No creation time in the API, so we set it to epoch
                'created_at': datetime.fromtimestamp(0),
                'updated_at': dt,
            }
        )

    def _to_collection(self, title: str) -> NoteCollection:
        return NoteCollection(
            id=title,
            plugin=self._plugin_name,
            title=title,
        )

    def _fetch_note(self, note_id: Any, *_, **__) -> Optional[Note]:
        response = self._api_exec('GET', f'notes/{note_id}')
        return self._to_note(response.json())  # type: ignore[return-value]

    def _fetch_notes(self, *_, limit: Optional[int] = None, **__) -> List[Note]:
        """
        Fetch notes from the Nextcloud Notes API.
        """
        return [
            self._to_note(note)
            for note in (
                self._api_exec(
                    'GET',
                    'notes',
                    params={
                        'exclude': 'content',
                        'chunkSize': limit or 10000,
                        # TODO Support chunkCursor
                    },
                ).json()
                or {}
            )
        ]

    def _create_note(
        self,
        title: str,
        content: str,
        *_,
        parent: Optional[Any] = None,
        **__,
    ) -> Note:
        response = self._api_exec(
            'POST',
            'notes',
            json={
                'title': title,
                'category': parent,
                'content': content,
            },
        )

        return self._to_note(response.json())

    def _edit_note(
        self,
        note_id: Any,
        *_,
        title: Optional[str] = None,
        content: Optional[str] = None,
        parent: Optional[Any] = None,
        **__,
    ) -> Note:
        data = {}

        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        if parent is not None:
            data['category'] = parent

        response = self._api_exec('PUT', f'notes/{note_id}', json=data)
        return self._to_note(response.json())

    def _delete_note(self, note_id: Any, *_, **__):
        self._api_exec('DELETE', f'notes/{note_id}')

    def _fetch_collections(self, *_, **__) -> List[NoteCollection]:
        """
        Retrieve the collections in the Notes folder using WebDAV.
        """
        response = requests.request(
            method='PROPFIND',
            url=self._webdav_url,
            auth=(self.username, self.password),
            timeout=self._timeout,
            headers={
                'Content-Type': 'application/xml; charset="utf-8"',
                'Depth': '100',
            },
        )

        response.raise_for_status()
        tree = ET.fromstring(response.content)
        namespaces = {'d': 'DAV:'}
        responses = tree.findall('.//d:response', namespaces)
        collections = []

        for resp in responses:
            href_elem = resp.find('d:href', namespaces)
            if href_elem is None or not href_elem.text:
                continue

            href = str(href_elem.text.strip('/'))
            collection_id = re.sub(
                fr'^{re.escape(self._webdav_path).strip("/")}', '', href
            ).strip('/')
            collection_id = collection_id.rstrip(self.settings.file_suffix)

            props = resp.find('d:propstat/d:prop', namespaces)
            if props is None:
                continue

            is_collection = (
                props.find('d:resourcetype/d:collection', namespaces) is not None
            )

            last_modified_elem = props.find('d:getlastmodified', namespaces)
            last_modified = utcnow()
            if last_modified_elem is not None and last_modified_elem.text:
                last_modified = dateutil.parser.parse(last_modified_elem.text)

            if not is_collection:
                continue

            collections.append(
                NoteCollection(
                    id=collection_id,
                    plugin=self._plugin_name,
                    title=collection_id,
                    # WebDAV doesn't provide the creation time, so we set it to epoch
                    created_at=datetime.fromtimestamp(0),
                    updated_at=last_modified,
                )
            )

        return collections

    def _fetch_collection(
        self, collection_id: Any, *_, **__
    ) -> Optional[NoteCollection]:
        """
        Fetch a collection (folder) by its ID.

        Note that the Nextcloud API does not provide a direct way to fetch
        collections. Instead, we use the WebDAV API to list the contents of
        the Notes folder.
        """
        return next(
            (
                collection
                for collection in self._fetch_collections()
                if collection.id == collection_id
            ),
            None,
        )

    def _create_collection(
        self,
        title: str,
        *_,
        parent: Optional[Any] = None,
        **__,
    ) -> NoteCollection:
        """
        This uses the WebDAV API to create a new collection (folder) in the Notes folder.
        """
        collection_id = '/'.join(
            [
                (parent or '').rstrip('/'),
                title.strip('/'),
            ]
        ).strip('/')

        response = requests.request(
            method='MKCOL',
            url=urljoin(self._webdav_url, collection_id),
            auth=(self.username, self.password),
            headers={'Content-Type': 'application/xml; charset="utf-8"'},
            timeout=self._timeout,
        )

        response.raise_for_status()
        return NoteCollection(
            id=collection_id,
            plugin=self._plugin_name,
            title=collection_id,
            created_at=utcnow(),
            updated_at=utcnow(),
        )

    def _edit_collection(
        self,
        collection_id: Any,
        *_,
        title: Optional[str] = None,
        parent: Optional[Any] = None,
        **__,
    ) -> NoteCollection:
        """
        Change a directory name using the WebDAV API.
        """
        if title is None:
            raise ValueError('Title is required to edit a collection')

        src_path = collection_id.strip('/')
        dest_path = '/'.join(
            [
                parent.rstrip('/') if parent else '',
                title.strip('/'),
            ]
        ).strip('/')

        webdav_url = self._webdav_url.rstrip('/')
        src_url = '/'.join([webdav_url, src_path.strip('/')])
        dest_url = '/'.join(
            [
                webdav_url,
                *[quote(part) for part in dest_path.split('/') if part],
            ]
        )

        self.logger.debug('Moving collection "%s" to "%s"', src_url, dest_url)

        response = requests.request(
            method='MOVE',
            url=src_url,
            auth=(self.username, self.password),
            headers={
                'Destination': dest_url,
                'Overwrite': 'T',
            },
            timeout=self._timeout,
        )

        response.raise_for_status()
        return NoteCollection(
            id=src_path,
            plugin=self._plugin_name,
            title=src_path,
            created_at=datetime.fromtimestamp(0),  # No creation time in WebDAV
            updated_at=utcnow(),
        )

    def _delete_collection(self, collection_id: Any, *_: Any, **__: Any):
        """
        Delete a collection (folder) by its ID.

        This uses the WebDAV API to delete the folder in the Notes folder.
        """
        url = '/'.join(
            [
                self._webdav_url.rstrip('/'),
                collection_id.strip('/'),
            ]
        )

        response = requests.request(
            method='DELETE',
            url=url,
            auth=(self.username, self.password),
            timeout=self._timeout,
        )

        response.raise_for_status()
        self.logger.info('Deleted collection: %s', collection_id)

    def _search(self, *_, **__) -> Results:
        """
        Search is not implemented in the Nextcloud Notes API.

        Fallback on the internal database search instead.
        """
        raise NotImplementedError(
            'Search is not implemented in the Nextcloud Notes API. '
            'Fallback on the internal database search instead.'
        )


# vim:sw=4:ts=4:et:
