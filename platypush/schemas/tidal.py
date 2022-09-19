from marshmallow import Schema, fields, pre_dump, post_dump

from platypush.schemas import DateTime


class TidalSchema(Schema):
    pass


class TidalArtistSchema(TidalSchema):
    id = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'example': '3288612',
            'description': 'Artist ID',
        },
    )

    url = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'description': 'Artist Tidal URL',
            'example': 'https://tidal.com/artist/3288612',
        },
    )

    name = fields.String(required=True)

    @pre_dump
    def _prefill_url(self, data, *_, **__):
        data.url = f'https://tidal.com/artist/{data.id}'
        return data


class TidalAlbumSchema(TidalSchema):
    def __init__(self, *args, with_tracks=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._with_tracks = with_tracks

    id = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'example': '45288612',
            'description': 'Album ID',
        },
    )

    url = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'description': 'Album Tidal URL',
            'example': 'https://tidal.com/album/45288612',
        },
    )

    name = fields.String(required=True)
    artist = fields.Nested(TidalArtistSchema)
    duration = fields.Int(metadata={'description': 'Album duration, in seconds'})
    year = fields.Integer(metadata={'example': 2003})
    num_tracks = fields.Int(metadata={'example': 10})
    tracks = fields.List(fields.Dict(), attribute='_tracks')

    @pre_dump
    def _prefill_url(self, data, *_, **__):
        data.url = f'https://tidal.com/album/{data.id}'
        return data

    @pre_dump
    def _cache_tracks(self, data, *_, **__):
        if self._with_tracks:
            album_id = str(data.id)
            self.context[album_id] = {
                'tracks': data.tracks(),
            }

        return data

    @post_dump
    def _dump_tracks(self, data, *_, **__):
        if self._with_tracks:
            album_id = str(data['id'])
            ctx = self.context.pop(album_id, {})
            data['tracks'] = TidalTrackSchema().dump(ctx.pop('tracks', []), many=True)

        return data


class TidalTrackSchema(TidalSchema):
    id = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'example': '25288614',
            'description': 'Track ID',
        },
    )

    url = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'description': 'Track Tidal URL',
            'example': 'https://tidal.com/track/25288614',
        },
    )

    artist = fields.Nested(TidalArtistSchema)
    album = fields.Nested(TidalAlbumSchema)
    name = fields.String(metadata={'description': 'Track title'})
    duration = fields.Int(metadata={'description': 'Track duration, in seconds'})
    track_num = fields.Int(
        metadata={'description': 'Index of the track within the album'}
    )

    @pre_dump
    def _prefill_url(self, data, *_, **__):
        data.url = f'https://tidal.com/track/{data.id}'
        return data


class TidalPlaylistSchema(TidalSchema):
    id = fields.String(
        required=True,
        dump_only=True,
        attribute='uuid',
        metadata={
            'example': '2b288612-34f5-11ed-b42d-001500e8f607',
            'description': 'Playlist ID',
        },
    )

    url = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'description': 'Playlist Tidal URL',
            'example': 'https://tidal.com/playlist/2b288612-34f5-11ed-b42d-001500e8f607',
        },
    )

    name = fields.String(required=True)
    description = fields.String()
    duration = fields.Int(metadata={'description': 'Playlist duration, in seconds'})
    public = fields.Boolean(attribute='publicPlaylist')
    owner = fields.String(
        attribute='creator',
        metadata={
            'description': 'Playlist creator/owner ID',
        },
    )

    num_tracks = fields.Int(
        attribute='numberOfTracks',
        default=0,
        metadata={
            'example': 42,
            'description': 'Number of tracks in the playlist',
        },
    )

    created_at = DateTime(
        attribute='created',
        metadata={
            'description': 'When the playlist was created',
        },
    )

    last_updated_at = DateTime(
        attribute='lastUpdated',
        metadata={
            'description': 'When the playlist was last updated',
        },
    )

    tracks = fields.Nested(TidalTrackSchema, many=True)

    def _flatten_object(self, data, *_, **__):
        if not isinstance(data, dict):
            data = {
                'created': data.created,
                'creator': data.creator.id,
                'description': data.description,
                'duration': data.duration,
                'lastUpdated': data.last_updated,
                'uuid': data.id,
                'name': data.name,
                'numberOfTracks': data.num_tracks,
                'publicPlaylist': data.public,
                'tracks': getattr(data, '_tracks', []),
            }

        return data

    def _normalize_owner(self, data, *_, **__):
        owner = data.pop('owner', data.pop('creator', None))
        if owner:
            if isinstance(owner, dict):
                owner = owner['id']
            data['creator'] = owner

        return data

    def _normalize_name(self, data, *_, **__):
        if data.get('title'):
            data['name'] = data.pop('title')
        return data

    @pre_dump
    def normalize(self, data, *_, **__):
        if not isinstance(data, dict):
            data = self._flatten_object(data)

        self._normalize_name(data)
        self._normalize_owner(data)
        if 'tracks' not in data:
            data['tracks'] = []
        return data


class TidalSearchResultsSchema(TidalSchema):
    artists = fields.Nested(TidalArtistSchema, many=True)
    albums = fields.Nested(TidalAlbumSchema, many=True)
    tracks = fields.Nested(TidalTrackSchema, many=True)
    playlists = fields.Nested(TidalPlaylistSchema, many=True)
