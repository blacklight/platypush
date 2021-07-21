from datetime import datetime
from typing import Union

from marshmallow import fields, pre_dump
from marshmallow.schema import Schema
from marshmallow.validate import OneOf, Range

from platypush.plugins.media import PlayerState
from platypush.schemas import normalize_datetime

device_types = [
    'Unknown',
    'Computer',
    'Tablet',
    'Smartphone',
    'Speaker',
    'TV',
    'AVR',
    'STB',
    'Audio dongle',
]


class SpotifySchema(Schema):
    @staticmethod
    def _normalize_timestamp(t: Union[str, datetime]) -> datetime:
        if isinstance(t, str):
            # Replace the "Z" suffix with "+00:00"
            t = datetime.fromisoformat(t[:-1] + '+00:00')

        return t

    @pre_dump
    def _extract_url(self, data, **_):
        url = data.get('external_urls', {}).get('spotify')
        if url:
            data['url'] = url

        return data


class SpotifyDeviceSchema(SpotifySchema):
    id = fields.String(required=True, dump_only=True, metadata=dict(description='Device unique ID'))
    name = fields.String(required=True, metadata=dict(description='Device name'))
    type = fields.String(attribute='deviceType', required=True, validate=OneOf(device_types),
                         metadata=dict(description=f'Supported types: [{", ".join(device_types)}]'))
    volume = fields.Int(attribute='volume_percent', validate=Range(min=0, max=100),
                        metadata=dict(description='Player volume in percentage [0-100]'))
    is_active = fields.Boolean(required=True, dump_only=True,
                               metadata=dict(description='True if the device is currently active'))
    is_restricted = fields.Boolean(required=True, metadata=dict(description='True if the device has restricted access'))
    is_private_session = fields.Boolean(required=False,
                                        metadata=dict(description='True if the device is currently playing a private '
                                                                  'session'))


class SpotifyTrackSchema(SpotifySchema):
    id = fields.String(required=True, dump_only=True, metadata=dict(description='Spotify ID'))
    uri = fields.String(required=True, dump_only=True, metadata=dict(description='Spotify URI'))
    url = fields.String(dump_only=True, metadata=dict(description='Spotify URL'))
    file = fields.String(required=True, dump_only=True,
                         metadata=dict(description='Cross-compatibility file ID (same as uri)'))
    title = fields.String(attribute='name', required=True, metadata=dict(description='Track title'))
    artist = fields.String(metadata=dict(description='Track artist'))
    album = fields.String(metadata=dict(description='Track album'))
    image_url = fields.String(metadata=dict(description='Album image URL'))
    date = fields.Int(metadata=dict(description='Track year release date'))
    track = fields.Int(attribute='track_number', metadata=dict(description='Album track number'))
    duration = fields.Float(metadata=dict(description='Track duration in seconds'))
    popularity = fields.Int(metadata=dict(description='Popularity between 0 and 100'))
    type = fields.Constant('track', metadata=dict(description='track'))

    @pre_dump
    def normalize_fields(self, data, **_):
        album = data.pop('album', {})
        if album and isinstance(album, dict):
            data['album'] = album['name']
            data['date'] = int(album.get('release_date', '').split('-')[0])
            data['x-albumuri'] = album['uri']
            if album.get('images'):
                data['image_url'] = album['images'][0]['url']

        artists = data.pop('artists', [])
        if artists:
            data['artist'] = '; '.join([
                artist['name'] for artist in artists
            ])

        duration_ms = data.pop('duration_ms', None)
        if duration_ms:
            data['duration'] = duration_ms/1000.

        return data


class SpotifyAlbumSchema(SpotifySchema):
    id = fields.String(required=True, dump_only=True, metadata=dict(description='Spotify ID'))
    uri = fields.String(required=True, dump_only=True, metadata=dict(description='Spotify URI'))
    url = fields.String(dump_only=True, metadata=dict(description='Spotify URL'))
    name = fields.String(required=True, metadata=dict(description='Name/title'))
    artist = fields.String(metadata=dict(description='Artist'))
    image_url = fields.String(metadata=dict(description='Image URL'))
    date = fields.Int(metadata=dict(description='Release date'))
    tracks = fields.Nested(SpotifyTrackSchema, many=True, metadata=dict(description='List of tracks on the album'))
    popularity = fields.Int(metadata=dict(description='Popularity between 0 and 100'))
    type = fields.Constant('album', metadata=dict(description='album'))

    @pre_dump
    def normalize(self, data, **_):
        album = data.pop('album', data)
        tracks = album.pop('tracks', {}).pop('items', [])
        if tracks:
            album['tracks'] = tracks

        artists = album.pop('artists', [])
        if artists:
            album['artist'] = ';'.join([artist['name'] for artist in artists])

        date = album.pop('release_date', None)
        if date:
            album['date'] = date.split('-')[0]

        images = album.pop('images', [])
        if images:
            album['image_url'] = images[0]['url']

        return album


class SpotifyUserSchema(SpotifySchema):
    id = fields.String(required=True, dump_only=True)
    display_name = fields.String(required=True)
    uri = fields.String(required=True, dump_only=True)


class SpotifyPlaylistTrackSchema(SpotifyTrackSchema):
    position = fields.Int(validate=Range(min=1), metadata=dict(description='Position of the track in the playlist'))
    added_at = fields.DateTime(metadata=dict(description='When the track was added to the playlist'))
    added_by = fields.Nested(SpotifyUserSchema, metadata=dict(description='User that added the track'))
    type = fields.Constant('playlist', metadata=dict(description='playlist'))


class SpotifyStatusSchema(SpotifySchema):
    device_id = fields.String(required=True, dump_only=True, metadata=dict(description='Playing device unique ID'))
    device_name = fields.String(required=True, metadata=dict(description='Playing device name'))
    state = fields.String(required=True, validate=OneOf([s.value for s in PlayerState]),
                          metadata=dict(description=f'Supported types: [{", ".join([s.value for s in PlayerState])}]'))
    volume = fields.Int(validate=Range(min=0, max=100), required=False,
                        metadata=dict(description='Player volume in percentage [0-100]'))
    elapsed = fields.Float(required=False, metadata=dict(description='Time elapsed into the current track'))
    time = fields.Float(required=False, metadata=dict(description='Duration of the current track'))
    repeat = fields.Boolean(metadata=dict(description='True if the device is in repeat mode'))
    random = fields.Boolean(attribute='shuffle_state',
                            metadata=dict(description='True if the device is in shuffle mode'))
    track = fields.Nested(SpotifyTrackSchema, metadata=dict(description='Information about the current track'))

    @pre_dump
    def normalize_fields(self, data, **_):
        device = data.pop('device', {})
        if device:
            data['device_id'] = device['id']
            data['device_name'] = device['name']
            if device.get('volume_percent') is not None:
                data['volume'] = device['volume_percent']

        elapsed = data.pop('progress_ms', None)
        if elapsed is not None:
            data['elapsed'] = int(elapsed)/1000.

        track = data.pop('item', {})
        if track:
            data['track'] = track
            duration = track.get('duration_ms')
            if duration is not None:
                data['time'] = int(duration)/1000.

        is_playing = data.pop('is_playing', None)
        if is_playing is True:
            data['state'] = PlayerState.PLAY.value
        elif is_playing is False:
            data['state'] = PlayerState.PAUSE.value

        repeat = data.pop('repeat_state', None)
        data['repeat'] = False if (not repeat or repeat == 'off') else True
        return data


class SpotifyHistoryItemSchema(SpotifyTrackSchema):
    played_at = fields.DateTime(metadata=dict(description='Item play datetime'))

    @pre_dump
    def _normalize_timestamps(self, data, **_):
        played_at = data.pop('played_at', None)
        if played_at:
            data['played_at'] = self._normalize_timestamp(played_at)

        return data


class SpotifyPlaylistSchema(SpotifySchema):
    id = fields.String(required=True, dump_only=True)
    uri = fields.String(required=True, dump_only=True, metadata=dict(
        description='Playlist unique Spotify URI'
    ))
    url = fields.String(dump_only=True, metadata=dict(description='Spotify URL'))
    name = fields.String(required=True)
    description = fields.String()
    owner = fields.Nested(SpotifyUserSchema, metadata=dict(
        description='Playlist owner data'
    ))
    collaborative = fields.Boolean()
    public = fields.Boolean()
    snapshot_id = fields.String(dump_only=True, metadata=dict(
        description='Playlist snapshot ID - it changes when the playlist is modified'
    ))
    tracks = fields.Nested(SpotifyPlaylistTrackSchema, many=True, metadata=dict(
        description='List of tracks in the playlist'
    ))

    @pre_dump
    def _normalize_tracks(self, data, **_):
        if 'tracks' in data:
            if not isinstance(data['tracks'], list):
                data.pop('tracks')
            else:
                data['tracks'] = [
                    {
                        **track['track'],
                        'added_at': normalize_datetime(track.get('added_at')),
                        'added_by': track.get('added_by'),
                    }
                    if isinstance(track.get('track'), dict) else track
                    for track in data['tracks']
                ]

        return data


class SpotifyEpisodeSchema(SpotifyTrackSchema):
    description = fields.String(metadata=dict(description='Episode description'))
    show = fields.String(metadata=dict(description='Episode show name'))
    type = fields.Constant('episode', metadata=dict(description='episode'))

    @pre_dump
    def normalize_fields(self, data, **_):
        data = data.pop('episode', data)

        # Cross-compatibility with SpotifyTrackSchema
        show = data.pop('show', {})
        data['artist'] = data['album'] = data['show'] = show.get('name')
        data['x-albumuri'] = show['uri']
        images = data.pop('images', show.pop('images', []))
        if images:
            data['image_url'] = images[0]['url']

        return data


class SpotifyShowSchema(SpotifyAlbumSchema):
    description = fields.String(metadata=dict(description='Show description'))
    publisher = fields.String(metadata=dict(description='Show publisher name'))
    type = fields.Constant('show', metadata=dict(description='show'))

    @pre_dump
    def normalize_fields(self, data, **_):
        data = data.pop('show', data)

        # Cross-compatibility with SpotifyAlbumSchema
        data['artist'] = data.get('publisher', data.get('name'))
        images = data.pop('images', [])
        if images:
            data['image_url'] = images[0]['url']

        return data


class SpotifyArtistSchema(SpotifySchema):
    id = fields.String(metadata=dict(description='Spotify ID'))
    uri = fields.String(metadata=dict(description='Spotify URI'))
    url = fields.String(dump_only=True, metadata=dict(description='Spotify URL'))
    name = fields.String(metadata=dict(description='Artist name'))
    genres = fields.List(fields.String, metadata=dict(description='Artist genres'))
    popularity = fields.Int(metadata=dict(description='Popularity between 0 and 100'))
    image_url = fields.String(metadata=dict(description='Image URL'))
    type = fields.Constant('artist', metadata=dict(description='artist'))

    @pre_dump
    def normalize_fields(self, data, **_):
        data = data.pop('artist', data)
        images = data.pop('images', [])
        if images:
            data['image_url'] = images[0]['url']

        return data
