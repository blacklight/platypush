import logging

from marshmallow import Schema, fields, pre_dump, post_dump

from platypush.context import get_plugin
from platypush.schemas import DateTime

from . import MediaArtistSchema, MediaCollectionSchema, MediaVideoSchema

logger = logging.getLogger(__name__)


class JellyfinSchema(Schema):
    can_delete = fields.Boolean(attribute='CanDelete')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'id' in self.fields:
            self.fields['id'].attribute = 'Id'
        if 'path' in self.fields:
            self.fields['path'].attribute = 'Path'
        if 'name' in self.fields:
            self.fields['name'].attribute = 'Name'
        if 'title' in self.fields:
            self.fields['title'].attribute = 'Name'

    @property
    def _plugin(self):
        p = get_plugin('media.jellyfin')
        assert p, 'The media.jellyfin plugin is not configured'
        return p

    @property
    def _server(self):
        return self._plugin.server

    @property
    def _api_key(self):
        return self._plugin._api_key  # pylint: disable=protected-access

    @pre_dump
    def _gen_video_url(self, data, **_):
        data = data or {}
        if data.get('MediaType') != 'Video':
            return data

        video_format = None
        containers_priority = ['mp4', 'mkv', 'm4a', 'mov', 'avi']
        available_containers = set(data.get('Container', '').split(','))
        for container in containers_priority:
            if container in available_containers:
                video_format = container
                break

        if not video_format:
            if not available_containers:
                logger.warning(
                    'The media ID %s has no available video containers', data["Id"]
                )

                return data

            video_format = list(available_containers)[0]

        data['url'] = (
            f'{self._server}/Videos/{data["Id"]}'
            f'/stream.{video_format}'
            f'?Static=true&api_key={self._api_key}'
        )

        return data

    @pre_dump
    def _gen_audio_url(self, data, **_):
        data = data or {}
        if data.get('MediaType') != 'Audio':
            return data

        data['url'] = (
            f'{self._server}/Audio/{data["Id"]}'
            f'/stream?Static=true&api_key={self._api_key}'
        )

        return data

    @post_dump
    def gen_img_url(self, data: dict, **_) -> dict:
        data = data or {}
        if 'image' in self.fields and data.get('id') and not data.get('image'):
            data['image'] = (
                self._server + f'/Items/{data["id"]}'  # type: ignore
                '/Images/Primary?fillHeight=333&fillWidth=222&quality=96'
            )

        return data

    @post_dump
    def _normalize_duration(self, data: dict, **_) -> dict:
        if data.get('duration'):
            data['duration'] //= 1e7
        return data


class JellyfinArtistSchema(JellyfinSchema, MediaArtistSchema, MediaCollectionSchema):
    type = fields.Constant('artist')
    item_type = fields.Constant('artist')
    collection_type = fields.Constant('music')


class JellyfinTrackSchema(JellyfinSchema):
    type = fields.Constant('audio')
    item_type = fields.Constant('track')
    id = fields.String(attribute='Id')
    url = fields.URL()
    duration = fields.Number(attribute='RunTimeTicks')
    artist = fields.String()
    album = fields.String(attribute='Album')
    name = fields.String(attribute='Name')
    track_number = fields.Number(attribute='IndexNumber')
    disc_number = fields.Number(attribute='ParentIndexNumber')
    year = fields.Number(attribute='ProductionYear')
    playlist_item_id = fields.String(attribute='PlaylistItemId')
    image = fields.String()
    created_at = DateTime(attribute='DateCreated')

    @pre_dump
    def _normalize_artist(self, data: dict, **_) -> dict:
        artists = data.get('Artists', [])
        if artists:
            data['artist'] = ', '.join(artists)
        return data

    @post_dump
    def _skip_missing_playlist_item_id(self, data: dict, **_) -> dict:
        if not data.get('playlist_item_id'):
            data.pop('playlist_item_id', None)
        return data

    @post_dump
    def _normalize_community_rating(self, data: dict, **_) -> dict:
        if data.get('community_rating'):
            data['community_rating'] *= 10
        return data

    @post_dump
    def _add_title(self, data: dict, **_) -> dict:
        if not data.get('title'):
            data['title'] = data.get('name')

        return data


class JellyfinAlbumSchema(JellyfinSchema, MediaCollectionSchema):
    id = fields.String(attribute='Id')
    type = fields.Constant('album')
    item_type = fields.Constant('album')
    collection_type = fields.Constant('music')
    name = fields.String(attribute='Name')
    artist = fields.Nested(JellyfinArtistSchema, attribute='AlbumArtist')
    duration = fields.Number(attribute='RunTimeTicks')
    year = fields.Number(attribute='ProductionYear')

    @pre_dump
    def _expand_artist(self, data: dict, **_) -> dict:
        artists = data.get('AlbumArtists', [])
        if not artists:
            return data

        data['AlbumArtist'] = {
            'Id': artists[0].get('Id'),
            'Name': artists[0].get('Name'),
        }
        return data


class JellyfinCollectionSchema(JellyfinSchema, MediaCollectionSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].attribute = 'CollectionType'

    type = fields.Constant('collection')
    item_type = fields.Constant('collection')
    collection_type = fields.String(attribute='CollectionType')
    image = fields.String()
    created_at = DateTime(attribute='DateCreated')


class JellyfinVideoSchema(JellyfinSchema, MediaVideoSchema):
    type = fields.Constant('video')
    item_type = fields.Constant('video')
    duration = fields.Number(attribute='RunTimeTicks')
    community_rating = fields.Number(attribute='CommunityRating')
    container = fields.String(
        attribute='Container',
        metadata={
            'description': 'Available video containers',
            'example': 'mp4',
        },
    )
    critic_rating = fields.Number(attribute='CriticRating')
    imdb_url = fields.URL(
        attribute='ExternalUrl',
        metadata={
            'description': 'IMDb URL',
            'example': 'https://www.imdb.com/title/tt1234567/',
        },
    )

    overview = fields.String(attribute='Overview')
    genres = fields.List(fields.String, attribute='Genres')
    tags = fields.List(fields.String, attribute='Tags')
    trailer_url = fields.URL(attribute='TrailerUrl')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year'].attribute = 'ProductionYear'
        self.fields['has_subtitles'].attribute = 'HasSubtitles'
        self.fields['created_at'].attribute = 'DateCreated'

    @post_dump
    def _normalize_community_rating(self, data: dict, **_) -> dict:
        if data.get('community_rating'):
            data['community_rating'] *= 10
        return data

    @pre_dump
    def _extract_imdb_url(self, data: dict, **_) -> dict:
        external_urls = data.get('ExternalUrls', [])
        for url in external_urls:
            if url.get('Name') == 'IMDb':
                data['ExternalUrl'] = url.get('Url')
                break

        return data

    @pre_dump
    def _extract_trailer_url(self, data: dict, **_) -> dict:
        trailers = data.get('RemoteTrailers', [])
        for trailer in trailers:
            if trailer.get('Type') == 'Trailer':
                data['TrailerUrl'] = trailer.get('Url')
                break

        return data


class JellyfinMovieSchema(JellyfinVideoSchema):
    type = fields.Constant('movie')
    item_type = fields.Constant('movie')


class JellyfinEpisodeSchema(JellyfinVideoSchema):
    type = fields.Constant('episode')
    item_type = fields.Constant('episode')

    @pre_dump
    def _normalize_episode_name(self, data: dict, **_) -> dict:
        prefix = ''
        series_name = data.get('SeriesName')
        if series_name:
            prefix = series_name

        episode_index = data.get('IndexNumber')
        if episode_index:
            season_index = data.get('SeasonIndex', 1)
            episode_index = 's{:02d}e{:02d}'.format(season_index, episode_index)

        if episode_index:
            prefix += f'{" " if prefix else ""}[{episode_index}] '

        data['Name'] = prefix + data.get('Name', '')
        return data


class JellyfinPhotoSchema(JellyfinSchema):
    id = fields.String(attribute='Id')
    name = fields.String(attribute='Name')
    url = fields.URL()
    type = fields.Constant('photo')
    item_type = fields.Constant('photo')
    path = fields.String(attribute='Path')
    created_at = DateTime(attribute='PremiereDate')
    width = fields.Number(attribute='Width')
    height = fields.Number(attribute='Height')
    camera_make = fields.String(attribute='CameraMake')
    camera_model = fields.String(attribute='CameraModel')
    software = fields.String(attribute='Software')
    exposure_time = fields.Float(attribute='ExposureTime')
    focal_length = fields.Float(attribute='FocalLength')
    image_orientation = fields.String(attribute='ImageOrientation')
    aperture = fields.Float(attribute='Aperture')
    iso = fields.Number(attribute='IsoSpeedRating')

    @pre_dump
    def _gen_photo_url(self, data, **_):
        data = data or {}
        base_url = f'{self._server}/Items/{data["Id"]}'
        data['preview_url'] = (
            f'{base_url}/Images/Primary?api_key={self._api_key}'
            f'&fillHeight=489&fillWidth=367&quality=96'
        )
        data['url'] = f'{base_url}/Download?api_key={self._api_key}'
        return data


class JellyfinBookSchema(JellyfinSchema):
    id = fields.String(attribute='Id')
    name = fields.String(attribute='Name')
    url = fields.URL()
    embed_url = fields.URL()
    type = fields.Constant('book')
    item_type = fields.Constant('book')
    path = fields.String(attribute='Path')

    @pre_dump
    def _gen_book_url(self, data, **_):
        data = data or {}
        data[
            'url'
        ] = f'{self._server}/Items/{data["Id"]}/Download?api_key={self._api_key}'
        data['embed_url'] = f'{self._server}/web/#/details?id={data["Id"]}'
        return data


class JellyfinPlaylistSchema(JellyfinSchema, MediaCollectionSchema):
    id = fields.String(attribute='Id')
    type = fields.Constant('playlist')
    item_type = fields.Constant('playlist')
    collection_type = fields.Constant('music')
    name = fields.String(attribute='Name')
    image = fields.String()
    public = fields.Boolean(attribute='IsPublic')
    duration = fields.Number(attribute='RunTimeTicks')
    n_items = fields.Number(attribute='ChildCount')
    genres = fields.List(fields.String, attribute='Genres')
    tags = fields.List(fields.String, attribute='Tags')
    created_at = DateTime(attribute='DateCreated')
