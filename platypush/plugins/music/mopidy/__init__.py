from typing import Dict, Iterable, List, Optional, Union

from platypush.plugins import RunnablePlugin, action
from platypush.plugins.media import PlayerState
from platypush.schemas.mopidy import (
    MopidyAlbumSchema,
    MopidyArtistSchema,
    MopidyDirectorySchema,
    MopidyFilterSchema,
    MopidyPlaylistSchema,
    MopidyStatusSchema,
    MopidyTrackSchema,
)
from platypush.utils import wait_for_either

from ._client import MopidyClient
from ._common import DEFAULT_TIMEOUT
from ._conf import MopidyConfig
from ._exc import EmptyTrackException
from ._playlist import MopidyPlaylist
from ._status import MopidyStatus
from ._sync import PlaylistSync
from ._task import MopidyTask
from ._track import MopidyTrack


class MusicMopidyPlugin(RunnablePlugin):
    """
    This plugin allows you to track the events from a Mopidy instance
    and control it through the Mopidy HTTP API.

    Requires:

        * A Mopidy instance running with the HTTP service enabled.

    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6680,
        ssl: bool = False,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
        **kwargs,
    ):
        """
        :param host: Mopidy host (default: localhost).
        :param port: Mopidy HTTP port (default: 6680).
        :param ssl: Set to True if the Mopidy server is running on HTTPS.
        :param timeout: Default timeout for the Mopidy requests (default: 20s).
        """
        super().__init__(**kwargs)

        self.config = MopidyConfig(host=host, port=port, ssl=ssl, timeout=timeout)
        self._status = MopidyStatus()
        self._tasks: Dict[int, MopidyTask] = {}
        self._client: Optional[MopidyClient] = None
        self._playlist_sync = PlaylistSync()

    def _exec(self, *msgs: dict, **kwargs):
        assert self._client, "Mopidy client not running"
        return self._client.exec(
            *msgs, timeout=kwargs.pop('timeout', self.config.timeout)
        )

    def _exec_with_status(self, *msgs: dict, **kwargs):
        self._exec(*msgs, **kwargs)
        return self._dump_status()

    def _dump_status(self):
        assert self._client, "Mopidy client not running"
        return MopidyStatusSchema().dump(self._client.status)

    def _dump_results(self, results: List[dict]) -> List[dict]:
        schema_by_type = {
            'artist': MopidyArtistSchema(),
            'album': MopidyAlbumSchema(),
            'directory': MopidyDirectorySchema(),
            'playlist': MopidyPlaylistSchema(),
            'track': MopidyTrackSchema(),
        }

        return [
            {
                **(
                    MopidyTrack.parse(item).to_dict()  # type: ignore
                    if item['type'] == 'track'
                    else schema_by_type[item['type']].dump(item)
                ),
                'type': item['type'],
            }
            for item in results
        ]

    def _dump_search_results(self, results: List[dict]) -> List[dict]:
        return self._dump_results(
            [
                {
                    **item,
                    'type': res_type,
                }
                for search_provider in results
                for res_type in ['artist', 'album', 'track']
                for item in search_provider.get(res_type + 's', [])
            ]
        )

    def _lookup(self, *uris: str) -> Dict[str, List[MopidyTrack]]:
        if not uris:
            return {}

        if len(uris) > 1:
            # If more than one URI is specified, we need to call only
            # library.lookup, as playlist.lookup does not support multiple
            # URIs.
            result = self._exec(
                {'method': 'core.library.lookup', 'uris': uris},
            )[0]
        else:
            # Otherwise, search both in the library and in the playlist
            # controllers.
            uri = uris[0]
            result = self._exec(
                {'method': 'core.playlists.lookup', 'uri': uri},
                {'method': 'core.library.lookup', 'uris': [uri]},
            )
            result = {
                uri: (
                    result[0].get('tracks', [])
                    if result[0]
                    else list(result[1].values())[0]
                )
            }

        ret = {}
        for uri, tracks in result.items():
            ret[uri] = []
            for track in tracks:
                parsed_track = MopidyTrack.parse(track)
                if parsed_track:
                    ret[uri].append(parsed_track)

        return ret

    def _add(
        self,
        *resources: str,
        position: Optional[int] = None,
        clear: bool = False,
        lookup: bool = True,
    ):
        batch_size = 50
        results = self._lookup(*resources).values()
        ret = []
        uris = (
            [track.uri for tracks in results for track in tracks if track and track.uri]
            if lookup
            else list(resources)
        )

        with self._playlist_sync:
            if clear:
                self.clear()

            for i in range(0, len(uris), batch_size):
                ret += self._exec(
                    {
                        'method': 'core.tracklist.add',
                        'uris': uris[i : i + batch_size],
                        'at_position': position,
                    }
                )[0]

                self.logger.info('Loaded %d/%d tracks', len(ret), len(uris))

        return ret

    def _get_playlist(self, playlist: str, with_tracks: bool = False) -> MopidyPlaylist:
        playlists = self._get_playlists()
        pl_by_name = {p.name: p for p in playlists}
        pl_by_uri = {p.uri: p for p in playlists}
        pl = pl_by_uri.get(playlist, pl_by_name.get(playlist))
        assert pl, f"Playlist {playlist} not found"

        if with_tracks:
            pl.tracks = self._get_playlist_tracks(playlist)

        return pl

    def _get_playlist_tracks(self, playlist: str) -> List[MopidyTrack]:
        playlists = self._get_playlists()
        pl_by_name = {p.name: p for p in playlists}
        pl_by_uri = {p.uri: p for p in playlists}
        pl = pl_by_uri.get(playlist, pl_by_name.get(playlist))
        assert pl, f"Playlist {playlist} not found"

        tracks = self._exec({'method': 'core.playlists.get_items', 'uri': pl.uri})[0]
        assert tracks is not None, f"Playlist {playlist} not found"

        ret = []
        for track in tracks:
            parsed_track = MopidyTrack.parse(track)
            if parsed_track:
                ret.append(parsed_track)

        return ret

    def _get_playlists(self, **__) -> List[MopidyPlaylist]:
        return [
            MopidyPlaylist.parse(pl)
            for pl in self._exec({'method': 'core.playlists.as_list'})[0]
        ]

    def _save_playlist(self, playlist: MopidyPlaylist):
        return self._exec(
            {
                'method': 'core.playlists.save',
                'playlist': {
                    '__model__': 'Playlist',
                    'uri': playlist.uri,
                    'name': playlist.name,
                    'tracks': [
                        {
                            '__model__': 'Track',
                            'uri': track.uri,
                        }
                        for track in playlist.tracks
                    ],
                },
            }
        )[0]

    @action
    def play(
        self,
        resource: Optional[str] = None,
        position: Optional[int] = None,
        track_id: Optional[int] = None,
        **__,
    ):
        """
        Start playback, or play a resource by URI.

        :param resource: Resource path/URI. If not specified, it will resume the
            playback if paused/stopped, otherwise it will start playing the
            selected track.
        :param track_id: The ID of track (or ``tlid``) in the current playlist
            that should be played, if you want to play a specific track already
            loaded in the current playlist.
        :param position: Position number (0-based) of the track in the current
            playlist that should be played.
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if resource:
            ret = self._add(resource, position=0)
            if not ret:
                self.logger.warning('Failed to add %s to the tracklist', resource)
            elif isinstance(ret, list):
                track_id = ret[0].get('tlid')
            elif isinstance(ret, dict):
                track_id = ret.get('tlid')
        elif position is not None:
            tracklist = self._exec({'method': 'core.tracklist.get_tl_tracks'})[0]
            if position < 0 or position >= len(tracklist):
                self.logger.warning(
                    'Position %d is out of bounds for the current tracklist', position
                )
                return None

            track_id = tracklist[position]['tlid']

        return self._exec_with_status(
            {'method': 'core.playback.play', 'tlid': track_id}
        )

    @action
    def play_pos(self, pos: int):
        """
        Play a track in the current playlist by position number.

        Legacy alias for :meth:`.play` with a ``position`` parameter.

        :param pos: Position number (0-based).
        """
        return self.play(position=pos)

    @action
    def load(self, playlist: str, play: bool = True):
        """
        Load/play a playlist.

        This method will clear the current playlist and load the tracks from the
        given playlist.

        You should usually prefer :meth:`.add` to this method, as it is more
        general-purpose (``load`` only works with playlists). This method exists
        mainly for compatibility with the MPD plugin.

        :param playlist: Playlist URI.
        :param play: Start playback after loading the playlist (default: True).
        """
        self._add(playlist, clear=True)
        if play:
            self.play()

    @action
    def lookup(self, resources: Iterable[str], **__):
        """
        Lookup (one or) resources by URI.

        Given a list of URIs, this method will return a dictionary in the form
        ``{uri: [track1, track2, ...]}``.

        :param resource: Resource URI(s).
        :return: .. schema:: mopidy.MopidyTrackSchema(many=True)
        """
        return {
            uri: [track.to_dict() for track in tracks]
            for uri, tracks in self._lookup(*resources).items()
        }

    @action
    def pause(self, **__):
        """
        Pause the playback.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self._exec_with_status({'method': 'core.playback.pause'})

    @action
    def stop(self, **__):  # type: ignore
        """
        Stop the playback.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        # Note: stop could be interpreted both as "stop the playback" and "stop
        # the plugin". If the stop event is set, we assume that the user wants
        # to stop the plugin.
        if self.should_stop():
            if self._client:
                self._client.stop()

            return None

        return self._exec_with_status({'method': 'core.playback.stop'})

    @action
    def prev(self, **__):
        """
        Play the previous track.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self._exec_with_status({'method': 'core.playback.previous'})

    @action
    def next(self, **__):
        """
        Play the next track.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self._exec_with_status({'method': 'core.playback.next'})

    @action
    def add(
        self,
        resource: Union[str, Iterable[str]],
        *_,
        position: Optional[int] = None,
        **__,
    ):
        """
        Add a resource (track, album, artist, folder etc.) to the current
        playlist.

        :param resource: Resource URI(s).
        :param position: Position (0-based) where the track(s) will be inserted
            (default: end of the playlist).
        :return: The list of tracks added to the queue.
            .. schema:: mopidy.MopidyTrackSchema(many=True)
        """
        resources = [resource] if isinstance(resource, str) else resource
        tracks = [
            MopidyTrack.parse(track)
            for track in self._add(*resources, position=position)
        ]
        return [track.to_dict() for track in tracks if track]

    @action
    def pause_if_playing(self, **__):
        """
        Pause the playback if it's currently playing.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if self._status.state == PlayerState.PLAY:
            return self.pause()

        return self._dump_status()

    @action
    def play_if_paused(self, **__):
        """
        Resume the playback if it's currently paused.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if self._status.state == PlayerState.PAUSE:
            return self.play()

        return self._dump_status()

    @action
    def play_if_paused_or_stopped(self):
        """
        Resume the playback if it's currently paused or stopped.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if self._status.state in {PlayerState.PAUSE, PlayerState.STOP}:
            return self.play()

        return self._dump_status()

    @action
    def play_or_stop(self):
        """
        Play if the playback is stopped, stop if it's playing, otherwise resume
        playback.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if self._status.state == PlayerState.PLAY:
            return self.stop()

        return self.play()

    @action
    def set_volume(self, volume: int, **__):
        """
        Set the volume.

        :param volume: Volume level (0-100).
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self._exec_with_status(
            {'method': 'core.mixer.set_volume', 'volume': volume}
        )

    @action
    def volup(self, step: int = 5, **__):
        """
        Increase the volume by a given step.

        :param step: Volume step (default: 5%).
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self.set_volume(volume=min(100, self._status.volume + step))

    @action
    def voldown(self, step: int = 5, **__):
        """
        Decrease the volume by a given step.

        :param step: Volume step (default: 5%).
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self.set_volume(volume=max(0, self._status.volume - step))

    @action
    def random(self, value: Optional[bool] = None, **__):
        """
        Set the random mode.

        :param value: Random mode. If not specified, it will toggle the current
            random mode.
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if value is None:
            value = not self._status.random

        return self._exec_with_status(
            {'method': 'core.tracklist.set_random', 'value': bool(value)}
        )

    @action
    def repeat(self, value: Optional[bool] = None, **__):
        """
        Set the repeat mode.

        :param value: Repeat mode. If not specified, it will toggle the current
            repeat mode.
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if value is None:
            value = not self._status.repeat

        return self._exec_with_status(
            {'method': 'core.tracklist.set_repeat', 'value': bool(value)}
        )

    @action
    def consume(self, value: Optional[bool] = None, **__):
        """
        Set the consume mode.

        :param value: Consume mode. If not specified, it will toggle the current
            consume mode.
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if value is None:
            value = not self._status.consume

        return self._exec_with_status(
            {'method': 'core.tracklist.set_consume', 'value': bool(value)}
        )

    @action
    def single(self, value: Optional[bool] = None, **__):
        """
        Set the single mode.

        :param value: Single mode. If not specified, it will toggle the current
            single mode.
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if value is None:
            value = not self._status.single

        return self._exec_with_status(
            {'method': 'core.tracklist.set_single', 'value': bool(value)}
        )

    @action
    def shuffle(self, **__):
        """
        Shuffle the current playlist.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self._exec_with_status({'method': 'core.tracklist.shuffle'})

    @action
    def save(self, name: str, **__):
        """
        Save the current tracklist to a new playlist with the given name.

        :param name: New playlist name.
        """
        return self._exec({'method': 'core.playlists.save', 'name': name})[0]

    @action
    def delete(
        self,
        positions: Optional[Iterable[int]] = None,
        uris: Optional[Iterable[str]] = None,
    ):
        """
        Delete tracks from the current tracklist.

        .. note:: At least one of the ``positions`` or ``uris`` parameters must
                  be specified.

        :param positions: (0-based) positions of the tracks to be deleted.
        :param uris: URIs of the tracks to be deleted.
        """
        assert (
            positions or uris
        ), "At least one of 'positions' or 'uris' must be specified"
        criteria = {}
        if positions:
            assert self._client, "Mopidy client not running"
            positions = set(positions)
            criteria['tlid'] = list(
                {
                    track.track_id
                    for i, track in enumerate(self._client.tracks)
                    if i in positions
                }
            )
        if uris:
            criteria['uri'] = list(uris)

        return self._exec(
            {
                'method': 'core.tracklist.remove',
                'criteria': criteria,
            }
        )[0]

    @action
    def move(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        position: Optional[int] = None,
        from_pos: Optional[int] = None,
        to_pos: Optional[int] = None,
        **__,
    ):
        """
        Move one or more tracks in the current playlist to a new position.

        You can pass either:

            - ``start``, ``end`` and ``position`` to move a slice of tracks
              from ``start`` to ``end`` to the new position ``position``.
            - ``from_pos`` and ``to_pos`` to move a single track from
              ``from_pos`` to ``to_pos``.

        .. note: Positions are 0-based (i.e. the first track has position 0).

        :param start: Start position of the slice of tracks to be moved.
        :param end: End position of the slice of tracks to be moved.
        :param position: New position where the tracks will be inserted.
        :param from_pos: Alias for ``start`` - it only works with one track at
            the time. Maintained for compatibility with
            :meth:`platypush.plugins.music.mpd.MusicMpdPlugin.move`.
        :param to_pos: Alias for ``position`` - it only works with one track at
            the time. Maintained for compatibility with
            :meth:`platypush.plugins.music.mpd.MusicMpdPlugin.move`.
        """
        assert (from_pos is not None and to_pos is not None) or (
            start is not None and end is not None and position is not None
        ), 'Either "start", "end" and "position", or "from_pos" and "to_pos" must be specified'

        if (from_pos is not None) and (to_pos is not None):
            start, end, position = from_pos, from_pos, to_pos

        ret = self._exec(
            {
                'method': 'core.tracklist.move',
                'start': start,
                'end': end,
                'to_position': position,
            }
        )[0]

        if self._client:
            self._client.refresh_status(with_tracks=True)
        return ret

    @action
    def clear(self, **__):
        """
        Clear the current playlist.
        """
        self._exec_with_status({'method': 'core.tracklist.clear'})

    @action
    def seek(self, position: float, **__):
        """
        Seek to a given position in the current track.

        :param position: Position in seconds.
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        return self._exec_with_status(
            {'method': 'core.playback.seek', 'time_position': int(position * 1000)}
        )

    @action
    def back(self, delta: float = 10, **__):
        """
        Seek back by a given number of seconds.

        :param delta: Number of seconds to seek back (default: 10s).
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if self._status.playing_pos is None:
            return self._dump_status()

        return self.seek(position=self._status.playing_pos - delta)

    @action
    def forward(self, delta: float = 10, **__):
        """
        Seek forward by a given number of seconds.

        :param delta: Number of seconds to seek forward (default: 10s).
        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        if self._status.playing_pos is None:
            return self._dump_status()

        return self.seek(position=self._status.playing_pos + delta)

    @action
    def status(self, **__):
        """
        Get the current Mopidy status.

        :return: .. schema:: mopidy.MopidyStatusSchema
        """
        assert self._client, "Mopidy client not running"
        self._client.refresh_status()
        return self._dump_status()

    @action
    def current_track(self, **__):
        """
        Get the current track.

        :return: .. schema:: mopidy.MopidyTrackSchema
        """
        assert self._client, "Mopidy client not running"
        if not self._client.status.track:
            return None

        return self._client.status.track.to_dict()

    @action
    def get_tracks(self, **__):
        """
        Get the current playlist tracks.

        :return: .. schema:: mopidy.MopidyTrackSchema(many=True)
        """
        assert self._client, "Mopidy client not running"
        return [t.to_dict() for t in self._client.tracks]

    @action
    def get_playlists(self, **__):
        """
        Get the available playlists.

        :return: .. schema:: mopidy.MopidyPlaylistSchema(many=True)
        """
        return MopidyPlaylistSchema().dump(self._get_playlists(), many=True)

    @action
    def get_playlist(self, playlist: str, **__):
        """
        Get the items in a playlist.

        :param playlist: Playlist URI.
        :param only_tracks: If True, only the tracks will be returned, otherwise
            the full playlist object will be returned - including name and other
            metadata.
        :return: .. schema:: mopidy.MopidyTrackSchema(many=True)
        """
        tracks = self._get_playlist_tracks(playlist)
        tracks_by_uri = {t.uri: t for t in tracks if t.uri}
        looked_up = self._lookup(*tracks_by_uri.keys())
        return [
            track.to_dict()
            for track in [
                (looked_up[uri][0] if looked_up.get(uri) else track)
                for uri, track in tracks_by_uri.items()
            ]
        ]

    @action
    def get_playlist_uri_schemes(self, **__):
        """
        Get the available playlist URI schemes.

        :return: List of available playlist URI schemes.
        """
        return self._exec({'method': 'core.playlists.get_uri_schemes'})[0]

    @action
    def create_playlist(self, name: str, uri_scheme: str = 'm3u', **__):
        """
        Create a new playlist.

        :param name: Playlist name.
        :param uri_scheme: URI scheme for the playlist (default: ``m3u``).
            You can get a full list of the available URI schemes that support
            playlist creation on the Mopidy instance by calling
            :meth:`.get_playlist_uri_schemes`.
        :return: .. schema:: mopidy.MopidyPlaylistSchema
        """
        return MopidyPlaylistSchema().dump(
            self._exec(
                {
                    'method': 'core.playlists.create',
                    'name': name,
                    'uri_scheme': uri_scheme,
                }
            )[0]
        )

    @action
    def delete_playlist(self, playlist: str, **__):
        """
        Delete a playlist.

        :param playlist: Playlist URI.
        :return: ``True`` if the playlist was deleted, ``False`` otherwise.
        """
        return self._exec({'method': 'core.playlists.delete', 'uri': playlist})[0]

    @action
    def add_to_playlist(
        self,
        playlist: str,
        resources: Iterable[str],
        position: Optional[int] = None,
        allow_duplicates: bool = False,
        **__,
    ):
        """
        Add tracks to a playlist.

        :param playlist: Playlist URI/name.
        :param resources: List of track URIs.
        :param position: Position where the tracks will be inserted (default:
            end of the playlist).
        :param allow_duplicates: If True, the tracks will be added even if they
            are already present in the playlist (default: False).
        :return: The modified playlist.
            .. schema:: mopidy.MopidyPlaylistSchema
        """
        pl = self._get_playlist(playlist, with_tracks=True)

        if not allow_duplicates:
            existing_uris = {t.uri for t in pl.tracks}
            resources = [t for t in resources if t not in existing_uris]

        new_tracks = [MopidyTrack(uri=t) for t in resources]
        if position is not None:
            pl.tracks = pl.tracks[:position] + new_tracks + pl.tracks[position:]
        else:
            pl.tracks += new_tracks

        self._save_playlist(pl)
        return pl.to_dict()

    @action
    def remove_from_playlist(
        self,
        playlist: str,
        resources: Optional[Iterable[Union[str, int]]] = None,
        from_pos: Optional[int] = None,
        to_pos: Optional[int] = None,
        **__,
    ):
        """
        Remove tracks from a playlist.

        This action can work in three different ways:

            - If the ``resources`` parameter is specified, and it contains
              strings, it will remove the tracks matching the provided URIs.
            - If the ``resources`` parameter is specified, and it contains
              integers, it will remove the tracks in the specified positions.
            - If the ``from_pos`` and ``to_pos`` parameters are specified, it
              will remove the tracks in the specified range (inclusive).

        .. note: Positions are 0-based (i.e. the first track has position 0).

        :param playlist: Playlist URI/name.
        :param tracks: List of track URIs.
        :param from_pos: Start position of the slice of tracks to be removed.
        :param to_pos: End position of the slice of tracks to be removed.
        :return: The modified playlist.
            .. schema:: mopidy.MopidyPlaylistSchema
        """
        assert resources or (
            from_pos is not None and to_pos is not None
        ), "Either 'tracks', or 'positions', or 'from_pos' and 'to_pos' must be specified"

        pl = self._get_playlist(playlist, with_tracks=True)

        if resources:
            resources = set(resources)
            positions = {
                i
                for i, t in enumerate(pl.tracks)
                if t.uri in resources or i in resources
            }

            pl.tracks = [t for i, t in enumerate(pl.tracks) if i not in positions]
        elif from_pos is not None and to_pos is not None:
            from_pos, to_pos = (min(from_pos, to_pos), max(from_pos, to_pos))
            pl.tracks = pl.tracks[: from_pos - 1] + pl.tracks[to_pos:]

        self._save_playlist(pl)
        return pl.to_dict()

    @action
    def playlist_move(
        self,
        playlist: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        position: Optional[int] = None,
        from_pos: Optional[int] = None,
        to_pos: Optional[int] = None,
        **__,
    ):
        """
        Move tracks in a playlist.

        This action can work in two different ways:

            - If the ``start``, ``end`` and ``position`` parameters are
              specified, it will move an individual track from the position
              ``start`` to the position ``end`` to the new position
              ``position``.

            - If the ``from_pos``, ``to_pos`` and ``position`` parameters are
              specified, it will move the tracks in the specified range
              (inclusive) to the new position ``position``.

        .. note: Positions are 0-based (i.e. the first track has position 0).

        :param playlist: Playlist URI.
        :param start: Start position of the slice of tracks to be moved.
        :param end: End position of the slice of tracks to be moved.
        :param position: New position where the tracks will be inserted.
        :return: The modified playlist.
            .. schema:: mopidy.MopidyPlaylistSchema
        """
        assert (start is not None and end is not None and position is not None) or (
            from_pos is not None and to_pos is not None
        ), "Either 'start', 'end' and 'position', or 'from_pos' and 'to_pos' must be specified"

        pl = self._get_playlist(playlist, with_tracks=True)

        if from_pos is not None and to_pos is not None:
            from_pos, to_pos = (min(from_pos, to_pos), max(from_pos, to_pos))
            pl.tracks = (
                pl.tracks[:from_pos]
                + pl.tracks[to_pos : to_pos + 1]
                + pl.tracks[from_pos + 1 : to_pos]
                + pl.tracks[from_pos : from_pos + 1]
                + pl.tracks[to_pos + 1 :]
            )
        elif start is not None and end is not None and position is not None:
            start, end = (min(start, end), max(start, end))
            if start == end:
                end += 1

            if start < position:
                pl.tracks = (
                    pl.tracks[:start]
                    + pl.tracks[end : end + (position - start)]
                    + pl.tracks[start:end]
                    + pl.tracks[end + (position - start) :]
                )
            else:
                pl.tracks = (
                    pl.tracks[:position]
                    + pl.tracks[start:end]
                    + pl.tracks[position:start]
                    + pl.tracks[end:]
                )

        self._save_playlist(pl)
        return pl.to_dict()

    @action
    def playlist_clear(self, playlist: str, **__):
        """
        Remove all the tracks from a playlist.

        :param playlist: Playlist URI/name.
        :return: The modified playlist.
            .. schema:: mopidy.MopidyPlaylistSchema
        """
        pl = self._get_playlist(playlist)
        pl.tracks = []
        self._save_playlist(pl)
        return pl.to_dict()

    @action
    def rename_playlist(self, playlist: str, new_name: str, **__):
        """
        Rename a playlist.

        :param playlist: Playlist URI/name.
        :param new_name: New playlist name.
        :return: The modified playlist.
            .. schema:: mopidy.MopidyPlaylistSchema
        """
        pl = self._get_playlist(playlist, with_tracks=True)
        pl.name = new_name
        self._save_playlist(pl)
        return pl.to_dict()

    @action
    def get_images(self, resources: Iterable[str], **__) -> Dict[str, Optional[str]]:
        """
        Get the images for a list of URIs.

        :param resources: List of URIs.
        :return: Dictionary in the form ``{uri: image_url}``.
        """
        return {
            uri: next(iter(images or []), {}).get('uri')
            for uri, images in self._exec(
                {'method': 'core.library.get_images', 'uris': list(resources)}
            )[0].items()
        }

    @action
    def search(  # pylint: disable=redefined-builtin
        self, filter: dict, exact: bool = False, **__
    ):
        """
        Search items that match the given query.

        :param filter: .. schema:: mopidy.MopidyFilterSchema
        :param exact: If True, the search will only return exact matches.
        :return: A list of result, including:

            - Tracks
                .. schema:: mopidy.MopidyTrackSchema(many=True)
            - Albums
                .. schema:: mopidy.MopidyAlbumSchema(many=True)
            - Artists
                .. schema:: mopidy.MopidyArtistSchema(many=True)

        """
        filter = dict(MopidyFilterSchema().load(filter) or {})
        uris = filter.pop('uris', None)
        kwargs = {
            'exact': exact,
            'query': filter,
            **({'uris': uris} if uris else {}),
        }

        return self._dump_search_results(
            self._exec({'method': 'core.library.search', **kwargs})[0]
        )

    @action
    def find(  # pylint: disable=redefined-builtin
        self, filter: dict, exact: bool = False, **__
    ):
        """
        Alias for :meth:`search`, for MPD compatibility.

        :param filter: .. schema:: mopidy.MopidyFilterSchema
        :param exact: If True, the search will only return exact matches.
        :return: .. schema:: mopidy.MopidyTrackSchema(many=True)
        """
        return self.search(filter=filter, exact=exact)

    @action
    def browse(self, uri: Optional[str] = None):
        """
        Browse the items under the specified URI.

        :param uri: URI to browse (default: root directory).
        :return: A list of result under the specified resource, including:

            - Directories
                .. schema:: mopidy.MopidyDirectorySchema(many=True)
            - Tracks
                .. schema:: mopidy.MopidyTrackSchema(many=True)
            - Albums
                .. schema:: mopidy.MopidyAlbumSchema(many=True)
            - Artists
                .. schema:: mopidy.MopidyArtistSchema(many=True)

        """
        return self._dump_results(
            self._exec({'method': 'core.library.browse', 'uri': uri})[0]
        )

    def main(self):
        while not self.should_stop():
            try:
                with MopidyClient(
                    config=self.config,
                    status=self._status,
                    stop_event=self._should_stop,
                    playlist_sync=self._playlist_sync,
                    tasks=self._tasks,
                ) as self._client:
                    self._client.start()
                    wait_for_either(self._should_stop, self._client.closed_event)
            finally:
                self._client = None
                self.wait_stop(10)


__all__ = ['EmptyTrackException', 'MusicMopidyPlugin', 'MopidyStatus', 'MopidyTrack']


# vim:sw=4:ts=4:et:
