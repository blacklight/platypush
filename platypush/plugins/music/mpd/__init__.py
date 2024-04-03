import re
import threading
from typing import Collection, Optional, Union

from platypush.plugins import RunnablePlugin, action
from platypush.plugins.music import MusicPlugin

from ._conf import MpdConfig
from ._listener import MpdListener


class MusicMpdPlugin(MusicPlugin, RunnablePlugin):
    """
    This plugin allows you to interact with an MPD/Mopidy music server.

    `MPD <https://www.musicpd.org/>`_ is a flexible server-side
    protocol/application for handling music collections and playing music,
    mostly aimed to manage local libraries.

    `Mopidy <https://www.mopidy.com/>`_ is an evolution of MPD, compatible with
    the original protocol and with support for multiple music sources through
    plugins (e.g. Spotify, TuneIn, Soundcloud, local files etc.).

    .. note:: If you use Mopidy, and unless you have quite specific use-cases
        (like you don't want to expose the Mopidy HTTP interface, or you have
        some legacy automation that uses the MPD interface), you should use the
        :class:`platypush.plugins.music.mopidy.MusicMopidyPlugin` plugin instead
        of this. The Mopidy plugin provides a more complete and feature-rich
        experience, as not all the features of Mopidy are available through the
        MPD interface, and its API is 100% compatible with this plugin. Also,
        this plugin operates a synchronous/polling logic because of the
        limitations of the MPD protocol, while the Mopidy plugin, as it uses the
        Mopidy Websocket API, can operate in a more efficient way and provide
        real-time updates.

    .. note:: As of Mopidy 3.0 MPD is an optional interface provided by the
        ``mopidy-mpd`` extension. Make sure that you have the extension
        installed and enabled on your instance to use this plugin if you want to
        use it with Mopidy instead of MPD.

    """

    _client_lock = threading.RLock()

    def __init__(
        self,
        host: str,
        port: int = 6600,
        poll_interval: Optional[float] = 20.0,
        **kwargs,
    ):
        """
        :param host: MPD IP/hostname.
        :param port: MPD port (default: 6600).
        :param poll_interval: Polling interval in seconds. If set, the plugin
            will poll the MPD server for status updates and trigger change
            events when required. Default: 20 seconds.
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
        self.conf = MpdConfig(host=host, port=port)
        self.client = None

    def _connect(self, n_tries: int = 2):
        import mpd

        with self._client_lock:
            if self.client:
                return self.client

            error = None
            while n_tries > 0:
                try:
                    n_tries -= 1
                    self.client = mpd.MPDClient()
                    self.client.connect(self.conf.host, self.conf.port)
                    return self.client
                except Exception as e:
                    error = e
                    self.logger.warning(
                        'Connection exception: %s%s',
                        e,
                        (': Retrying' if n_tries > 0 else ''),
                    )
                    self.wait_stop(0.5)

        self.client = None
        if error:
            raise error

        return self.client

    def _exec(self, method: str, *args, **kwargs):
        error = None
        n_tries = int(kwargs.pop('n_tries')) if 'n_tries' in kwargs else 2
        return_status = (
            kwargs.pop('return_status') if 'return_status' in kwargs else True
        )

        while n_tries > 0:
            try:
                self._connect()
                n_tries -= 1
                with self._client_lock:
                    response = getattr(self.client, method)(*args, **kwargs)

                if return_status:
                    return self._status()

                return response
            except Exception as e:
                error = str(e)
                self.logger.warning(
                    'Exception while executing MPD method %s: %s', method, error
                )
                self.client = None

        return None, error

    @staticmethod
    def _dump_directory(item: dict):
        item['type'] = 'directory'
        item['uri'] = item['name'] = item['directory']
        return item

    @staticmethod
    def _dump_playlist(item: dict):
        item['type'] = 'playlist'
        item['uri'] = item['name'] = item['playlist']
        item['last_modified'] = item.pop('last-modified', None)
        return item

    @staticmethod
    def _dump_track(item: dict, pos: Optional[int] = None):
        item['type'] = 'track'
        item['uri'] = item['file']
        for attr in ('time', 'track', 'disc'):
            item[attr] = int(item[attr]) if item.get(attr) is not None else None

        if 'pos' in item:
            item['playlist_pos'] = int(item.pop('pos'))
        elif pos is not None:
            item['playlist_pos'] = pos

        return item

    @action
    def play(self, resource: Optional[str] = None, **__):
        """
        Play a resource by path/URI.

        :param resource: Resource path/URI
        :type resource: str
        """

        if resource:
            self.add(resource, position=0)
            return self.play_pos(0)

        return self._exec('play')

    @action
    def play_pos(self, pos: int):
        """
        Play a track in the current playlist by position number.

        :param pos: Position number.
        """

        return self._exec('play', pos)

    @action
    def pause(self, *_, **__):
        """Pause playback"""

        status = self._status()['state']
        return self._exec('pause') if status == 'play' else self._exec('play')

    @action
    def pause_if_playing(self):
        """Pause playback only if it's playing"""
        status = self._status()['state']
        return self._exec('pause') if status == 'play' else None

    @action
    def play_if_paused(self):
        """Play only if it's paused (resume)"""
        status = self._status()['state']
        return self._exec('play') if status == 'pause' else None

    @action
    def play_if_paused_or_stopped(self):
        """Play only if it's paused or stopped"""
        status = self._status()['state']
        return self._exec('play') if status in ('pause', 'stop') else None

    @action
    def stop(self, *_, **__):  # type: ignore
        """Stop playback"""
        # Note: stop could be interpreted both as "stop the playback" and "stop
        # the plugin". If the stop event is set, we assume that the user wants
        # to stop the plugin.
        if self.should_stop():
            if self.client:
                self.client.disconnect()

            return None

        return self._exec('stop')

    @action
    def play_or_stop(self):
        """Play or stop (play state toggle)"""
        status = self._status()['state']
        if status == 'play':
            return self._exec('stop')
        return self._exec('play')

    @action
    def next(self, *_, **__):
        """Play the next track"""
        return self._exec('next')

    @action
    def previous(self, **__):
        """Play the previous track"""
        return self._exec('previous')

    @action
    def set_volume(self, volume: int, **__):
        """
        Set the volume.

        :param volume: Volume value (range: 0-100).
        """
        return self._exec('setvol', str(volume))

    @action
    def volup(self, step: Optional[float] = None, **kwargs):
        """
        Turn up the volume.

        :param step: Volume up step (default: 5%).
        """
        step = step or kwargs.get('delta') or 5
        volume = int(self._status()['volume'])
        new_volume = min(volume + step, 100)
        return self.set_volume(new_volume)

    @action
    def voldown(self, step: Optional[float] = None, **kwargs):
        """
        Turn down the volume.

        :param step: Volume down step (default: 5%).
        """
        step = step or kwargs.get('delta') or 5
        volume = int(self._status()['volume'])
        new_volume = max(volume - step, 0)
        return self.set_volume(new_volume)

    def _toggle(self, key: str, value: Optional[bool] = None):
        if value is None:
            value = bool(self._status()[key])
        return self._exec(key, int(value))

    @action
    def random(self, value: Optional[bool] = None):
        """
        Set random mode.

        :param value: If set, set the random state this value (true/false).
            Default: None (toggle current state).
        """
        return self._toggle('random', value)

    @action
    def consume(self, value: Optional[bool] = None):
        """
        Set consume mode.

        :param value: If set, set the consume state this value (true/false).
            Default: None (toggle current state)
        """
        return self._toggle('consume', value)

    @action
    def single(self, value: Optional[bool] = None):
        """
        Set single mode.

        :param value: If set, set the consume state this value (true/false).
            Default: None (toggle current state)
        """
        return self._toggle('single', value)

    @action
    def repeat(self, value: Optional[bool] = None):
        """
        Set repeat mode.

        :param value: If set, set the repeat state this value (true/false).
            Default: None (toggle current state)
        """
        return self._toggle('repeat', value)

    @action
    def shuffle(self):
        """
        Shuffles the current playlist.
        """
        return self._exec('shuffle')

    @action
    def save(self, name: str):
        """
        Save the current tracklist to a new playlist with the specified name.

        :param name: Name of the playlist
        """
        return self._exec('save', name)

    @action
    def add(self, resource: str, *_, position: Optional[int] = None, **__):
        """
        Add a resource (track, album, artist, folder etc.) to the current
        playlist.

        :param resource: Resource path or URI.
        :param position: Position where the track(s) will be inserted (default:
            end of the playlist).
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
                    self.logger.warning('Could not add %s: %s', r, e)

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
        return self.get_tracks()

    @action
    def delete_playlist(self, playlist: Union[str, Collection[str]]):
        """
        Permanently remove playlist(s) by name

        :param playlist: Name or list of playlist names to remove
        :type playlist: str or list[str]
        """
        if isinstance(playlist, str):
            playlist = [playlist]
        elif not isinstance(playlist, list):
            raise RuntimeError(f'Invalid type for playlist: {type(playlist)}')

        for p in playlist:
            self._exec('rm', p)

    @action
    def move(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        position: Optional[int] = None,
        from_pos: Optional[int] = None,
        to_pos: Optional[int] = None,
    ):
        """
        Move the playlist items from the positions ``start`` to ``end`` to the
        new position ``position``.

        You can pass either:

            - ``start``, ``end`` and ``position`` to move a slice of tracks
              from ``start`` to ``end`` to the new position ``position``.
            - ``from_pos`` and ``to_pos`` to move a single track from
              ``from_pos`` to ``to_pos``.

        .. note: Positions are 0-based (i.e. the first track has position 0).

        :param start: Start position of the selection.
        :param end: End position of the selection.
        :param position: New position.
        :param from_pos: Alias for ``start`` - it only works with one track at
            the time.
        :param to_pos: Alias for ``position`` - it only works with one track at
            the time.
        """
        assert (start is not None and end is not None and position is not None) or (
            from_pos is not None and to_pos is not None
        ), 'Specify either (start, end, position) or (from_pos, to_pos)'

        if from_pos is not None and to_pos is not None:
            return self._exec('move', from_pos, to_pos)

        chunk = start if start == end else f'{start}:{end}'
        return self._exec('move', chunk, position)

    @classmethod
    def _parse_resource(cls, resource):
        if not resource:
            return None

        m = re.search(r'^https?://open\.spotify\.com/([^?]+)', resource)
        if m:
            resource = 'spotify:' + m.group(1).replace('/', ':')

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
    def clear(self, **__):
        """Clear the current playlist"""
        return self._exec('clear')

    @action
    def seek(self, position: float, **__):
        """
        Seek to the specified position

        :param position: Seek position in seconds, or delta string (e.g. '+15'
            or '-15') to indicate a seek relative to the current position
        """
        return self._exec('seekcur', position)

    @action
    def forward(self):
        """Go forward by 15 seconds"""
        return self._exec('seekcur', '+15')

    @action
    def back(self):
        """Go backward by 15 seconds"""
        return self._exec('seekcur', '-15')

    def _status(self) -> dict:
        n_tries = 2
        error = None

        while n_tries > 0:
            try:
                n_tries -= 1
                self._connect()
                if self.client:
                    return self.client.status()  # type: ignore
            except Exception as e:
                error = e
                self.logger.warning('Exception while getting MPD status: %s', e)
                self.client = None

        raise AssertionError(str(error))

    @action
    def status(self, *_, **__):
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
        return self._status()

    def _current_track(self):
        track = self._exec('currentsong', return_status=False)
        if not isinstance(track, dict):
            return None

        if 'title' in track and (
            'artist' not in track
            or not track['artist']
            or re.search('^https?://', track['file'])
            or re.search('^tunein:', track['file'])
        ):
            m = re.match(r'^\s*(.+?)\s+-\s+(.*)\s*$', track['title'])
            if m and m.group(1) and m.group(2):
                track['artist'] = m.group(1)
                track['title'] = m.group(2)

        return track

    @action
    def currentsong(self):
        """
        Legacy alias for :meth:`.current_track`.
        """
        return self.current_track()

    @action
    def current_track(self, *_, **__):
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
        return self._current_track()

    @action
    def get_tracks(self, *_, **__):
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
        return [
            self._dump_track(track, pos=i)  # type: ignore
            for i, track in enumerate(self._exec('playlistinfo', return_status=False))
        ]

    @action
    def get_playlists(self, *_, **__):
        """
        :returns: The playlists available on the server as a list of dicts.

        Example response::

            output = [
                {
                    "playlist": "Rock",
                    "last_modified": "2018-06-25T21:28:19Z"
                },
                {
                    "playlist": "Jazz",
                    "last_modified": "2018-06-24T22:28:29Z"
                },
                {
                    # ...
                }
            ]

        """
        playlists: list = self._exec(  # type: ignore
            'listplaylists', return_status=False
        )

        return sorted(
            [self._dump_playlist(pl) for pl in playlists], key=lambda p: p['playlist']
        )

    @action
    def get_playlist(self, playlist: str, *_, **__):
        """
        Get the tracks in a playlist.

        :param playlist: Name of the playlist
        """
        return [
            self._dump_track(track)  # type: ignore
            for track in self._exec(
                'listplaylistinfo',  # if with_tracks else 'listplaylist',
                playlist,
                return_status=False,
            )
            if track
        ]

    @action
    def add_to_playlist(
        self, playlist: str, resources: Union[str, Collection[str]], **_
    ):
        """
        Add one or multiple resources to a playlist.

        :param playlist: Playlist name
        :param resources: URI or path of the resource(s) to be added
        """

        if isinstance(resources, str):
            resources = [resources]

        for res in resources:
            self._exec('playlistadd', playlist, res)

    @action
    def remove_from_playlist(
        self, playlist: str, resources: Union[int, Collection[int]], *_, **__
    ):
        """
        Remove one or multiple tracks from a playlist.

        :param playlist: Playlist name
        :param resources: Position or list of positions to remove
        """

        if isinstance(resources, str):
            resources = int(resources)
        if isinstance(resources, int):
            resources = [resources]

        for p in sorted(resources, reverse=True):
            self._exec('playlistdelete', playlist, p)

    @action
    def playlist_move(self, playlist: str, from_pos: int, to_pos: int, *_, **__):
        """
        Change the position of a track in the specified playlist.

        :param playlist: Playlist name
        :param from_pos: Original track position
        :param to_pos: New track position
        """
        self._exec('playlistmove', playlist, from_pos, to_pos)

    @action
    def playlist_clear(self, name: str):
        """
        Clears all the elements from the specified playlist.

        :param name: Playlist name.
        """
        self._exec('playlistclear', name)

    @action
    def rename_playlist(self, playlist: str, new_name: str):
        """
        Rename a playlist.

        :param playlist: Original playlist name or URI
        :param new_name: New playlist name
        """
        self._exec('rename', playlist, new_name)

    @action
    def browse(self, uri: Optional[str] = None):
        """
        Browse the items under the specified URI.

        :param uri: URI to browse (default: root directory).
        """
        resp: dict = (  # type: ignore
            self._exec('lsinfo', uri, return_status=False)
            if uri
            else self._exec('lsinfo', return_status=False)
        )

        ret = []
        for item in resp:
            if item.get('directory'):
                item = self._dump_directory(item)
            elif item.get('playlist'):
                item = self._dump_playlist(item)
            elif item.get('file'):
                item = self._dump_track(item)
            else:
                continue

            ret.append(item)

        return ret

    @action
    def plchanges(self, version: int):
        """
        Show what has changed on the current playlist since a specified playlist
        version number.

        :param version: Version number
        :returns: A list of dicts representing the songs being added since the specified version
        """
        return self._exec('plchanges', version, return_status=False)

    @action
    def searchaddplaylist(self, name: str):
        """
        Search and add a playlist by (partial or full) name.

        :param name: Playlist name, can be partial.
        """

        resp: list = self._exec('listplaylists', return_status=False)  # type: ignore
        playlists = [
            pl['playlist'] for pl in resp if name.lower() in pl['playlist'].lower()
        ]

        if not playlists:
            return None

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

    @action
    def find(self, filter: dict, *args, **kwargs):  # pylint: disable=redefined-builtin
        """
        Find in the database/library by filter.

        :param filter: Search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``)
        :returns: list[dict]
        """
        filter_list = self._make_filter(filter)
        return self._exec('find', *filter_list, *args, return_status=False, **kwargs)

    @action
    def findadd(
        self, filter: dict, *args, **kwargs  # pylint: disable=redefined-builtin
    ):
        """
        Find in the database/library by filter and add to the current playlist.

        :param filter: Search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``)
        :returns: list[dict]
        """
        filter_list = self._make_filter(filter)
        return self._exec('findadd', *filter_list, *args, return_status=False, **kwargs)

    @action
    def search(
        self,
        *args,
        query: Optional[Union[str, dict]] = None,
        filter: Optional[dict] = None,  # pylint: disable=redefined-builtin
        **kwargs,
    ):
        """
        Free search by filter.

        :param query: Free-text query or search structured filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``).
        :param filter: Structured search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``) - same as
            ``query``, it's still here for back-compatibility reasons.
        :returns: list[dict]
        """
        assert query or filter, 'Specify either `query` or `filter`'

        filt = filter
        if isinstance(query, str):
            filt = query
        elif isinstance(query, dict):
            filt = {**(filter or {}), **query}

        filter_list = self._make_filter(filt) if isinstance(filt, dict) else [query]

        items: list = self._exec(  # type: ignore
            'search', *filter_list, *args, return_status=False, **kwargs
        )

        # Spotify results first
        return sorted(
            items, key=lambda item: 0 if item['file'].startswith('spotify:') else 1
        )

    @action
    def searchadd(
        self, filter: dict, *args, **kwargs  # pylint: disable=redefined-builtin
    ):
        """
        Free search by filter and add the results to the current playlist.

        :param filter: Search filter (e.g. ``{"artist": "Led Zeppelin", "album": "IV"}``)
        :returns: list[dict]
        """
        filter_list = self._make_filter(filter)
        return self._exec(
            'searchadd', *filter_list, *args, return_status=False, **kwargs
        )

    def main(self):
        listener = None
        if self.poll_interval is not None:
            listener = MpdListener(self)
            listener.start()

        self.wait_stop()

        if listener:
            listener.join()


# vim:sw=4:ts=4:et:
