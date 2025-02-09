import base64
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Collection, List, Optional
from urllib.parse import urljoin

from marshmallow import Schema
import requests

from platypush.schemas.piped import (
    PipedChannelSchema,
    PipedPlaylistSchema,
    PipedVideoSchema,
)
from platypush.utils import ignore_unhashable

from ..model import YoutubeChannel, YoutubeEntity, YoutubePlaylist, YoutubeVideo
from .base import BaseBackend


@dataclass
class PipedBackend(BaseBackend):
    """
    Piped YouTube backend.

    :param instance_url: Base API URL of the Piped instance.
    :param auth_token: Optional authentication token from the Piped instance.
    """

    instance_url: str = 'https://pipedapi.kavin.rocks'
    auth_token: Optional[str] = None
    frontend_url: Optional[str] = None

    @property
    def _frontend_url(self) -> str:
        if not self.frontend_url:
            return self.instance_url.replace('api', '')

        return self.frontend_url

    def _api_url(self, path: str = '') -> str:
        return f"{self.instance_url}/{path}"

    def _request(
        self,
        path: str,
        method: str = 'get',
        body: Optional[str] = None,
        auth: bool = True,
        **kwargs,
    ):
        timeout = kwargs.pop('timeout', self.timeout)
        if auth:
            kwargs['params'] = kwargs.get('params', {})
            kwargs['params']['authToken'] = self.auth_token
            kwargs['headers'] = kwargs.get('headers', {})
            kwargs['headers']['Authorization'] = self.auth_token

        if body:
            kwargs['data'] = body

        func = getattr(requests, method.lower())
        rs = func(self._api_url(path), timeout=timeout, **kwargs)
        rs.raise_for_status()

        try:
            return rs.json()
        except (TypeError, ValueError):
            return {}

    def _to_entity(
        self,
        item: dict,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> YoutubeEntity:
        def dump(schema: Schema, item: dict) -> dict:
            data = dict(schema.dump(item))
            data.pop('item_type', None)
            return data

        if not type:
            type = item.get('type')

        if type == 'stream':
            return YoutubeVideo(**dump(PipedVideoSchema(), item))

        if type == 'channel':
            channel_id = item.pop('id', None)
            if channel_id:
                url = f'/channel/{channel_id}'

            url = item.pop('url', None)
            if url and not re.match(r'^https?://', url):
                url = urljoin(self.instance_url, url)

            data = dump(
                PipedChannelSchema(),
                {
                    'url': url,
                    **item,
                },
            )

            data.pop('id', None)
            return YoutubeChannel(**data)

        if type == 'playlist':
            playlist_id = item.pop('id', None)
            if not playlist_id:
                playlist_id = re.sub(
                    r'^.*\/playlist\?list=([^&]+).*$', r'\1', item.get('url', '')
                )

            playlist = dump(
                PipedPlaylistSchema(),
                {
                    'url': urljoin(
                        self._frontend_url,
                        f'playlist?list={playlist_id}',
                    ),
                    **item,
                },
            )

            playlist.pop('id', None)
            return YoutubePlaylist(**playlist)

        raise ValueError(f'Unknown item type: {type}')

    def _to_video(self, video: dict) -> YoutubeVideo:
        item = self._to_entity(video, type='stream')
        assert isinstance(item, YoutubeVideo), f'Expected a video, got {item}'
        return item

    def _to_channel(self, channel: dict) -> YoutubeChannel:
        item = self._to_entity(channel, type='channel')
        assert isinstance(item, YoutubeChannel), f'Expected a channel, got {item}'
        return item

    def _to_playlist(self, playlist: dict) -> YoutubePlaylist:
        item = self._to_entity(playlist, type='playlist')
        assert isinstance(item, YoutubePlaylist), f'Expected a playlist, got {item}'
        return item

    @ignore_unhashable
    @lru_cache(maxsize=10)  # noqa
    def _get_channel(self, id: str) -> dict:  # pylint: disable=redefined-builtin
        if (
            id.startswith('http')
            or id.startswith('https')
            or id.startswith('/channel/')
        ):
            id = id.split('/')[-1]

        return (
            PipedChannelSchema().dump(self._request(f'channel/{id}')) or {}  # type: ignore
        )

    def search(self, query: str, *_, **__) -> List[YoutubeEntity]:
        rs = self._request('search', auth=False, params={'q': query, 'filter': 'all'})
        results = [self._to_entity(item) for item in rs.get('items', [])]
        return results

    def get_feed(self, **_) -> List[YoutubeVideo]:
        return [self._to_video(item) for item in (self._request('feed') or [])]

    def get_playlists(self, **_) -> List[YoutubePlaylist]:
        return [
            self._to_playlist(item) for item in (self._request('user/playlists') or [])
        ]

    def get_playlist(
        self,
        id: str,  # pylint: disable=redefined-builtin
        **_,
    ) -> List[YoutubeVideo]:
        return [
            self._to_video(item)
            for item in (
                self._request(f'playlists/{id}').get('relatedStreams', []) or []
            )
        ]

    def get_subscriptions(self, **_) -> List[YoutubeChannel]:
        return [
            self._to_channel(item) for item in (self._request('subscriptions') or [])
        ]

    def get_channel(
        self,
        id: str,  # pylint: disable=redefined-builtin
        page: Optional[str] = None,
        **_,
    ) -> YoutubeChannel:
        if (
            id.startswith('http')
            or id.startswith('https')
            or id.startswith('/channel/')
        ):
            id = id.split('/')[-1]

        info = {}
        if page:
            info = self._get_channel(id).copy()
            info.pop('next_page_token', None)
            info['items'] = []
            next_page = base64.b64decode(page.encode()).decode()
            response = {
                **info,
                **self._request(
                    f'nextpage/channel/{id}', params={'nextpage': next_page}, auth=False
                ),
            }
        else:
            response = self._request(f'channel/{id}')

        if not response.get('url'):
            response['url'] = urljoin(self._frontend_url, f'channel/{id}')

        return self._to_channel(response)

    def add_to_playlist(
        self, playlist_id: str, item_ids: Optional[Collection[str]] = None, **kwargs
    ):
        items = item_ids
        if kwargs.get('video_id'):
            self.logger.warning(
                'The "video_id" parameter is deprecated. Use "item_ids" instead.'
            )
            items = [kwargs['video_id']]

        assert items, 'No items provided to add to the playlist'
        self._request(
            'user/playlists/add',
            method='post',
            json={
                'videoIds': [self._get_video_id(item_id) for item_id in items],
                'playlistId': playlist_id,
            },
        )

    def remove_from_playlist(
        self,
        playlist_id: str,
        item_ids: Optional[Collection[str]] = None,
        indices: Optional[Collection[int]] = None,
        **kwargs,
    ):
        items = item_ids
        if kwargs.get('video_id'):
            self.logger.warning(
                'The "video_id" parameter is deprecated. Use "item_ids" instead.'
            )
            items = [kwargs['video_id']]

        if kwargs.get('index'):
            self.logger.warning(
                'The "index" parameter is deprecated. Use "indices" instead.'
            )
            indices = [kwargs['index']]

        assert items or indices, 'Either item_ids or indices must be provided'

        if not indices:
            item_ids = {
                video_id
                for video_id in [
                    self._get_video_id(item_id) for item_id in (items or [])
                ]
                if video_id
            }

            playlist_items = self._request(f'playlists/{playlist_id}').get(
                'relatedStreams', []
            )
            indices = [
                i
                for i, v in enumerate(playlist_items)
                if self._get_video_id(v.get('url')) in item_ids
            ]

        if not indices:
            self.logger.warning(
                'Items not found in the playlist %s: %s', playlist_id, items or []
            )
            return

        for index in indices:
            self._request(
                'user/playlists/remove',
                method='post',
                json={
                    'index': index,
                    'playlistId': playlist_id,
                },
            )

    def create_playlist(self, name: str, **_) -> YoutubePlaylist:
        name = name.strip()
        assert name, 'Playlist name cannot be empty'

        playlist_id = self._request(
            'user/playlists/create',
            method='post',
            json={'name': name},
        ).get('playlistId')

        assert playlist_id, 'Failed to create the playlist'
        playlists = self._request('user/playlists')
        new_playlist = next((p for p in playlists if p.get('id') == playlist_id), None)

        assert new_playlist, 'Failed to retrieve the new playlist'
        return self._to_playlist(new_playlist)

    def edit_playlist(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **_,
    ):  # pylint: disable=redefined-builtin
        args = {}
        if name:
            args['newName'] = name
        if description:
            args['description'] = description
        if not args:
            self.logger.info('No new name or description provided')
            return

        self._request(
            'user/playlists/rename',
            method='post',
            json={
                'playlistId': id,
                **args,
            },
        )

    def delete_playlist(self, id: str):  # pylint: disable=redefined-builtin
        self._request(
            'user/playlists/delete',
            method='post',
            json={'playlistId': id},
        )

    def is_subscribed(self, channel_id: str) -> bool:
        return self._request(
            'subscribed',
            params={'channelId': channel_id},
        ).get('subscribed', False)

    def subscribe(self, channel_id: str):
        self._request(
            'subscribe',
            method='post',
            json={'channelId': channel_id},
        )

    def unsubscribe(self, channel_id: str):
        self._request(
            'unsubscribe',
            method='post',
            json={'channelId': channel_id},
        )


# vim:sw=4:ts=4:et:
