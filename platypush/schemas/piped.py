import base64
from datetime import datetime

from marshmallow import EXCLUDE, fields, pre_dump
from marshmallow.schema import Schema

from platypush.schemas import StrippedString


class PipedVideoSchema(Schema):
    """
    Class for video items returned by the Piped API.
    """

    class Meta:
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
        missing='[No Title]',
        metadata={
            'description': 'Video title',
            'example': 'My Video Title',
        },
    )

    image = fields.Url(
        attribute='thumbnail',
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
        missing=0,
        metadata={
            'description': 'Video duration in seconds',
            'example': 120,
        },
    )

    channel = fields.String(
        attribute='uploaderName',
        metadata={
            'description': 'Channel name',
            'example': 'My Channel',
        },
    )

    channel_url = fields.Url(
        attribute='uploaderUrl',
        metadata={
            'description': 'Channel URL',
            'example': 'https://youtube.com/channel/1234567890',
        },
    )

    channel_image = fields.Url(
        attribute='uploaderAvatar',
        metadata={
            'description': 'Channel image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    created_at = fields.DateTime(
        attribute='uploaded',
        metadata={
            'description': 'Video upload date',
            'example': '2020-01-01T00:00:00',
        },
    )

    @pre_dump
    def fill_urls(self, data: dict, **_):
        for attr in ('url', 'uploaderUrl'):
            if data.get(attr) and not data[attr].startswith('https://'):
                data[attr] = f'https://youtube.com{data[attr]}'

        return data

    @pre_dump
    def normalize_timestamps(self, data: dict, **_):
        if data.get('uploaded') and isinstance(data['uploaded'], int):
            data['uploaded'] = datetime.fromtimestamp(data["uploaded"] / 1000)

        return data


class PipedPlaylistSchema(Schema):
    """
    Class for playlist items returned by the Piped API.
    """

    class Meta:
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

    id = fields.UUID(
        required=True,
        metadata={
            'description': 'Playlist ID',
            'example': '12345678-1234-1234-1234-1234567890ab',
        },
    )

    name = StrippedString(
        missing='[No Name]',
        metadata={
            'description': 'Playlist name',
            'example': 'My Playlist Name',
        },
    )

    image = fields.Url(
        attribute='thumbnail',
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

    videos = fields.Int(
        missing=0,
        metadata={
            'description': 'Number of videos in the playlist',
            'example': 10,
        },
    )

    channel = fields.String(
        attribute='uploaderName',
        metadata={
            'description': 'Channel name',
            'example': 'My Channel',
        },
    )

    channel_url = fields.Url(
        attribute='uploaderUrl',
        metadata={
            'description': 'Channel URL',
            'example': 'https://youtube.com/channel/1234567890',
        },
    )

    channel_image = fields.Url(
        attribute='uploaderAvatar',
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
    def fill_urls(self, data: dict, **_):
        for attr in ('url', 'uploaderUrl'):
            if data.get(attr) and not data[attr].startswith('https://'):
                data[attr] = f'https://youtube.com{data[attr]}'

        if not data.get('id') and data.get('url'):
            data['id'] = data['url'].split('=')[-1]

        return data

    @pre_dump
    def normalize_timestamps(self, data: dict, **_):
        if data.get('uploaded') and isinstance(data['uploaded'], int):
            data['uploaded'] = datetime.fromtimestamp(data["uploaded"] / 1000)

        return data


class PipedChannelSchema(Schema):
    """
    Class for channel items returned by the Piped API.
    """

    class Meta:
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    id = fields.String(
        required=True,
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
        metadata={
            'description': 'Channel URL',
            'example': 'https://youtube.com/channel/1234567890',
        },
    )

    name = StrippedString(
        missing='[No Name]',
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
        attribute='avatar',
        metadata={
            'description': 'Channel image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    banner = fields.Url(
        attribute='bannerUrl',
        metadata={
            'description': 'Channel banner URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    subscribers = fields.Int(
        attribute='subscriberCount',
        missing=0,
        metadata={
            'description': 'Number of subscribers',
            'example': 1000,
        },
    )

    next_page_token = fields.String(
        attribute='nextpage',
        metadata={
            'description': 'The token that should be passed to get the next page of results',
            'example': '1234567890',
        },
    )

    items = fields.Nested(PipedVideoSchema, attribute='relatedStreams', many=True)

    @pre_dump
    def normalize_id_and_url(self, data: dict, **_):
        if data.get('id'):
            if not data.get('url'):
                data['url'] = f'https://youtube.com/channel/{data["id"]}'
        elif data.get('url'):
            data['id'] = data['url'].split('/')[-1]
            data['url'] = f'https://youtube.com{data["url"]}'
        else:
            raise AssertionError('Channel ID or URL not found')

        return data

    @pre_dump
    def normalize_avatar(self, data: dict, **_):
        if data.get('avatarUrl'):
            data['avatar'] = data.pop('avatarUrl')

        return data

    @pre_dump
    def serialize_next_page_token(self, data: dict, **_):
        if data.get('nextpage'):
            data['nextpage'] = base64.b64encode(data['nextpage'].encode()).decode()

        return data
