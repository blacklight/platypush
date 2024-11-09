import base64
import re
from functools import lru_cache
from typing import Collection, List, Optional

import requests

from platypush.plugins import Plugin, action
from platypush.schemas.piped import (
    PipedChannelSchema,
    PipedPlaylistSchema,
    PipedVideoSchema,
)


class YoutubePlugin(Plugin):
    r"""
    YouTube plugin.

    Unlike other Google plugins, this plugin doesn't rely on the Google API.

    That's because the official YouTube API has been subject to many changes to
    prevent scraping, and it requires the user to tinker with the OAuth layer,
    app permissions and app validation in order to get it working.

    Instead, it relies on a `Piped <https://docs.piped.video/>`_, an open-source
    alternative YouTube gateway.

    It thus requires a link to a valid Piped instance.
    """

    _timeout = 20

    def __init__(
        self,
        piped_api_url: str = 'https://pipedapi.kavin.rocks',
        auth_token: Optional[str] = None,
        **kwargs,
    ):
        """
        :param piped_api_url: Base API URL of the Piped instance (default:
            ``https://pipedapi.kavin.rocks``).
        :param auth_token: Optional authentication token from the Piped
            instance. This is required if you want to access your private feed
            and playlists, but not for searching public videos.

            In order to retrieve an authentication token:

              1. Login to your configured Piped instance.
              2. Copy the RSS/Atom feed URL on the _Feed_ tab.
              3. Copy the ``auth_token`` query parameter from the URL.
              4. Enter it in the ``auth_token`` field in the ``youtube`` section
                 of the configuration file.

        """
        super().__init__(**kwargs)
        self._piped_api_url = piped_api_url
        self._auth_token = auth_token

    def _api_url(self, path: str = '') -> str:
        return f"{self._piped_api_url}/{path}"

    def _request(
        self,
        path: str,
        method: str = 'get',
        body: Optional[str] = None,
        auth: bool = True,
        **kwargs,
    ):
        timeout = kwargs.pop('timeout', self._timeout)
        if auth:
            kwargs['params'] = kwargs.get('params', {})
            kwargs['params']['authToken'] = self._auth_token
            kwargs['headers'] = kwargs.get('headers', {})
            kwargs['headers']['Authorization'] = self._auth_token

        if body:
            kwargs['data'] = body

        func = getattr(requests, method.lower())
        rs = func(self._api_url(path), timeout=timeout, **kwargs)
        rs.raise_for_status()

        try:
            return rs.json()
        except (TypeError, ValueError):
            return {}

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

    @staticmethod
    def _get_video_id(id_or_url: str) -> str:
        m = re.search(r'/watch\?v=([^&]+)', id_or_url)
        if m:
            return m.group(1)

        return id_or_url

    @staticmethod
    def _dump_item(item: dict) -> dict:
        if item.get('type') == 'stream':
            return dict(PipedVideoSchema().dump(item))

        if item.get('type') == 'channel':
            return dict(PipedChannelSchema().dump(item))

        if item.get('type') == 'playlist':
            return dict(PipedPlaylistSchema().dump(item))

        return item

    @action
    def search(self, query: str, **_) -> List[dict]:
        """
        Search for YouTube videos.

        :param query: Query string.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        self.logger.info('Searching YouTube for "%s"', query)
        rs = self._request('search', auth=False, params={'q': query, 'filter': 'all'})
        results = [self._dump_item(item) for item in rs.get('items', [])]
        self.logger.info(
            '%d YouTube results for the search query "%s"',
            len(results),
            query,
        )

        return results

    @action
    def get_feed(self) -> List[dict]:
        """
        Retrieve the YouTube feed.

        Depending on your account settings on the configured Piped instance,
        this may return either the latest videos uploaded by your subscribed
        channels, or the trending videos in the configured area.

        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return PipedVideoSchema(many=True).dump(self._request('feed')) or []

    @action
    def get_playlists(self) -> List[dict]:
        """
        Retrieve the playlists saved by the user logged in to the Piped
        instance.

        :return: .. schema:: piped.PipedPlaylistSchema(many=True)
        """
        return (
            PipedPlaylistSchema(many=True).dump(self._request('user/playlists')) or []
        )

    @action
    def get_playlist(self, id: str) -> List[dict]:  # pylint: disable=redefined-builtin
        """
        Retrieve the videos in a playlist.

        :param id: Piped playlist ID.
        :return: .. schema:: piped.PipedVideoSchema(many=True)
        """
        return (
            PipedVideoSchema(many=True).dump(
                self._request(f'playlists/{id}').get('relatedStreams', [])
            )
            or []
        )

    @action
    def get_subscriptions(self) -> List[dict]:
        """
        Retrieve the channels subscribed by the user logged in to the Piped
        instance.

        :return: .. schema:: piped.PipedChannelSchema(many=True)
        """
        return PipedChannelSchema(many=True).dump(self._request('subscriptions')) or []

    @action
    def get_channel(
        self,
        id: str,  # pylint: disable=redefined-builtin
        next_page_token: Optional[str] = None,
    ) -> dict:
        """
        Retrieve the information and videos of a channel given its ID or URL.

        :param id: Channel ID or URL.
        :param next_page_token: Optional token to retrieve the next page of
            results.
        :return: .. schema:: piped.PipedChannelSchema
        """
        if (
            id.startswith('http')
            or id.startswith('https')
            or id.startswith('/channel/')
        ):
            id = id.split('/')[-1]

        info = {}
        if next_page_token:
            info = self._get_channel(id).copy()
            info.pop('next_page_token', None)
            info['items'] = []
            next_page = base64.b64decode(next_page_token.encode()).decode()
            response = {
                **info,
                **self._request(
                    f'nextpage/channel/{id}', params={'nextpage': next_page}, auth=False
                ),
            }
        else:
            response = self._request(f'channel/{id}')

        return PipedChannelSchema().dump(response) or {}  # type: ignore

    @action
    def add_to_playlist(
        self, playlist_id: str, item_ids: Optional[Collection[str]] = None, **kwargs
    ):
        """
        Add a video to a playlist.

        :param playlist_id: Piped playlist ID.
        :param item_ids: YouTube IDs or URLs to add to the playlist.
        """
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

    @action
    def remove_from_playlist(
        self,
        playlist_id: str,
        item_ids: Optional[Collection[str]] = None,
        indices: Optional[Collection[int]] = None,
        **kwargs,
    ):
        """
        Remove a video from a playlist.

        Note that either ``item_ids`` or ``indices`` must be provided.

        :param item_ids: YouTube video IDs or URLs to remove from the playlist.
        :param indices: (0-based) indices of the items in the playlist to remove.
        :param playlist_id: Piped playlist ID.
        """
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

    @action
    def create_playlist(self, name: str) -> dict:
        """
        Create a new playlist.

        :param name: Playlist name.
        :return: Playlist information.
        """
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
        return dict(PipedPlaylistSchema().dump(new_playlist) or {})

    @action
    def rename_playlist(
        self, id: str, name: Optional[str] = None, description: Optional[str] = None
    ):  # pylint: disable=redefined-builtin
        """
        Rename a playlist.

        :param id: Piped playlist ID.
        :param name: New playlist name.
        :param description: New playlist description.
        """
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

    @action
    def delete_playlist(self, id: str):  # pylint: disable=redefined-builtin
        """
        Delete a playlist.

        :param id: Piped playlist ID.
        """
        self._request(
            'user/playlists/delete',
            method='post',
            json={'playlistId': id},
        )

    @action
    def is_subscribed(self, channel_id: str) -> bool:
        """
        Check if the user is subscribed to a channel.

        :param channel_id: YouTube channel ID.
        :return: True if the user is subscribed to the channel, False otherwise.
        """
        return self._request(
            'subscribed',
            params={'channelId': channel_id},
        ).get('subscribed', False)

    @action
    def subscribe(self, channel_id: str):
        """
        Subscribe to a channel.

        :param channel_id: YouTube channel ID.
        """
        self._request(
            'subscribe',
            method='post',
            json={'channelId': channel_id},
        )

    @action
    def unsubscribe(self, channel_id: str):
        """
        Unsubscribe from a channel.

        :param channel_id: YouTube channel ID.
        """
        self._request(
            'unsubscribe',
            method='post',
            json={'channelId': channel_id},
        )


# vim:sw=4:ts=4:et:
