from marshmallow import fields, EXCLUDE, INCLUDE
from marshmallow.schema import Schema

from platypush.schemas import DateTime, StrippedString


class TorrentResultSchema(Schema):
    """
    Schema for results returned by
    :meth:`platypush.plugins.torrent.TorrentPlugin.search`.
    """

    # pylint: disable=too-few-public-methods
    class Meta(Schema.Meta):
        """
        Schema metadata.
        """

        missing = EXCLUDE
        ordered = True
        unknown = INCLUDE

    title = StrippedString(
        required=True,
        metadata={
            'description': 'Title of the torrent',
            'example': '2001: A Space Odyssey',
        },
    )

    file = StrippedString(
        metadata={
            'description': (
                'File name of the torrent, if the resource is a local .torrent file'
            ),
            'example': '/home/user/downloads/2001_a_space_odyssey.torrent',
        },
    )

    url = StrippedString(
        metadata={
            'description': 'URL of the torrent, if the resource is a remote torrent',
            'example': 'magnet:?xt=urn:btih:...',
        },
    )

    provider = StrippedString(
        metadata={
            'description': (
                'Provider of the torrent - e.g. `popcorntime`, `yts` or `torrent-csv`'
            ),
            'example': 'popcorntime',
        },
    )

    type = StrippedString(
        metadata={
            'description': 'Type of the torrent',
            'example': 'movies',
        },
    )

    is_media = fields.Boolean(
        metadata={
            'description': 'True if the torrent is a media file',
            'example': True,
        },
    )

    size = fields.Integer(
        missing=0,
        metadata={
            'description': 'Size of the torrent in bytes',
            'example': 123456789,
        },
    )

    duration = fields.Float(
        metadata={
            'description': 'Duration of the torrent in seconds, if applicable',
            'example': 123.45,
        },
    )

    language = StrippedString(
        metadata={
            'description': 'Language of the torrent',
            'example': 'en',
        },
    )

    seeds = fields.Integer(
        missing=0,
        metadata={
            'description': 'Number of seeders',
            'example': 123,
        },
    )

    peers = fields.Integer(
        missing=0,
        metadata={
            'description': 'Number of peers',
            'example': 123,
        },
    )

    image = StrippedString(
        metadata={
            'description': 'URL of the image associated to the torrent',
            'example': 'https://example.com/image.jpg',
        },
    )

    description = StrippedString(
        metadata={
            'description': 'Description of the torrent',
            'example': 'A description of the torrent',
        },
    )

    imdb_id = StrippedString(
        metadata={
            'description': 'IMDb ID of the torrent, if applicable',
            'example': 'tt0062622',
        },
    )

    tvdb_id = StrippedString(
        metadata={
            'description': 'TVDB ID of the torrent, if applicable',
            'example': '76283',
        },
    )

    year = fields.Integer(
        metadata={
            'description': 'Year of the release of the underlying product, if applicable',
            'example': 1968,
        },
    )

    created_at = DateTime(
        metadata={
            'description': 'Creation date of the torrent',
            'example': '2021-01-01T00:00:00',
        },
    )

    quality = StrippedString(
        metadata={
            'description': 'Quality of the torrent, if video/audio',
            'example': '1080p',
        },
    )

    overview = StrippedString(
        metadata={
            'description': 'Overview of the torrent, if it is a TV show',
            'example': 'Overview of the torrent, if it is a TV show',
        },
    )

    trailer = fields.URL(
        metadata={
            'description': 'URL of the trailer of the torrent, if available',
            'example': 'https://example.com/trailer.mp4',
        },
    )

    genres = fields.List(
        fields.String(),
        metadata={
            'description': 'List of genres associated to the torrent',
            'example': ['Sci-Fi', 'Adventure'],
        },
    )

    rating = fields.Float(
        metadata={
            'description': (
                'Rating of the torrent or the underlying product, as a '
                'percentage between 0 and 100'
            ),
            'example': 86.0,
        },
    )

    critic_rating = fields.Float(
        metadata={
            'description': 'Critic rating, if applicable, as a percentage between 0 and 100',
            'example': 86.0,
        },
    )

    community_rating = fields.Float(
        metadata={
            'description': (
                'Community rating, if applicable, as a percentage between 0 and 100'
            ),
            'example': 86.0,
        },
    )

    votes = fields.Integer(
        metadata={
            'description': 'Number of votes, if applicable',
            'example': 123,
        },
    )

    series = StrippedString(
        metadata={
            'description': 'Title of the TV series, if applicable',
            'example': 'Breaking Bad',
        },
    )

    season = fields.Integer(
        metadata={
            'description': 'Season number of the TV series, if applicable',
            'example': 1,
        },
    )

    episode = fields.Integer(
        metadata={
            'description': 'Episode number of the TV series, if applicable',
            'example': 1,
        },
    )

    num_seasons = fields.Integer(
        metadata={
            'description': 'Number of seasons of the TV series, if applicable',
            'example': 5,
        },
    )

    country = StrippedString(
        metadata={
            'description': 'Country of origin of the torrent or the underlying product',
            'example': 'USA',
        },
    )

    network = StrippedString(
        metadata={
            'description': 'Network of the TV series, if applicable',
            'example': 'AMC',
        },
    )

    series_status = StrippedString(
        metadata={
            'description': 'Status of the TV series, if applicable',
            'example': 'Ended',
        },
    )
