import logging

from marshmallow import Schema, fields, pre_dump, post_dump

from platypush.context import get_plugin

from . import MediaArtistSchema, MediaCollectionSchema, MediaVideoSchema

logger = logging.getLogger(__name__)


class JellyfinSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'id' in self.fields:
            self.fields['id'].attribute = 'Id'
        if 'name' in self.fields:
            self.fields['name'].attribute = 'Name'
        elif 'title' in self.fields:
            self.fields['title'].attribute = 'Name'

    @post_dump
    def gen_img_url(self, data: dict, **_) -> dict:
        if 'image' in self.fields:
            plugin = get_plugin('media.jellyfin')
            assert plugin, 'The media.jellyfin plugin is not configured'
            data['image'] = (
                plugin.server + f'/Items/{data["id"]}'  # type: ignore
                '/Images/Primary?fillHeight=333&fillWidth=222&quality=96'
            )

        return data

    @pre_dump
    def _gen_video_url(self, data, **_):
        if data.get('MediaType') != 'Video':
            return data

        video_format = None
        containers_priority = ['mp4', 'mkv', 'm4a', 'mov', 'avi']
        available_containers = data.get('Container', '').split(',')
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

            video_format = available_containers[0]

        plugin = get_plugin('media.jellyfin')
        assert plugin, 'The media.jellyfin plugin is not configured'
        data['url'] = (
            f'{plugin.server}/Videos/{data["Id"]}'
            f'/stream.{video_format}'
            f'?Static=true&api_key={plugin._api_key}'
        )

        return data


class JellyfinArtistSchema(JellyfinSchema, MediaArtistSchema):
    pass


class JellyfinCollectionSchema(JellyfinSchema, MediaCollectionSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].attribute = 'CollectionType'


class JellyfinVideoSchema(JellyfinSchema, MediaVideoSchema):
    duration = fields.Number(attribute='RunTimeTicks')
    community_rating = fields.Number(attribute='CommunityRating')
    critic_rating = fields.Number(attribute='CriticRating')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year'].attribute = 'ProductionYear'
        self.fields['has_subtitles'].attribute = 'HasSubtitles'

    @post_dump
    def _normalize_community_rating(self, data: dict, **_) -> dict:
        if data.get('community_rating'):
            data['community_rating'] *= 10
        return data

    @post_dump
    def _normalize_duration(self, data: dict, **_) -> dict:
        if data.get('duration'):
            data['duration'] //= 1e7
        return data


class JellyfinMovieSchema(JellyfinVideoSchema):
    pass


class JellyfinEpisodeSchema(JellyfinVideoSchema):
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
