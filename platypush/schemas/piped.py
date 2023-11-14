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
