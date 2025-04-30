import re
from typing import Collection, Optional, Union

from marshmallow import EXCLUDE, fields, pre_dump
from marshmallow.schema import Schema

from platypush.schemas import DateTime, StrippedString


def _get_image(data: dict, **_) -> Optional[str]:
    return next(
        iter(
            data.get(quality, {}).get('url')
            for quality in ['high', 'medium', 'standard', 'default', 'maxres']
            if data.get(quality)
        ),
        None,
    )


def yt_time(duration: Optional[Union[str, int]]) -> Optional[int]:
    """
    Converts YouTube duration (ISO 8061) into seconds.

    See http://en.wikipedia.org/wiki/ISO_8601#Durations
    See https://stackoverflow.com/questions/16742381/how-to-convert-youtube-api-duration-to-seconds#
    """
    if duration is None or isinstance(duration, int):
        return duration

    ISO_8601 = re.compile(
        'P'  # designates a period
        r'(?:(?P<years>\d+)Y)?'  # years
        r'(?:(?P<months>\d+)M)?'  # months
        r'(?:(?P<weeks>\d+)W)?'  # weeks
        r'(?:(?P<days>\d+)D)?'  # days
        r'(?:T'  # time part must begin with a T
        r'(?:(?P<hours>\d+)H)?'  # hours
        r'(?:(?P<minutes>\d+)M)?'  # minutes
        r'(?:(?P<seconds>\d+)S)?'  # seconds
        ')?'
    )  # end of time part

    m = ISO_8601.match(duration)
    if not m:
        return None

    # Convert regex matches into a short list of time units
    units = list(m.groups()[-3:])
    # Put list in ascending order & remove 'None' types
    units = list(reversed([int(x) if x is not None else 0 for x in units]))
    # Do the maths
    return int(sum(x * 60 ** units.index(x) for x in units))


class YoutubeVideoSchema(Schema):
    """
    Class for video items returned by the Youtube API.
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
        metadata={
            'description': 'Video description',
            'example': 'My video description',
        },
    )

    duration = fields.Int(
        load_default=0,
        metadata={
            'description': 'Video duration in seconds',
            'example': 120,
        },
    )

    channel = fields.String(
        metadata={
            'description': 'Channel name',
            'example': 'My Channel',
        },
    )

    channel_url = fields.Url(
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
        metadata={
            'description': "Index ID of the video",
            'example': '1234567890abcdef',
        },
    )

    created_at = DateTime(
        metadata={
            'description': 'Video upload date',
            'example': '2020-01-01T00:00:00',
        },
    )

    next_page_token = fields.String(
        metadata={
            'description': (
                'If the video is retrieved within the context of a list of search results, '
                'this is the token that should be passed to get the next page of results',
            ),
            'example': '1234567890',
        },
    )

    @pre_dump
    def fill_ids_and_url(self, data: dict, **_):
        # Check if it's a video or a playlist item
        if data.get('snippet', {}).get('resourceId', {}).get('kind') == 'youtube#video':
            data['id'] = data['snippet']['resourceId']['videoId']
            data['index_id'] = data['id']

        data['url'] = f'https://youtube.com/watch?v={data["id"]}'
        return data

    @pre_dump
    def fill_image(self, data: dict, **_):
        data['image'] = _get_image(data.get('snippet', {}).get('thumbnails', {}))
        return data

    @pre_dump
    def fill_timestamp(self, data: dict, **_):
        data['created_at'] = data.get('snippet', {}).get('publishedAt')
        return data

    @pre_dump
    def fill_index(self, data: dict, **_):
        if data.get('snippet', {}).get('position') is not None:
            data['index'] = data['snippet']['position']
        return data

    @pre_dump
    def fill_channel(self, data: dict, **_):
        snippet = data.get('snippet', {})
        if snippet.get('videoOwnerChannelId'):
            data['channel'] = snippet.get(
                'videoOwnerChannelTitle', snippet.get('channelTitle', '[No Channel]')
            )
            data[
                'channel_url'
            ] = f'https://youtube.com/channel/{snippet["videoOwnerChannelId"]}'
        else:
            data['channel'] = snippet.get('channelTitle', '[No Channel]')
            data['channel_url'] = 'https://youtube.com/channel/' + snippet.get(
                'channelId', ''
            )

        return data

    @pre_dump
    def fill_metadata(self, data: dict, **_):
        data['title'] = data.get('snippet', {}).get('title', '[No Title]')
        data['description'] = data.get('snippet', {}).get('description')
        details = data.get('contentDetails', {})
        if details.get('duration') is not None:
            data['duration'] = yt_time(details['duration'])

        return data


class YoutubePlaylistSchema(Schema):
    """
    Class for playlist items returned by the Youtube API.
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
        metadata={
            'description': 'Playlist ID',
            'example': '1234567890abcdef',
        },
    )

    name = fields.String(
        load_default='[No Name]',
        metadata={
            'description': 'Playlist name',
            'example': 'My Playlist Name',
        },
    )

    description = StrippedString(
        metadata={
            'description': 'Playlist description',
            'example': 'My playlist description',
        },
    )

    image = fields.Url(
        metadata={
            'description': 'Image URL',
            'example': 'https://i.ytimg.com/vi/1234567890/hqdefault.jpg',
        },
    )

    channel = fields.String(
        metadata={
            'description': 'Channel name',
            'example': 'My Channel',
        },
    )

    channel_url = fields.Url(
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

    videos = fields.Int(
        load_default=0,
        metadata={
            'description': 'Number of videos in the playlist',
            'example': 10,
        },
    )

    next_page_token = fields.String(
        metadata={
            'description': 'The token that should be passed to get the next page of results',
            'example': '1234567890',
        },
    )

    @pre_dump
    def extract_snippets(self, data: dict, **_):
        snippet = data.get('snippet', {})
        if not snippet:
            return data

        localized = snippet.get('localized', {})
        if localized:
            data['name'] = localized.get('title')
            data['description'] = localized.get('description')

        data['name'] = data.get('title', snippet.get('title', '[No Name]'))
        data['description'] = data.get(
            'description', snippet.get('description', '[No Description]')
        )
        data['channel'] = snippet.get('channelTitle', '[No Channel]')
        return data

    @pre_dump
    def fill_url(self, data: dict, **_):
        if data.get('id'):
            data['url'] = f'https://youtube.com/playlist?list={data["id"]}'

        if data.get('snippet', {}).get('channelId'):
            data[
                'channel_url'
            ] = f'https://youtube.com/channel/{data["snippet"]["channelId"]}'

        return data

    @pre_dump
    def fill_image(self, data: dict, **_):
        data['image'] = _get_image(data.get('snippet', {}).get('thumbnails', {}))
        return data

    @pre_dump
    def fill_content_details(self, data: dict, **_):
        content_details = data.get('contentDetails', {})
        data['videos'] = content_details.get('itemCount', 0)
        return data


class YoutubeChannelSchema(Schema):
    """
    Class for channel items returned by the Youtube API.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
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

    name = fields.String(
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
        load_default=0,
        metadata={
            'description': 'Number of subscribers',
            'example': 1000,
        },
    )

    next_page_token = fields.String(
        metadata={
            'description': 'The token that should be passed to get the next page of results',
            'example': '1234567890',
        },
    )

    items = fields.List(
        fields.Nested(YoutubeVideoSchema),
        metadata={
            'description': 'List of videos',
        },
    )

    count = fields.Int(
        load_default=0,
        metadata={
            'description': 'Total number of videos published by the channel',
            'example': 10,
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

        if data.get('authorThumbnails'):
            data['image'] = get_image(data['authorThumbnails'])
        elif data.get('snippet', {}).get('thumbnails'):
            data['image'] = next(
                iter(
                    data['snippet']['thumbnails'].get(quality, {}).get('url')
                    for quality in ['high', 'medium', 'standard', 'default', 'maxres']
                    if data['snippet']['thumbnails'].get(quality)
                ),
                None,
            )

        return data

    @pre_dump
    def default_items(self, data: dict, **_):
        data['items'] = data.get('items', [])
        return data

    @pre_dump
    def fill_name(self, data: dict, **_):
        data['name'] = data.get('snippet', {}).get('title', '[No Name]')
        return data

    @pre_dump
    def fill_url(self, data: dict, **_):
        snippet = data.get('snippet', {})
        if snippet.get('resourceId', {}).get('channelId'):
            data[
                'url'
            ] = f'https://youtube.com/channel/{snippet["resourceId"]["channelId"]}'
        elif snippet.get('channelId'):
            data['url'] = f'https://youtube.com/channel/{snippet["channelId"]}'
        elif data.get('id'):
            data['url'] = f'https://youtube.com/channel/{data["id"]}'

        return data

    @pre_dump
    def fill_stats(self, data: dict, **_):
        data['subscribers'] = data.get('statistics', {}).get('subscriberCount', 0)
        data['count'] = data.get('statistics', {}).get('videoCount', 0)
        return data
