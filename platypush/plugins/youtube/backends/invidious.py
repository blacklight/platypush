import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Collection, List, Optional, Union
from urllib.parse import urljoin

from marshmallow import Schema
import requests

from platypush.schemas.invidious import (
    InvidiousChannelSchema,
    InvidiousPlaylistSchema,
    InvidiousVideoSchema,
)
from platypush.utils import ignore_unhashable

from ..model import YoutubeChannel, YoutubeEntity, YoutubePlaylist, YoutubeVideo
from .base import BaseBackend


@dataclass
class InvidiousBackend(BaseBackend):
    """
    Invidious YouTube backend.

    :param instance_url: Base URL of the Invidious instance.
    """

    instance_url: str = 'https://yewtu.be'
    auth_token: Optional[str] = None

    def _request(
        self,
        path: str,
        method: str = 'get',
        body: Optional[Union[str, list, dict]] = None,
        auth: bool = True,
        **kwargs,
    ):
        req = {
            **{
                "timeout": self.timeout,
                "headers": {},
                **kwargs,
            },
        }

        api_url = self.instance_url.rstrip('/') + '/api/v1'
        if auth:
            api_url = f'{api_url}/auth'
            req["headers"]["Authorization"] = f"Bearer {self.auth_token}"

        if body:
            req["json"] = body

        api_url = api_url + '/' + path.lstrip('/')
        rs = requests.request(
            method.upper(),
            api_url,
            **req,
        )

        try:
            rs.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error('Error while processing response to %s: %s', api_url, e)
            self.logger.debug('Response content: %s', rs.content)
            raise e

        return rs

    def _to_entity(self, item: dict) -> YoutubeEntity:
        def dump(schema: Schema, item: dict) -> dict:
            data = dict(schema.dump(item))
            id = data.pop("id", None)
            item_type = data.pop("item_type", None)

            if item_type == "channel":
                data["url"] = urljoin(self.instance_url, f'/channel/{id}')
            elif item_type == "playlist":
                data["url"] = urljoin(self.instance_url, f'/playlist?list={id}')

            if data.get("channel_url") and not data["channel_url"].startswith("http"):
                data["channel_url"] = urljoin(self.instance_url, data["channel_url"])

            return data

        if item.get('type') == 'video':
            item['url'] = urljoin(self.instance_url, f'/watch?v={item["videoId"]}')
            return YoutubeVideo(**dump(InvidiousVideoSchema(), item))

        if item.get('type') == 'channel':
            item['url'] = urljoin(self.instance_url, f'/channel/{item["authorId"]}')
            return YoutubeChannel(**dump(InvidiousChannelSchema(), item))

        if item.get('type') == 'playlist':
            item['url'] = urljoin(
                self.instance_url, f'/playlist?list={item["playlistId"]}'
            )
            return YoutubePlaylist(**dump(InvidiousPlaylistSchema(), item))

        raise ValueError(f'Unsupported entity type: {item.get("type")}')

    def _to_video(self, item: dict) -> YoutubeVideo:
        if not item.get('type') or item.get('type') == 'shortVideo':
            item['type'] = 'video'

        assert item.get('type') == 'video', f'Item [{item}] is not a video'
        ret = self._to_entity(item)
        assert isinstance(ret, YoutubeVideo), f'Expected a video, got {type(ret)}'
        return ret

    def _to_channel(self, item: dict) -> YoutubeChannel:
        if not item.get('type'):
            item['type'] = 'channel'

        assert item.get('type') == 'channel', f'Item [{item}] is not a channel'
        ret = self._to_entity(item)
        assert isinstance(ret, YoutubeChannel), f'Expected a channel, got {type(ret)}'
        return ret

    def _to_playlist(self, item: dict) -> YoutubePlaylist:
        if not item.get('type') or item.get('type') == 'invidiousPlaylist':
            item['type'] = 'playlist'

        assert item.get('type') == 'playlist', f'Item [{item}] is not a playlist'
        ret = self._to_entity(item)
        assert isinstance(ret, YoutubePlaylist), f'Expected a playlist, got {type(ret)}'
        return ret

    def _json(self, rs: requests.Response) -> Union[dict, list]:
        try:
            return rs.json()
        except ValueError as e:
            self.logger.error(
                'Error while parsing JSON response from Invidious: %s',
                json.dumps(
                    {
                        "url": rs.url,
                        "method": rs.request.method,
                        "response": {
                            "body": rs.content.decode(),
                            "status": rs.status_code,
                        },
                        "exception": {
                            "type": type(e).__name__,
                            "message": str(e),
                        },
                    },
                    indent=2,
                ),
            )
            raise e

    def _json_dict(self, rs: requests.Response) -> dict:
        resp = self._json(rs)
        assert isinstance(resp, dict), f'Expected a dict, got {type(resp)}'
        return resp

    def _json_list(self, rs: requests.Response) -> list:
        resp = self._json(rs)
        assert isinstance(resp, list), f'Expected a list, got {type(resp)}'
        return resp

    @staticmethod
    def _to_video_id(s: str) -> str:
        return re.sub(r'^https?://.*?/watch\?v=', '', s)

    def search(  # pylint: disable=too-many-positional-arguments
        self,
        query: str,
        page: Optional[int] = 1,
        sort: Optional[str] = "relevance",
        type: Optional[str] = "all",  # pylint: disable=redefined-builtin
        duration: Optional[str] = None,
        **_,
    ) -> List[YoutubeEntity]:
        """
        Supported sort values:

            - relevance
            - rating
            - date
            - views

        Supported type values:

            - video
            - channel
            - playlist
            - movie
            - show
            - all

        Supported duration values:

            - short
            - medium
            - long
        """
        rs = self._json_list(
            self._request(
                "search",
                auth=False,
                params={
                    "q": query,
                    "page": page,
                    "sort": sort,
                    "type": type,
                    "duration": duration,
                },
            )
        )

        return [self._to_entity(item) for item in rs]

    def get_feed(self, page: Optional[Any] = None, **_) -> List[YoutubeVideo]:
        resp = self._json_dict(self._request("feed", params={"page": page or 1}))
        return [
            self._to_video(video)
            for video in sorted(
                [
                    *{
                        item['videoId']: item
                        for item in [
                            *resp.get("videos", []),
                            *resp.get("notifications", []),
                        ]
                    }.values()
                ],
                key=lambda item: item.get("published", 0),
                reverse=True,
            )
        ]

    def get_playlists(self, **_) -> List[YoutubePlaylist]:
        return [
            self._to_playlist(playlist)
            for playlist in self._json_list(self._request("playlists"))
        ]

    def get_playlist(
        self,
        id: str,  # pylint: disable=redefined-builtin
        page: Optional[int] = None,
        **_,
    ) -> List[YoutubeVideo]:
        page = page or 1
        videos = [
            self._to_video(video)
            for video in self._json_dict(
                self._request(f"playlists/{id}", params={"page": page})
            ).get("videos", [])
        ]

        for video in videos:
            video.next_page_token = page + 1

        return videos

    def get_subscriptions(self, **_) -> List[YoutubeChannel]:
        return sorted(
            [
                self._to_channel(channel)
                for channel in self._json_list(self._request("subscriptions"))
            ],
            key=lambda channel: channel.name,
        )

    @ignore_unhashable
    @lru_cache(maxsize=100)  # noqa
    def _get_channel(
        self,
        id: str,  # pylint: disable=redefined-builtin
        **_,
    ) -> YoutubeChannel:
        return self._to_channel(
            self._json_dict(self._request(f"channels/{id}", auth=False))
        )

    def get_channel(
        self,
        id: str,  # pylint: disable=redefined-builtin
        page: Optional[str] = None,
        **_,
    ) -> YoutubeChannel:
        channel = self._get_channel(id)
        rs = self._json_dict(
            self._request(
                f"channels/{id}/videos",
                auth=False,
                params={
                    "continuation": page,
                    "sort_by": "newest",
                },
            )
        )

        channel.items = [self._to_video(video) for video in rs.get("videos", [])]
        channel.next_page_token = rs.get("continuation")
        return channel

    def add_to_playlist(
        self, playlist_id: str, item_ids: Optional[Collection[str]] = None, **_
    ):
        for item_id in item_ids or []:
            self._request(
                f"playlists/{playlist_id}/videos",
                method="post",
                body={"videoId": self._to_video_id(item_id)},
            )

    def remove_from_playlist(
        self,
        playlist_id: str,
        item_ids: Optional[Collection[str]] = None,
        indices: Optional[Collection[int]] = None,
        **_,
    ):
        items = self.get_playlist(playlist_id)
        items_by_index = {item.index: item for item in items if item.index is not None}
        index_ids = set()

        # Convert item_ids to indices
        if item_ids:
            item_ids = set(item_ids)
            video_ids = {self._to_video_id(item_id) for item_id in item_ids}

            index_ids.update(
                [
                    item.index_id
                    for item in items
                    if (item.id in video_ids or item.index_id in item_ids)
                    and item.index is not None
                ]
            )

        # Convert any numeric indices to index_ids
        for index_id in indices or []:
            if isinstance(index_id, int):
                item = items_by_index.get(index_id)
                if item and item.index_id is not None:
                    index_ids.add(index_id)

        if not index_ids:
            self.logger.warning(
                'No videos found in the playlist matching the specified IDs'
            )
            return

        for index_id in index_ids:
            self._request(
                f"playlists/{playlist_id}/videos/{index_id}",
                method="delete",
            )

    def create_playlist(
        self, name: str, privacy: str = "private", **_
    ) -> YoutubePlaylist:
        """
        Supported privacy values:

            - private
            - public
            - unlisted

        """
        return self._to_playlist(
            self._json_dict(
                self._request(
                    "playlists",
                    method="post",
                    body={"title": name, "privacy": privacy},
                )
            )
        )

    def edit_playlist(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        privacy: Optional[str] = None,
        **_,
    ):  # pylint: disable=redefined-builtin
        self._request(
            f"playlists/{id}",
            method="patch",
            body={
                "title": name,
                "description": description,
                "privacy": privacy,
            },
        )

    def delete_playlist(self, id: str):  # pylint: disable=redefined-builtin
        self._request(f"playlists/{id}", method="delete")

    def is_subscribed(self, channel_id: str) -> bool:
        subs = self.get_subscriptions()
        return any(sub.id == channel_id for sub in subs)

    def subscribe(self, channel_id: str):
        self._request(
            f"subscriptions/{channel_id}",
            method="post",
        )

    def unsubscribe(self, channel_id: str):
        self._request(
            f"subscriptions/{channel_id}",
            method="delete",
        )


# vim:sw=4:ts=4:et:
