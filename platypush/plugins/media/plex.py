from platypush.context import get_plugin
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

        from plexapi.myplex import MyPlexAccount
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
            ret.append(self._flatten_item(item))

        return ret


    @action
    def playlists(self):
        """
        Get the playlists on the server
        """

        return [
            {
                'title': pl.title,
                'duration': pl.duration,
                'summary': pl.summary,
                'viewed_at': pl.viewedAt,
                'items': [ self._flatten_item(item) for item in pl.items() ],
            } for pl in self.plex.playlists()
        ]


    @action
    def history(self):
        """
        Get the history of items played on the server
        """

        return [
            self._flatten_item(item) for item in self.plex.history()
        ]


    def get_chromecast(self, chromecast):
        from .lib.plexcast import PlexController

        hndl = PlexController()
        hndl.namespace = 'urn:x-cast:com.google.cast.sse'
        cast = get_plugin('media.chromecast').get_chromecast(chromecast)
        cast.register_handler(hndl)

        return (cast, hndl)


    @action
    def play(self, client=None, chromecast=None, **kwargs):
        """
        Search and play content on a client or a Chromecast. If no search filter
        is specified, a play event will be sent to the specified client.

        NOTE: Adding and managing play queues through the Plex API isn't fully
        supported yet, therefore in case multiple items are returned from the
        search only the first one will be played.

        :param client: Client name
        :type client: str

        :param chromecast: Chromecast name
        :type chromecast: str

        :param kwargs: Search filter (e.g. title, section, unwatched, director etc.)
        :type kwargs: dict
        """

        if not client and not chromecast:
            raise RuntimeError('No client nor chromecast specified')

        if client:
            client = plex.client(client)
        elif chromecast:
            (chromecast, handler) = self.get_chromecast(chromecast)

        if not kwargs:
            if client:
                return client.play()
            elif chromecast:
                return handler.play()

        if 'section' in kwargs:
            library = self.plex.library.section(kwargs.pop('section'))
        else:
            library = self.plex.library

        results = library.search(**kwargs)
        if not results:
            self.logger.info('No results for {}'.format(kwargs))
            return

        item = results[0]
        self.logger.info('Playing {} on {}'.format(item.title, client or chromecast))

        if client:
            return client.playMedia(item)
        elif chromecast:
            return handler.play_media(item, self.plex)


    @action
    def pause(self, client):
        """
        Send pause event to a client
        """

        return self.client(client).pause()


    @action
    def stop(self, client):
        """
        Send stop event to a client
        """

        return self.client(client).stop()


    @action
    def seek(self, client, offset):
        """
        Send seek event to a client
        """

        return self.client(client).seekTo(offset)


    @action
    def forward(self, client):
        """
        Forward playback on a client
        """

        return self.client(client).stepForward()


    @action
    def back(self, client):
        """
        Backward playback on a client
        """

        return self.client(client).stepBack()


    @action
    def next(self, client):
        """
        Play next item on a client
        """

        return self.client(client).skipNext()


    @action
    def previous(self, client):
        """
        Play previous item on a client
        """

        return self.client(client).skipPrevious()


    @action
    def set_volume(self, client, volume):
        """
        Set the volume on a client between 0 and 100
        """

        return self.client(client).setVolume(volume/100)


    @action
    def repeat(self, client, repeat):
        """
        Set the repeat status on a client
        """

        return self.client(client).setRepeat(repeat)


    @action
    def random(self, client, random):
        """
        Set the random status on a client
        """

        return self.client(client).setShuffle(random)


    @action
    def up(self, client):
        """
        Send an up key event to a client
        """

        return self.client(client).moveUp()


    @action
    def down(self, client):
        """
        Send a down key event to a client
        """

        return self.client(client).moveDown()


    @action
    def left(self, client):
        """
        Send a left key event to a client
        """

        return self.client(client).moveLeft()


    @action
    def right(self, client):
        """
        Send a right key event to a client
        """

        return self.client(client).moveRight()


    @action
    def go_back(self, client):
        """
        Send a back key event to a client
        """

        return self.client(client).goBack()


    @action
    def go_home(self, client):
        """
        Send a home key event to a client
        """

        return self.client(client).goHome()


    @action
    def go_to_media(self, client):
        """
        Send a go to media event to a client
        """

        return self.client(client).goToMedia()


    @action
    def go_to_music(self, client):
        """
        Send a go to music event to a client
        """

        return self.client(client).goToMusic()


    @action
    def next_letter(self, client):
        """
        Send a next letter event to a client
        """

        return self.client(client).nextLetter()


    @action
    def page_down(self, client):
        """
        Send a page down event to a client
        """

        return self.client(client).pageDown()


    @action
    def page_up(self, client):
        """
        Send a page up event to a client
        """

        return self.client(client).pageUp()


    def _flatten_item(self, item):
        from plexapi.video import Movie, Show

        _item = {
            'summary': item.summary,
            'title': item.title,
            'type': item.type,
            'genres': [g.tag for g in getattr(item, 'genres', [])],
            'art': getattr(item, 'art', None),
            'art_url': getattr(item, 'artUrl', None),
            'rating': getattr(item, 'rating', None),
            'content_rating': getattr(item, 'content_rating', None),
        }

        if isinstance(item, Movie):
            _item['is_watched'] = item.isWatched
            _item['view_offset'] = item.viewOffset
            _item['view_count'] = item.viewCount
            _item['year'] = item.year
            _item['audience_rating'] = item.audienceRating
            _item['countries'] = [c.tag for c in item.countries]

            _item['media'] = [
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
            _item['media'] = [
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

        return _item


# vim:sw=4:ts=4:et:

