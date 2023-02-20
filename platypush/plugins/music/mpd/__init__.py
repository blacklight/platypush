import re
import threading
import time
from typing import Optional, Union

from platypush.plugins import action
from platypush.plugins.music import MusicPlugin


class MusicMpdPlugin(MusicPlugin):
    """
    This plugin allows you to interact with an MPD/Mopidy music server.  MPD
    (https://www.musicpd.org/) is a flexible server-side protocol/application
    for handling music collections and playing music, mostly aimed to manage
    local libraries. Mopidy (https://www.mopidy.com/) is an evolution of MPD,
    compatible with the original protocol and with support for multiple music
    sources through plugins (e.g. Spotify, TuneIn, Soundcloud, local files
    etc.).

    **NOTE**: As of Mopidy 3.0 MPD is an optional interface provided by the ``mopidy-mpd`` extension. Make sure that you
    have the extension installed and enabled on your instance to use this plugin with your server.

    Requires:

        * **python-mpd2** (``pip install python-mpd2``)

    """

    _client_lock = threading.RLock()

    def __init__(self, host, port=6600):
        """
        :param host: MPD IP/hostname
        :type host: str

        :param port: MPD port (default: 6600)
        :type port: int
        """

        super().__init__()
        self.host = host
        self.port = port
        self.client = None

    def _connect(self, n_tries=2):
        import mpd

        with self._client_lock:
            if self.client:
                return

            error = None
            while n_tries > 0:
                try:
                    n_tries -= 1
                    self.client = mpd.MPDClient()
                    self.client.connect(self.host, self.port)
                    return self.client
                except Exception as e:
                    error = e
                    self.logger.warning('Connection exception: {}{}'.
                                        format(str(e), (': Retrying' if n_tries > 0 else '')))
                    time.sleep(0.5)

        self.client = None
        if error:
            raise error

    def _exec(self, method, *args, **kwargs):
        error = None
        n_tries = int(kwargs.pop('n_tries')) if 'n_tries' in kwargs else 2
        return_status = kwargs.pop('return_status') \
            if 'return_status' in kwargs else True

        while n_tries > 0:
            try:
                self._connect()
                n_tries -= 1
                with self._client_lock:
                    response = getattr(self.client, method)(*args, **kwargs)

                if return_status:
                    return self.status().output
                return response
            except Exception as e:
                error = str(e)
                self.logger.warning('Exception while executing MPD method {}: {}'.
                                    format(method, error))
                self.client = None

        return None, error

    @action
    def play(self, resource=None):
        """
        Play a resource by path/URI

        :param resource: Resource path/URI
        :type resource: str
        """

        if resource:
            self.add(resource, position=0)
            return self.play_pos(0)

        return self._exec('play')

    @action
    def play_pos(self, pos):
        """
        Play a track in the current playlist by position number

        :param pos: Position number
        """

        return self._exec('play', pos)

    @action
    def pause(self):
        """ Pause playback """

        status = self.status().output['state']
        if status == 'play':
            return self._exec('pause')
        else:
            return self._exec('play')

    @action
    def pause_if_playing(self):
        """ Pause playback only if it's playing """

        status = self.status().output['state']
        if status == 'play':
            return self._exec('pause')

    @action
    def play_if_paused(self):
        """ Play only if it's paused (resume) """

        status = self.status().output['state']
        if status == 'pause':
            return self._exec('play')

    @action
    def play_if_paused_or_stopped(self):
        """ Play only if it's paused or stopped """

        status = self.status().output['state']
        if status == 'pause' or status == 'stop':
            return self._exec('play')

    @action
    def stop(self):
        """ Stop playback """
        return self._exec('stop')

    @action
    def play_or_stop(self):
        """ Play or stop (play state toggle) """
        status = self.status().output['state']
        if status == 'play':
            return self._exec('stop')
        else:
            return self._exec('play')

    @action
    def playid(self, track_id):
        """
        Play a track by ID

        :param track_id: Track ID
        :type track_id: str
        """

        return self._exec('playid', track_id)

    @action
    def next(self):
        """ Play the next track """
        return self._exec('next')

    @action
    def previous(self):
        """ Play the previous track """
        return self._exec('previous')

    @action
    def setvol(self, vol):
        """
        Set the volume (DEPRECATED, use :meth:`.set_volume` instead).

        :param vol: Volume value (range: 0-100)
        :type vol: int
        """
        return self.set_volume(vol)

    @action
    def set_volume(self, volume):
        """
        Set the volume.

        :param volume: Volume value (range: 0-100)
        :type volume: int
        """
        return self._exec('setvol', str(volume))

    @action
    def volup(self, delta=10):
        """
        Turn up the volume

        :param delta: Volume up delta (default: +10%)
        :type delta: int
        """

        volume = int(self.status().output['volume'])
        new_volume = min(volume + delta, 100)
        return self.setvol(new_volume)

    @action
    def voldown(self, delta=10):
        """
        Turn down the volume

        :param delta: Volume down delta (default: -10%)
        :type delta: int
        """

        volume = int(self.status().output['volume'])
        new_volume = max(volume - delta, 0)
        return self.setvol(new_volume)

    @action
    def random(self, value=None):
        """
        Set random mode

        :param value: If set, set the random state this value (true/false). Default: None (toggle current state)
        :type value: bool
        """

        if value is None:
            value = int(self.status().output['random'])
            value = 1 if value == 0 else 0
        return self._exec('random', value)

    @action
    def consume(self, value=None):
        """
        Set consume mode

        :param value: If set, set the consume state this value (true/false). Default: None (toggle current state)
        :type value: bool
        """

        if value is None:
            value = int(self.status().output['consume'])
            value = 1 if value == 0 else 0
        return self._exec('consume', value)

    @action
    def single(self, value=None):
        """
        Set single mode

        :param value: If set, set the consume state this value (true/false). Default: None (toggle current state)
        :type value: bool
        """

        if value is None:
            value = int(self.status().output['single'])
            value = 1 if value == 0 else 0
        return self._exec('single', value)

    @action
    def repeat(self, value=None):
        """
        Set repeat mode

        :param value: If set, set the repeat state this value (true/false). Default: None (toggle current state)
        :type value: bool
        """

        if value is None:
            value = int(self.status().output['repeat'])
            value = 1 if value == 0 else 0
        return self._exec('repeat', value)

    @action
    def shuffle(self):
        """
        Shuffles the current playlist
        """
        return self._exec('shuffle')

    @action
    def save(self, name):
        """
        Save the current tracklist to a new playlist with the specified name

        :param name: Name of the playlist
        :type name: str
        """
        return self._exec('save', name)

    @action
    def add(self, resource, position=None):
        """
        Add a resource (track, album, artist, folder etc.) to the current playlist

        :param resource: Resource path or URI
        :type resource: str

        :param position: Position where the track(s) will be inserted (default: end of the playlist)
        :type position: int
        """

        if isinstance(resource, list):
            for r in resource:
                r = self._parse_resource(r)
                try:
                    if position is None:
                        self._exec('add', r)
                    else:
                        self._exec('addid', r, position)
                except Exception as e:
                    self.logger.warning('Could not add {}: {}'.format(r, e))

            return self.status().output

        r = self._parse_resource(resource)

        if position is None:
            return self._exec('add', r)
        return self._exec('addid', r, position)

    @action
    def delete(self, positions):
        """
        Delete the playlist item(s) in the specified position(s).

        :param positions: Positions of the tracks to be removed
        :type positions: list[int]

        :return: The modified playlist
        """

        for pos in sorted(positions, key=int, reverse=True):
            self._exec('delete', pos)
        return self.playlistinfo()

    @action
    def rm(self, playlist):
        """
        Permanently remove playlist(s) by name

        :param playlist: Name or list of playlist names to remove
        :type playlist: str or list[str]
        """

        if isinstance(playlist, str):
            playlist = [playlist]
        elif not isinstance(playlist, list):
            raise RuntimeError('Invalid type for playlist: {}'.format(type(playlist)))

        for p in playlist:
            self._exec('rm', p)

    @action
    def move(self, from_pos, to_pos):
        """
        Move the playlist item in position <from_pos> to position <to_pos>

        :param from_pos: Track current position
        :type from_pos: int

        :param to_pos: Track new position
        :type to_pos: int
        """
        return self._exec('move', from_pos, to_pos)

    @classmethod
    def _parse_resource(cls, resource):
        if not resource:
            return

        m = re.search(r'^https?://open\.spotify\.com/([^?]+)', resource)
        if m:
            resource = 'spotify:{}'.format(m.group(1).replace('/', ':'))

        if resource.startswith('spotify:'):
            resource = resource.split('?')[0]

        m = re.match(r'spotify:playlist:(.*)', resource)
        if m:
            # Old Spotify URI format, convert it to new
            resource = 'spotify:user:spotify:playlist:' + m.group(1)
        return resource

    @action
    def load(self, playlist, play=True):
        """
        Load and play a playlist by name

        :param playlist: Playlist name
        :type playlist: str

        :param play: Start playback after loading the playlist (default: True)
        :type play: bool
        """

        ret = self._exec('load', playlist)
        if play:
            self.play()
        return ret

    @action
    def clear(self):
        """ Clear the current playlist """
        return self._exec('clear')

    @action
    def seekcur(self, value):
        """
        Seek to the specified position (DEPRECATED, use :meth:`.seek` instead).

        :param value: Seek position in seconds, or delta string (e.g. '+15' or '-15') to indicate a seek relative to
            the current position :type value: int
        """

        return self.seek(value)

    @action
    def seek(self, position):
        """
        Seek to the specified position

        :param position: Seek position in seconds, or delta string (e.g. '+15' or '-15') to indicate a seek relative
            to the current position :type position: int
        """

        return self._exec('seekcur', position)

    @action
    def forward(self):
        """ Go forward by 15 seconds """

        return self._exec('seekcur', '+15')

    @action
    def back(self):
        """ Go backward by 15 seconds """

        return self._exec('seekcur', '-15')

    @action
    def status(self):
        """
        :returns: The current state.

        Example response::

            output = {
                "volume": "9",
                "repeat": "0",
                "random": "0",
                "single": "0",
                "consume": "0",
                "playlist": "52",
                "playlistlength": "14",
                "xfade": "0",
                "state": "play",
                "song": "9",
                "songid": "3061",
                "nextsong": "10",
                "nextsongid": "3062",
                "time": "161:255",
                "elapsed": "161.967",
                "bitrate": "320"
            }

        """

        n_tries = 2
        error = None

        while n_tries > 0:
            try:
                n_tries -= 1
                self._connect()
                if self.client:
                    return self.client.status()
            except Exception as e:
                error = e
                self.logger.warning('Exception while getting MPD status: {}'.
                                    format(str(e)))
                self.client = None

        return None, error

    @action
    def currentsong(self):
        """
        Legacy alias for :meth:`.current_track`.
        """
        return self.current_track()

    # noinspection PyTypeChecker
    @action
    def current_track(self):
        """
        :returns: The currently played track.

        Example response::

            output = {
                "file": "spotify:track:7CO5ADlDN3DcR2pwlnB14P",
                "time": "255",
                "artist": "Elbow",
                "album": "Little Fictions",
                "title": "Kindling",
                "date": "2017",
                "track": "10",
                "pos": "9",
                "id": "3061",
                "albumartist": "Elbow",
                "x-albumuri": "spotify:album:6q5KhDhf9BZkoob7uAnq19"
            }
        """

        track = self._exec('currentsong', return_status=False)
        if 'title' in track and ('artist' not in track
                                 or not track['artist']
                                 or re.search('^https?://', track['file'])
                                 or re.search('^tunein:', track['file'])):
            m = re.match(r'^\s*(.+?)\s+-\s+(.*)\s*$', track['title'])
            if m and m.group(1) and m.group(2):
                track['artist'] = m.group(1)
                track['title'] = m.group(2)

        return track

    @action
    def playlistinfo(self):
        """
        :returns: The tracks in the current playlist as a list of dicts.

        Example output::

            output = [
                {
                    "file": "spotify:track:79VtgIoznishPUDWO7Kafu",
                    "time": "355",
                    "artist": "Elbow",
                    "album": "Little Fictions",
                    "title": "Trust the Sun",
                    "date": "2017",
                    "track": "3",
                    "pos": "10",
                    "id": "3062",
                    "albumartist": "Elbow",
                    "x-albumuri": "spotify:album:6q5KhDhf9BZkoob7uAnq19"
                },
                {
                    "file": "spotify:track:3EzTre0pxmoMYRuhJKMHj6",
                    "time": "219",
                    "artist": "Elbow",
                    "album": "Little Fictions",
                    "title": "Gentle Storm",
                    "date": "2017",
                    "track": "2",
                    "pos": "11",
                    "id": "3063",
                    "albumartist": "Elbow",
                    "x-albumuri": "spotify:album:6q5KhDhf9BZkoob7uAnq19"
                },
            ]
        """

        return self._exec('playlistinfo', return_status=False)

    @action
    def get_playlists(self):
        """
        :returns: The playlists available on the server as a list of dicts.

        Example response::

            output = [
                {
                    "playlist": "Rock",
                    "last-modified": "2018-06-25T21:28:19Z"
                },
                {
                    "playlist": "Jazz",
                    "last-modified": "2018-06-24T22:28:29Z"
                },
                {
                    # ...
                }
            ]
        """
        return sorted(self._exec('listplaylists', return_status=False),
                      key=lambda p: p['playlist'])

    @action
    def listplaylists(self):
        """
        Deprecated alias for :meth:`.playlists`.
        """
        return self.get_playlists()

    @action
    def get_playlist(self, playlist, with_tracks=False):
        """
        List the items in the specified playlist.

        :param playlist: Name of the playlist
        :type playlist: str
        :param with_tracks: If True then the list of tracks in the playlist will be returned as well (default: False).
        :type with_tracks: bool
        """
        return self._exec(
            'listplaylistinfo' if with_tracks else 'listplaylist',
            playlist, return_status=False)

    @action
    def listplaylist(self, name):
        """
        Deprecated alias for :meth:`.playlist`.
        """
        return self._exec('listplaylist', name, return_status=False)

    @action
    def listplaylistinfo(self, name):
        """
        Deprecated alias for :meth:`.playlist` with `with_tracks=True`.
        """
        return self.get_playlist(name, with_tracks=True)

    @action
    def add_to_playlist(self, playlist, resources):
        """
        Add one or multiple resources to a playlist.

        :param playlist: Playlist name
        :type playlist: str

        :param resources: URI or path of the resource(s) to be added
        :type resources: str or list[str]
        """

        if isinstance(resources, str):
            resources = [resources]

        for res in resources:
            self._exec('playlistadd', playlist, res)

    @action
    def playlistadd(self, name, uri):
        """
        Deprecated alias for :meth:`.add_to_playlist`.
        """
        return self.add_to_playlist(name, uri)

    @action
    def remove_from_playlist(self, playlist, resources):
        """
        Remove one or multiple tracks from a playlist.

        :param playlist: Playlist name
        :type playlist: str

        :param resources: Position or list of positions to remove
        :type resources: int or list[int]
        """

        if isinstance(resources, str):
            resources = int(resources)
        if isinstance(resources, int):
            resources = [resources]

        for p in sorted(resources, reverse=True):
            self._exec('playlistdelete', playlist, p)

    @action
    def playlist_move(self, playlist, from_pos, to_pos):
        """
        Change the position of a track in the specified playlist.

        :param playlist: Playlist name
        :type playlist: str

        :param from_pos: Original track position
        :type from_pos: int

        :param to_pos: New track position
        :type to_pos: int
        """
        self._exec('playlistmove', playlist, from_pos, to_pos)

    @action
    def playlistdelete(self, name, pos):
        """
        Deprecated alias for :meth:`.remove_from_playlist`.
        """
        return self.remove_from_playlist(name, pos)

    @action
    def playlistmove(self, name, from_pos, to_pos):
        """
        Deprecated alias for :meth:`.playlist_move`.
        """
        return self.playlist_move(name, from_pos=from_pos, to_pos=to_pos)

    @action
    def playlistclear(self, name):
        """
        Clears all the elements from the specified playlist

        :param name: Playlist name
        :type name: str
        """
        self._exec('playlistclear', name)

    @action
    def rename(self, name, new_name):
        """
        Rename a playlist

        :param name: Original playlist name
        :type name: str

        :param new_name: New playlist name
        :type name: str
        """
        self._exec('rename', name, new_name)

    @action
    def lsinfo(self, uri=None):
        """
        Returns the list of playlists and directories on the server
        """

        return self._exec('lsinfo', uri, return_status=False) \
            if uri else self._exec('lsinfo', return_status=False)

    @action
    def plchanges(self, version):
        """
        Show what has changed on the current playlist since a specified playlist
        version number.

        :param version: Version number
        :type version: int

        :returns: A list of dicts representing the songs being added since the specified version
        """

        return self._exec('plchanges', version, return_status=False)

    @action
    def searchaddplaylist(self, name):
        """
        Search and add a playlist by (partial or full) name

        :param name: Playlist name, can be partial
        :type name: str
        """

        playlists = list(map(lambda _: _['playlist'],
                             filter(lambda playlist:
                                    name.lower() in playlist['playlist'].lower(),
                                    self._exec('listplaylists', return_status=False))))

        if len(playlists):
            self._exec('clear')
            self._exec('load', playlists[0])
            self._exec('play')
            return {'playlist': playlists[0]}

    @staticmethod
    def _make_filter(f: dict) -> list:
        ll = []
        for k, v in f.items():
            ll.extend([k, v])
        return ll

    # noinspection PyShadowingBuiltins
    @action
    def find(self, filter: dict, *args, **kwargs):
        """
        Find in the database/library by filter.

        :param filter: Search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``)
        :returns: list[dict]
        """

        filter = self._make_filter(filter)
        return self._exec('find', *filter, *args, return_status=False, **kwargs)

    # noinspection PyShadowingBuiltins
    @action
    def findadd(self, filter: dict, *args, **kwargs):
        """
        Find in the database/library by filter and add to the current playlist.

        :param filter: Search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``)
        :returns: list[dict]
        """

        filter = self._make_filter(filter)
        return self._exec('findadd', *filter, *args, return_status=False, **kwargs)

    # noinspection PyShadowingBuiltins
    @action
    def search(self, query: Optional[Union[str, dict]] = None, filter: Optional[dict] = None, *args, **kwargs):
        """
        Free search by filter.

        :param query: Free-text query or search structured filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``).
        :param filter: Structured search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``) - same as
            ``query``, it's still here for back-compatibility reasons.
        :returns: list[dict]
        """
        filter = self._make_filter(query or filter)
        items = self._exec('search', *filter, *args, return_status=False, **kwargs)

        # Spotify results first
        return sorted(items, key=lambda item: 0 if item['file'].startswith('spotify:') else 1)

    # noinspection PyShadowingBuiltins
    @action
    def searchadd(self, filter, *args, **kwargs):
        """
        Free search by filter and add the results to the current playlist.

        :param filter: Search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``)
        :returns: list[dict]
        """

        filter = self._make_filter(filter)
        return self._exec('searchadd', *filter, *args, return_status=False, **kwargs)


# vim:sw=4:ts=4:et:
