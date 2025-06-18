import datetime
from typing import Any, List, Optional
from urllib.parse import urljoin

import requests

from platypush.common.notes import Note, NoteCollection, NoteSource
from platypush.plugins._notes import BaseNotePlugin


class JoplinPlugin(BaseNotePlugin):
    r"""
    Plugin to interact with `Joplin <https://joplinapp.org/>`_, a free and
    open-source note-taking application.

    ## Advised setup

    Joplin is mainly intended as a desktop application, with support for
    synchronization across multiple devices via various backends.

    This plugin is designed to interact with the Joplin API exposed by the
    "desktop" application - the same one used by the `Joplin Web Clipper
    extension <https://joplinapp.org/clipper/>`_.

    This can be achieved in two ways:

        1. Using the Joplin desktop application
        2. Using Joplin in headless mode

    ### Using the Joplin desktop application

    To use the Joplin desktop application, you need to enable the Web Clipper
    service in the Joplin settings. This will expose an HTTP API on the port
    41184 on your local machine.

    Note that the Joplin desktop application must be running for this plugin to
    work, and by default it will only accept requests from the local machine.

    If you want to run the Platypush server on a different machine, you can
    e.g. open an SSH tunnel to the Joplin machine:

        .. code-block:: bash
            ssh -L 41184:localhost:41184 user@joplin-machine

    ### Using Joplin in headless mode

    The downside of the Joplin desktop application is that it must be running
    on a live desktop session for the plugin to work. Unfortunately, Joplin
    does not provide an official headless mode, but there is `a community
    project <https://github.com/jspiers/headless-joplin>`_ that allows you to
    run Joplin in a Docker container in headless mode, exposing the same HTTP
    API as the desktop application.

    It's first advised to run and configure your Joplin on the desktop app.
    Then locate the Joplin profile directory (usually
    ``~/.config/joplin-desktop`` on Linux, but depending on the installed
    version it could also be named ``Joplin`` or ``joplin``) and copy the
    file named ``settings.json`` to ``~/.config/joplin/settings.json`` on the
    machine where you run the headless Joplin container.

    Optionally, you can also copy the ``database.sqlite`` file from the
    desktop Joplin profile directory to the headless Joplin profile, but make
    sure that the desktop instance and the headless instance run the same
    version of Joplin, otherwise you might run into database incompatibility
    issues.

    #### Credentials

    If you opt not to copy the database file to the headless Joplin profile,
    then you may have to manually set up the credentials in a separate file
    named ``secrets.json`` in the Joplin profile directory. This will contain
    both the API token and the passwords for any connected synchronization
    services. For example:

        .. code-block:: json

            {
                "api.token": "your_api_token_here",
                "sync.1.password": "your_sync_password_here"
            }

    Note:

        1. The ``api.token`` field is mandatory, and it should match the one
           you configure in this plugin.

        2. ``sync.<n>.password`` should be such that ``<n>`` is the index of
           the synchronization target configured in ``settings.json`` (e.g.
           Dropbox, Nextcloud, S3, Joplin Cloud, a local Joplin server, etc.).

    #### Running the service

        .. code-block:: bash

            docker run --rm \
                --name joplin-headless \
                -v ~/.config/joplin:/home/node/.config/joplin \
                -v ~/.config/joplin/secrets.json:/run/secrets/joplin-config.json:ro \
                -p 41184:80 \
                jspiers/headless-joplin:2.13.2-node-20.11.1

    #### Synchronization

    Unlike the Joplin desktop application, the headless Joplin instance does
    not provide a periodic synchronization mechanism. But you can schedule a
    cronjob to periodically run synchronization each e.g. 5 minutes:

        .. code-block:: bash

            crontab -e
            # Add the following line to the crontab file
            */5 * * * * /usr/bin/docker exec joplin-headless joplin sync

    It is advised to have at least a remote synchronization target, and have
    the same target configured both in the Joplin desktop or mobile application
    and in the headless instance, so that you can keep your notes in sync
    across all of your devices, even though this plugin will only interact with
    the headless instance.
    """

    _default_note_fields = (
        'id',
        'parent_id',
        'title',
        'created_time',
        'updated_time',
        'latitude',
        'longitude',
        'altitude',
        'author',
        'source',
        'source_url',
        'source_application',
    )

    _default_collection_fields = (
        'id',
        'title',
        'parent_id',
        'created_time',
        'updated_time',
    )

    def __init__(self, *args, host: str, port: int = 41184, token: str, **kwargs):
        """
        :param host: The hostname or IP address of your Joplin application.
        :param port: The port number of your Joplin application (default: 41184).
        :param token: The access token of your Joplin server.
        """
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.token = token

    def _base_url(self, path: str = '') -> str:
        return urljoin(
            f'http://{self.host}:{self.port}/',
            path.lstrip('/'),
        )

    def _exec(self, method: str, path: str = '', **kwargs) -> Optional[dict]:
        """
        Execute a request to the Joplin API.
        """
        url = self._base_url(path)
        params = kwargs.pop('params', {})
        self.logger.debug(
            'Calling Joplin API: %s %s with params: %s',
            method,
            url,
            params,
        )

        params['token'] = self.token
        response = requests.request(method, url, params=params, timeout=10, **kwargs)

        if not response.ok:
            err = response.text
            try:
                rs = response.json()
                err = rs.get('error', err).splitlines()[0]
            except (TypeError, ValueError):
                pass

            raise RuntimeError(
                f'Joplin API request failed with status {response.status_code}: {err}'
            )

        try:
            return response.json()
        except ValueError:
            return None

    def _parse_source(self, data: dict) -> Optional[NoteSource]:
        has_source = any(
            key in data for key in ('source', 'source_url', 'source_application')
        )

        if not has_source:
            return None

        return NoteSource(
            name=data.get('source'),
            url=data.get('source_url'),
            app=data.get('source_application'),
        )

    @staticmethod
    def _parse_time(t: Optional[int]) -> Optional[datetime.datetime]:
        """
        Parse a Joplin timestamp (in milliseconds) into a datetime object.
        """
        if t is None:
            return None
        return datetime.datetime.fromtimestamp(t / 1000)

    def _to_note(self, data: dict) -> Note:
        parent_id = data.get('parent_id')
        parent = None

        if parent_id:
            parent = self._collections.get(
                parent_id, NoteCollection(id=parent_id, title='')
            )

        return Note(
            **{
                'id': data.get('id', ''),
                'title': data.get('title', ''),
                'description': data.get('description'),
                'content': data.get('body'),
                'parent': parent,
                'source': self._parse_source(data),
                **self._parse_geo(data),
                'created_at': self._parse_time(data.get('created_time')),
                'updated_at': self._parse_time(data.get('updated_time')),
            }
        )

    def _to_collection(self, data: dict) -> NoteCollection:
        """
        Convert a Joplin collection (folder) to a NoteCollection.
        """
        return NoteCollection(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description'),
            created_at=self._parse_time(data.get('created_time')),
            updated_at=self._parse_time(data.get('updated_time')),
        )

    def _fetch_note(self, note_id: Any, *_, **__) -> Optional[Note]:
        note = None
        err = None

        try:
            note = self._exec(
                'GET',
                f'notes/{note_id}',
                params={
                    'fields': ','.join(
                        *[
                            self._default_note_fields,
                            'body',  # Include body content
                        ]
                    )
                },
            )
        except RuntimeError as e:
            err = e

        if not note:
            self.logger.warning(
                'Note with ID %s could not be fetched: %s',
                note_id,
                err if err else 'Unknown error',
            )
            return None

        return self._to_note(note)  # type: ignore[return-value]

    def _fetch_notes(self, *_, **__) -> List[Note]:
        """
        Fetch notes from Joplin.
        """
        notes_data = (
            self._exec(
                'GET', 'notes', params={'fields': ','.join(self._default_note_fields)}
            )
            or {}
        ).get('items', [])
        return [self._to_note(note) for note in notes_data]

    def _create_note(
        self,
        title: str,
        content: str,
        *_,
        parent: Optional[Any] = None,
        geo: Optional[dict] = None,
        source: Optional[NoteSource] = None,
        author: Optional[str] = None,
        **__,
    ) -> Note:
        data = {
            'title': title,
            'body': content,
            'parent_id': parent,
            'latitude': geo.get('latitude') if geo else None,
            'longitude': geo.get('longitude') if geo else None,
            'altitude': geo.get('altitude') if geo else None,
            'author': author or '',
        }

        if source:
            data['source'] = source.name or ''
            data['source_url'] = source.url or ''
            data['source_application'] = source.app or ''

        response = self._exec('POST', 'notes', json=data)
        assert response, 'Failed to create note'
        return self._to_note(response)

    def _edit_note(
        self,
        note_id: Any,
        *_,
        title: Optional[str] = None,
        content: Optional[str] = None,
        parent: Optional[Any] = None,
        geo: Optional[dict] = None,
        source: Optional[NoteSource] = None,
        author: Optional[str] = None,
        **__,
    ) -> Note:
        data = {}

        if title is not None:
            data['title'] = title
        if content is not None:
            data['body'] = content
        if parent is not None:
            data['parent_id'] = parent
        if geo:
            data['latitude'] = geo.get('latitude')
            data['longitude'] = geo.get('longitude')
            data['altitude'] = geo.get('altitude')
        if author is not None:
            data['author'] = author
        if source:
            data['source'] = source.name or ''
            data['source_url'] = source.url or ''
            data['source_application'] = source.app or ''

        response = self._exec('PUT', f'notes/{note_id}', json=data)
        assert response, 'Failed to edit note'
        return self._to_note(response)

    def _delete_note(self, note_id: Any, *_, **__):
        self._exec('DELETE', f'notes/{note_id}')

    def _fetch_collection(
        self, collection_id: Any, *_, **__
    ) -> Optional[NoteCollection]:
        """
        Fetch a collection (folder) by its ID.
        """
        collection_data = self._exec(
            'GET',
            f'folders/{collection_id}',
            params={'fields': ','.join(self._default_collection_fields)},
        )

        if not collection_data:
            self.logger.warning(
                'Collection with ID %s could not be fetched', collection_id
            )
            return None

        return self._to_collection(collection_data)

    def _fetch_collections(self, *_, **__) -> List[NoteCollection]:
        """
        Fetch collections (folders) from Joplin.
        """
        collections_data = (
            self._exec(
                'GET',
                'folders',
                params={'fields': ','.join(self._default_collection_fields)},
            )
            or {}
        ).get('items', [])
        return [self._to_collection(coll) for coll in collections_data]

    def _create_collection(
        self,
        title: str,
        *_,
        parent: Optional[Any] = None,
        **__,
    ) -> NoteCollection:
        response = self._exec(
            'POST',
            'folders',
            json={
                'title': title,
                'parent_id': parent,
            },
        )

        assert response, 'Failed to create collection'
        return self._to_collection(response)

    def _edit_collection(
        self,
        collection_id: Any,
        *_,
        title: Optional[str] = None,
        parent: Optional[Any] = None,
        **__,
    ) -> NoteCollection:
        data = {}

        if title is not None:
            data['title'] = title
        if parent is not None:
            data['parent_id'] = parent

        response = self._exec('PUT', f'folders/{collection_id}', json=data)
        assert response, 'Failed to edit collection'
        return self._to_collection(response)

    def _delete_collection(self, collection_id: Any, *_: Any, **__: Any):
        """
        Delete a collection (folder) by its ID.
        """
        self._exec('DELETE', f'folders/{collection_id}')


# vim:sw=4:ts=4:et:
