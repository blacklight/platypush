from datetime import datetime
from typing import Collection, Optional

from marshmallow import EXCLUDE, fields, pre_dump
from marshmallow.schema import Schema

from platypush.schemas import StrippedString


class InvidiousVideoSchema(Schema):
    """
    Class for video items returned by the Invidious API.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    item_type = fields.Constant(
        'video',
        metadata={
            'description': 'Item type',
            'example': 'video',
        },
    )

    url = fields.Url(
        required=True,
        metadata={
            'description': 'Video URL',
            'example': 'https://youtube.com/watch?v=1234567890',
        },
    )

    title = StrippedString(
        load_default='[No Title]',
        metadata={
            'description': 'Video title',
            'example': 'My Video Title',
        },
    )

    image = fields.Url(
        metadata={
            'description': 'Image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    description = StrippedString(
        attribute='shortDescription',
        metadata={
            'description': 'Video description',
            'example': 'My video description',
        },
    )

    duration = fields.Int(
        load_default=0,
        attribute='lengthSeconds',
        metadata={
            'description': 'Video duration in seconds',
            'example': 120,
        },
    )

    channel = fields.String(
        attribute='author',
        metadata={
            'description': 'Channel name',
            'example': 'My Channel',
        },
    )

    channel_url = fields.Url(
        attribute='authorUrl',
        metadata={
            'description': 'Channel URL',
            'example': 'https://youtube.com/channel/1234567890',
        },
    )

    index = fields.Int(
        metadata={
            'description': "Index of the video, if it's part of a playlist",
            'example': 1,
        },
    )

    index_id = fields.String(
        attribute='indexId',
        metadata={
            'description': "Index ID of the video, if it's part of a playlist and the backend supports it",
            'example': '1234567890abcdef',
        },
    )

    created_at = fields.DateTime(
        attribute='published',
        metadata={
            'description': 'Video upload date',
            'example': '2020-01-01T00:00:00',
        },
    )

    @pre_dump
    def fill_image(self, data: dict, **_):
        images = {img['quality']: img for img in data.get('videoThumbnails', [])}
        img = None

        if images.get('high'):
            img = images['high']
        elif images.get('sddefault'):
            img = images['sddefault']
        elif images.get('medium'):
            img = images['medium']
        elif images.get('maxresdefault'):
            img = images['maxresdefault']
        elif images.get('default'):
            img = images['default']
        else:
            # Fallback to the first image
            img = next(iter(images.values()), None)

        if img:
            data['image'] = img['url']

        return data

    @pre_dump
    def normalize_timestamps(self, data: dict, **_):
        if data.get('published') and isinstance(data['published'], int):
            data['published'] = datetime.fromtimestamp(data["published"])

        return data


class InvidiousPlaylistSchema(Schema):
    """
    Class for playlist items returned by the Invidious API.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    item_type = fields.Constant(
        'playlist',
        metadata={
            'description': 'Item type',
            'example': 'playlist',
        },
    )

    id = fields.String(
        required=True,
        attribute='playlistId',
        metadata={
            'description': 'Playlist ID',
            'example': '1234567890abcdef',
        },
    )

    name = fields.String(
        attribute='title',
        load_default='[No Name]',
        metadata={
            'description': 'Playlist name',
            'example': 'My Playlist Name',
        },
    )

    image = fields.Url(
        attribute='playlistThumbnail',
        metadata={
            'description': 'Image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    videos = fields.Int(
        attribute='videoCount',
        load_default=0,
        metadata={
            'description': 'Number of videos in the playlist',
            'example': 10,
        },
    )

    channel = fields.String(
        attribute='author',
        metadata={
            'description': 'Channel name',
            'example': 'My Channel',
        },
    )

    channel_url = fields.Url(
        attribute='authorUrl',
        metadata={
            'description': 'Channel URL',
            'example': 'https://youtube.com/channel/1234567890',
        },
    )

    channel_image = fields.Url(
        metadata={
            'description': 'Channel image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    url = fields.Url(
        metadata={
            'description': 'Playlist URL',
            'example': 'https://youtube.com/playlist?list=1234567890',
        },
    )

    @pre_dump
    def fill_counters(self, data: dict, **_):
        if not data.get('videoCount') and data.get('videos') is not None:
            data['videoCount'] = len(data['videos'])

        return data

    @pre_dump
    def fill_channel_image(self, data: dict, **_):
        images = data.get('authorThumbnails', [])
        data['channel_image'] = next(
            iter(
                sorted(
                    images,
                    key=lambda i: i.get('width', 0),
                    reverse=True,
                )
            ),
            None,
        )

        return data


class InvidiousChannelSchema(Schema):
    """
    Class for channel items returned by the Invidious API.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    id = fields.String(
        required=True,
        attribute='authorId',
        metadata={
            'description': 'Channel ID',
            'example': '1234567890',
        },
    )

    item_type = fields.Constant(
        'channel',
        metadata={
            'description': 'Item type',
            'example': 'channel',
        },
    )

    url = fields.String(
        required=True,
        attribute='authorUrl',
        metadata={
            'description': 'Channel URL',
            'example': 'https://youtube.com/channel/1234567890',
        },
    )

    name = fields.String(
        attribute='author',
        load_default='[No Name]',
        metadata={
            'description': 'Channel name',
            'example': 'My Channel Name',
        },
    )

    description = StrippedString(
        metadata={
            'description': 'Channel description',
            'example': 'My channel description',
        },
    )

    image = fields.Url(
        metadata={
            'description': 'Channel image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    banner = fields.Url(
        metadata={
            'description': 'Channel banner URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    subscribers = fields.Int(
        attribute='subCount',
        load_default=0,
        metadata={
            'description': 'Number of subscribers',
            'example': 1000,
        },
    )

    next_page_token = fields.String(
        attribute='continuation',
        metadata={
            'description': 'The token that should be passed to get the next page of results',
            'example': '1234567890',
        },
    )

    items = fields.List(
        fields.Nested(InvidiousVideoSchema),
        metadata={
            'description': 'List of videos',
        },
    )

    @pre_dump
    def fill_images(self, data: dict, **_):
        def get_image(data: Optional[Collection[dict]]) -> Optional[str]:
            if not data:
                return None

            img = next(
                iter(
                    sorted(
                        data,
                        key=lambda i: i.get('width', 0),
                        reverse=True,
                    )
                ),
                None,
            )

            if img:
                return img['url']

            return None

        data['banner'] = get_image(data.get('authorBanners', []))
        data['image'] = get_image(data.get('authorThumbnails', []))
        return data

    @pre_dump
    def default_items(self, data: dict, **_):
        data['items'] = data.get('items', [])
        return data
