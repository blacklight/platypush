from typing import Collection, Optional, List

from platypush.plugins.google import GooglePlugin
from platypush.schemas.youtube import (
    YoutubeChannelSchema,
    YoutubePlaylistSchema,
    YoutubeVideoSchema,
    yt_time,
)

from ..model import YoutubeChannel, YoutubeEntity, YoutubePlaylist, YoutubeVideo
from .base import BaseBackend


class GoogleBackend(GooglePlugin, BaseBackend):
    """
    Google (official) YouTube backend.

    See :class:`platypush.plugins.google.GooglePlugin` for the common
    configuration parameters.
    """

    scopes = [
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl',
    ]

    def __init__(self, **kwargs):
        super().__init__(scopes=self.scopes, **kwargs)

    def get_service(self, *_, **__):
        return super().get_service(service='youtube', version='v3')

    def _request(self, *_, **__):
        pass

    def _to_entity(self, item: dict) -> YoutubeEntity:
        kind = item.get('kind')

        if kind == 'youtube#video':
            return self._to_video(item)
        if kind == 'youtube#playlist':
            return self._to_playlist(item)
        if kind == 'youtube#channel':
            return self._to_channel(item)

        raise NotImplementedError(f'Unsupported entity kind: {kind}')

    def _to_video(self, item: dict) -> YoutubeVideo:
        args = dict(YoutubeVideoSchema().dump(item))
        args.pop('id', None)
        args.pop('item_type', None)
        return YoutubeVideo(**args)

    def _to_playlist(self, item: dict) -> YoutubePlaylist:
        args = dict(YoutubePlaylistSchema().dump(item))
        args.pop('id', None)
        args.pop('item_type', None)
        return YoutubePlaylist(**args)

    def _to_channel(self, item: dict) -> YoutubeChannel:
        args = dict(YoutubeChannelSchema().dump(item))
        args.pop('id', None)
        args.pop('item_type', None)
        return YoutubeChannel(**args)

    def search(
        self, query: str, page: Optional[str] = None, sort=None, **_
    ) -> List[YoutubeEntity]:
        response = (
            self.get_service()
            .search()
            .list(
                part='snippet',
                q=query,
                pageToken=page,
                order=sort,
            )
            .execute()
        )

        next_page_token = response.get('nextPageToken')
        ret = []

        for item in response.get('items', []):
            # Replace the `youtube#searchResult` type with the actual entity type
            kind = item['kind'] = item['id']['kind']
            if kind == 'youtube#video':
                item['id'] = item['id']['videoId']
            elif kind == 'youtube#playlist':
                item['id'] = item['id']['playlistId']
            elif kind == 'youtube#channel':
                item['id'] = item['id']['channelId']
            else:
                self.logger.info('Ignoring unsupported entity kind: %s', kind)
                continue

            entity = self._to_entity(item)
            entity.next_page_token = next_page_token  # type: ignore
            ret.append(entity)

        return ret

    def get_playlists(self, page: Optional[str] = None, **_) -> List[YoutubePlaylist]:
        response = (
            self.get_service()
            .playlists()
            .list(
                part='contentDetails,snippet',
                mine=True,
                maxResults=50,
                pageToken=page,
            )
            .execute()
        )

        ret = []
        for item in response.get('items', []):
            entity = self._to_playlist(item)
            entity.next_page_token = response.get('nextPageToken')
            ret.append(entity)

        return ret

    def get_playlist(
        self,
        id: str,  # pylint: disable=redefined-builtin
        page: Optional[str] = None,
        **_,
    ) -> List[YoutubeVideo]:
        results = (
            self.get_service()
            .playlistItems()
            .list(
                part='contentDetails,snippet',
                playlistId=id,
                maxResults=50,
                pageToken=page,
            )
            .execute()
        )

        next_page_token = results.get('nextPageToken')
        item_data = [
            {
                'index_id': item['id'],
                'index': item.get('snippet', {}).get('position'),
            }
            for item in results.get('items', [])
        ]

        items = [self._to_video(item) for item in results.get('items', [])]
        for i, item in enumerate(items):
            item.next_page_token = next_page_token
            item.index = item_data[i].get('index')
            item.index_id = item_data[i].get('index_id')

        # Get the videos from the playlist, since the API doesn't return some
        # of the metadata (e.g. duration)
        results = {
            item['id']: item
            for item in (
                self.get_service()
                .videos()
                .list(
                    part='contentDetails,snippet',
                    id=','.join([item.id for item in items]),
                    maxResults=len(items),
                )
                .execute()
            ).get('items', [])
        }

        for item in items:
            video = results.get(item.id)
            if video:
                item.duration = (
                    yt_time(video['contentDetails']['duration']) or item.duration
                )

        return items

    def get_subscriptions(
        self, page: Optional[str] = None, **_
    ) -> List[YoutubeChannel]:
        results = (
            self.get_service()
            .subscriptions()
            .list(
                part='contentDetails,snippet',
                mine=True,
                order='alphabetical',
                maxResults=50,
                pageToken=page,
            )
            .execute()
        )

        channels = [self._to_channel(item) for item in results.get('items', [])]
        for channel in channels:
            channel.next_page_token = results.get('nextPageToken')

        return channels

    def get_channel(self, id: str, page: Optional[str] = None, **_) -> YoutubeChannel:
        results = (
            self.get_service()
            .channels()
            .list(
                part='snippet,contentDetails,statistics',
                id=id,
            )
            .execute()
        )

        result = next(iter(results.get('items', [])), None)
        assert result, f'Channel not found: {id}'
        channel = self._to_channel(result)

        playlist_id = (
            result.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        )

        if playlist_id:
            channel.items = list(self.get_playlist(playlist_id, page=page))
            if channel.items:
                channel.next_page_token = channel.items[0].next_page_token  # type: ignore

        return channel

    def get_feed(self, *_, **__) -> List[YoutubeVideo]:
        raise NotImplementedError("Feed not supported by the YouTube API")

    def add_to_playlist(
        self, playlist_id: str, item_ids: Optional[Collection[str]] = None, **_
    ):
        for item_id in item_ids or []:
            self.get_service().playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': item_id,
                        },
                    }
                },
            ).execute()

    def remove_from_playlist(
        self,
        *_,
        item_ids: Optional[Collection[str]] = None,
        **__,
    ):
        for item_id in item_ids or []:
            self.get_service().playlistItems().delete(id=item_id).execute()

    def create_playlist(self, name: str, **_) -> YoutubePlaylist:
        result = (
            self.get_service()
            .playlists()
            .insert(
                part='snippet',
                body={
                    'snippet': {
                        'title': name,
                    }
                },
            )
            .execute()
        )

        return self._to_playlist(result)

    def edit_playlist(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **_,
    ):  # pylint: disable=redefined-builtin
        self.get_service().playlists().update(
            part='snippet',
            body={
                'id': id,
                'snippet': {
                    'title': name,
                    'description': description,
                },
            },
        ).execute()

    def delete_playlist(self, id: str):  # pylint: disable=redefined-builtin
        self.get_service().playlists().delete(id=id).execute()

    def is_subscribed(self, channel_id: str) -> bool:
        subscription = (
            self.get_service()
            .subscriptions()
            .list(
                part='snippet',
                forChannelId=channel_id,
                mine=True,
            )
            .execute()
        )

        return bool(subscription)

    def subscribe(self, channel_id: str):
        self.get_service().subscriptions().insert(
            part='snippet',
            body={
                'snippet': {
                    'resourceId': {
                        'kind': 'youtube#channel',
                        'channelId': channel_id,
                    },
                }
            },
        ).execute()

    def unsubscribe(self, channel_id: str):
        self.get_service().subscriptions().delete(id=channel_id).execute()


# vim:sw=4:ts=4:et:
