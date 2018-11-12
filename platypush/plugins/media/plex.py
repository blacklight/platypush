from plexapi.myplex import MyPlexAccount
from plexapi.video import Movie, Show

from platypush.plugins import Plugin, action


class MediaPlexPlugin(Plugin):
    """
    Plugin to interact with a Plex media server

    Requires:

        * **plexapi** (``pip install plexapi``)
    """

    def __init__(self, server, username, password, *args, **kwargs):
        """
        :param server: Plex server name
        :type server: str

        :param username: Plex username
        :type username: str

        :param password: Plex password
        :type username: str
        """

        super().__init__(*args, **kwargs)

        self.resource = MyPlexAccount(username, password).resource(server)
        self._plex = None


    @property
    def plex(self):
        if not self._plex:
            self._plex = self.resource.connect()

        return self._plex


    @action
    def get_clients(self):
        """
        Get the list of active clients
        """

        return [{
            'device': c.device,
            'device_class': c.deviceClass,
            'local': c.local,
            'model': c.model,
            'platform': c.platform,
            'platform_version': c.platformVersion,
            'product': c.product,
            'state': c.state,
            'title': c.title,
            'version': c.version,
        } for c in self.plex.clients()]


    def _get_client(self, name):
        return self.plex.client(name)


    @action
    def search(self, section=None, title=None, **kwargs):
        """
        Return all the items matching the search criteria (default: all library items)

        :param section: Section to search (Movies, Shows etc.)
        :type section: str

        :param title: Full or partial title
        :type title: str

        :param kwargs: Search criteria - includes e.g. title, unwatched, director, genre etc.
        :type kwargs: dict
        """

        ret = []
        library = self.plex.library

        if section:
            library = library.section(section)

        if title or kwargs:
            items = library.search(title, **kwargs)
        else:
            items = library.all()

        for item in items:
            video_item = {
                'summary': item.summary,
                'title': item.title,
                'type': item.type,
                'rating': item.rating,
            }

            if isinstance(item, Movie):
                video_item['is_watched'] = item.isWatched
                video_item['view_offset'] = item.viewOffset
                video_item['view_count'] = item.viewCount
                video_item['year'] = item.year

                video_item['media'] = [
                    {
                        'duration': (item.media[i].duration or 0)/1000,
                        'width': item.media[i].width,
                        'height': item.media[i].height,
                        'audio_channels': item.media[i].audioChannels,
                        'audio_codec': item.media[i].audioCodec,
                        'video_codec': item.media[i].videoCodec,
                        'video_resolution': item.media[i].videoResolution,
                        'video_frame_rate': item.media[i].videoFrameRate,
                        'parts': [
                            {
                                'file': part.file,
                                'duration': (part.duration or 0)/1000,
                            } for part in item.media[i].parts
                        ]
                    } for i in range(0, len(item.media))
                ]
            elif isinstance(item, Show):
                video_item['media'] = [
                    {
                        'title': season.title,
                        'season_number': season.seasonNumber,
                        'summary': season.summary,
                        'episodes': [
                            {
                                'duration': episode.duration/1000,
                                'index': episode.index,
                                'year': episode.year,
                                'season_number': episode.seasonNumber,
                                'season_episode': episode.seasonEpisode,
                                'summary': episode.summary,
                                'is_watched': episode.isWatched,
                                'view_count': episode.viewCount,
                                'view_offset': episode.viewOffset,
                                'media': [
                                    {
                                        'duration': episode.media[i].duration/1000,
                                        'width': episode.media[i].width,
                                        'height': episode.media[i].height,
                                        'audio_channels': episode.media[i].audioChannels,
                                        'audio_codec': episode.media[i].audioCodec,
                                        'video_codec': episode.media[i].videoCodec,
                                        'video_resolution': episode.media[i].videoResolution,
                                        'video_frame_rate': episode.media[i].videoFrameRate,
                                        'title': episode.title,
                                        'parts': [
                                            {
                                                'file': part.file,
                                                'duration': part.duration/1000,
                                            } for part in episode.media[i].parts
                                        ]
                                    } for i in range(0, len(episode.locations))
                                ]
                            } for episode in season.episodes()
                        ]
                    } for season in item.seasons()
                ]

            ret.append(video_item)

        return ret


# vim:sw=4:ts=4:et:

