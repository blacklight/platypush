from datetime import datetime
from typing import List, Optional, Union, Iterable

from platypush.common.spotify import SpotifyMixin
from platypush.message.response import Response
from platypush.plugins import action
from platypush.plugins.media import PlayerState
from platypush.plugins.music import MusicPlugin
from platypush.schemas.spotify import (
    SpotifyDeviceSchema,
    SpotifyStatusSchema,
    SpotifyTrackSchema,
    SpotifyHistoryItemSchema,
    SpotifyPlaylistSchema,
    SpotifyAlbumSchema,
    SpotifyEpisodeSchema,
    SpotifyShowSchema,
    SpotifyArtistSchema,
)


class MusicSpotifyPlugin(MusicPlugin, SpotifyMixin):
    """
    Plugin to interact with the user's Spotify library and players.

    In order to use this plugin to interact with your Spotify account you need to register a new app on the Spotify
    developers website, whitelist the callback URL of your Platypush host and authorize the app to your account:

        - Create a developer app on https://developer.spotify.com.
        - Get the app's ``client_id`` and ``client_secret``.
        - Whitelist the authorization callback URL on the Platypush machine, usually in the form
          ``http(s)://your-platypush-hostname-or-local-ip:8008/spotify/auth_callback`` (you need the
          ``http`` Platypush backend to be enabled).
        - You can then authorize the app by opening the following URL in a browser:
          ``https://accounts.spotify.com/authorize?client_id=<client_id>&response_type=code&redirect_uri=http(s)://your-platypush-hostname-or-local-ip:8008/spotify/auth_callback&scope=<comma-separated-list-of-scopes>&state=<some-random-string>``.

    This is the list of scopes required for full plugin functionalities:

        - ``user-read-playback-state``
        - ``user-modify-playback-state``
        - ``user-read-currently-playing``
        - ``user-read-recently-played``
        - ``app-remote-control``
        - ``streaming``
        - ``playlist-modify-public``
        - ``playlist-modify-private``
        - ``playlist-read-private``
        - ``playlist-read-collaborative``
        - ``user-library-modify``
        - ``user-library-read``

    Alternatively, you can call any of the methods from this plugin over HTTP API, and the full authorization URL should
    be printed on the application logs/stdout.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        **kwargs,
    ):
        MusicPlugin.__init__(self, **kwargs)
        SpotifyMixin.__init__(
            self, client_id=client_id, client_secret=client_secret, **kwargs
        )
        self._players_by_id = {}
        self._players_by_name = {}
        # Playlist ID -> snapshot ID and tracks cache
        self._playlist_snapshots = {}

    def _get_device(self, device: str):
        dev = self._players_by_id.get(device, self._players_by_name.get(device))
        if not dev:
            self.get_devices()

        dev = self._players_by_id.get(device, self._players_by_name.get(device))
        assert dev, f'No such device: {device}'
        return dev

    @staticmethod
    def _parse_datetime(
        dt: Optional[Union[str, datetime, int, float]]
    ) -> Optional[datetime]:
        if isinstance(dt, str):
            try:
                dt = float(dt)
            except (ValueError, TypeError):
                return datetime.fromisoformat(dt)

        if isinstance(dt, (int, float)):
            return datetime.fromtimestamp(dt)

        return dt

    @action
    def get_devices(self) -> List[dict]:
        """
        Get the list of players associated to the Spotify account.

        :return: .. schema:: spotify.SpotifyDeviceSchema(many=True)
        """
        devices = self.spotify_user_call('/v1/me/player/devices').get('devices', [])
        self._players_by_id = {
            **self._players_by_id,
            **{dev['id']: dev for dev in devices},
        }

        self._players_by_name = {
            **self._players_by_name,
            **{dev['name']: dev for dev in devices},
        }

        return SpotifyDeviceSchema().dump(devices, many=True)

    @action
    def set_volume(self, volume: int, device: Optional[str] = None):
        """
        Set the playback volume on a device.

        :param volume: Target volume as a percentage between 0 and 100.
        :param device: Device ID or name. If none is specified then the currently active device will be used.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/volume',
            method='put',
            params={
                'volume_percent': volume,
                **({'device_id': device} if device else {}),
            },
        )

    def _get_volume(self, device: Optional[str] = None) -> Optional[int]:
        if device:
            return self._get_device(device).get('volume')

        return self.status.output.get('volume')

    @action
    def volup(self, delta: int = 5, device: Optional[str] = None):
        """
        Set the volume up by a certain delta.

        :param delta: Increase the volume by this percentage amount (between 0 and 100).
        :param device: Device ID or name. If none is specified then the currently active device will be used.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/volume',
            params={
                'volume_percent': min(100, (self._get_volume() or 0) + delta),
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def voldown(self, delta: int = 5, device: Optional[str] = None):
        """
        Set the volume down by a certain delta.

        :param delta: Decrease the volume by this percentage amount (between 0 and 100).
        :param device: Device ID or name. If none is specified then the currently active device will be used.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/volume',
            params={
                'volume_percent': max(0, (self._get_volume() or 0) - delta),
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def play(self, resource: Optional[str] = None, device: Optional[str] = None):
        """
        Change the playback state of a device to ``PLAY`` or start playing a specific resource.

        :param resource: Resource to play, in Spotify URI format (e.g. ``spotify:track:xxxxxxxxxxxxxxxxxxxxxx``).
            If none is specified then the method will change the playback state to ``PLAY``.
        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/play',
            method='put',
            json={'uris': [resource]} if resource else {},
            params={
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def pause(self, device: Optional[str] = None):
        """
        Toggle paused state.

        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        # noinspection PyUnresolvedReferences
        status = self.status().output
        state = (
            'play'
            if status.get('device_id') != device
            or status.get('state') != PlayerState.PLAY.value
            else 'pause'
        )

        self.spotify_user_call(
            f'/v1/me/player/{state}',
            method='put',
            params={
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def pause_if_playing(self):
        """
        Pause playback only if it's playing
        """
        # noinspection PyUnresolvedReferences
        status = self.status().output
        if status.get('state') == PlayerState.PLAY.value:
            self.spotify_user_call(
                '/v1/me/player/pause',
                method='put',
            )

    @action
    def play_if_paused(self, device: Optional[str] = None):
        """
        Play only if it's paused (resume)

        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        # noinspection PyUnresolvedReferences
        status = self.status().output
        if status.get('state') != PlayerState.PLAY.value:
            self.spotify_user_call(
                '/v1/me/player/play',
                method='put',
                params={
                    **({'device_id': device} if device else {}),
                },
            )

    @action
    def play_if_paused_or_stopped(self):
        """
        Alias for :meth:`.play_if_paused`.
        """
        return self.play_if_paused()

    @action
    def stop(self, **kwargs):
        """
        This method is actually just an alias to :meth:`.stop`, since Spotify manages clearing playback sessions
        automatically after a while for paused devices.
        """
        return self.pause(**kwargs)

    @action
    def start_or_transfer_playback(self, device: str):
        """
        Start or transfer playback to the device specified.

        :param device: Device ID or name.
        """
        device = self._get_device(device)['id']
        self.spotify_user_call(
            '/v1/me/player',
            method='put',
            json={
                'device_ids': [device],
            },
        )

    @action
    def next(self, device: Optional[str] = None, **kwargs):
        """
        Skip to the next track.

        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/next',
            method='post',
            params={
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def previous(self, device: Optional[str] = None, **kwargs):
        """
        Skip to the next track.

        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/previous',
            method='post',
            params={
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def seek(self, position: float, device: Optional[str] = None, **kwargs):
        """
        Set the cursor to the specified position in the track.

        :param position: Position in seconds.
        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/seek',
            method='put',
            params={
                'position_ms': int(position * 1000),
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def repeat(self, value: Optional[bool] = None, device: Optional[str] = None):
        """
        Set or toggle repeat mode.

        :param value: If set, set the repeat state this value (true/false). Default: None (toggle current state).
        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        if value is None:
            # noinspection PyUnresolvedReferences
            status = self.status().output
            state = (
                'context'
                if status.get('device_id') != device or not status.get('repeat')
                else 'off'
            )
        else:
            state = value is True

        self.spotify_user_call(
            '/v1/me/player/repeat',
            method='put',
            params={
                'state': 'context' if state else 'off',
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def random(self, value: Optional[bool] = None, device: Optional[str] = None):
        """
        Set or toggle random/shuffle mode.

        :param value: If set, set the shuffle state this value (true/false). Default: None (toggle current state).
        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        if value is None:
            # noinspection PyUnresolvedReferences
            status = self.status().output
            state = bool(status.get('device_id') != device or not status.get('random'))
        else:
            state = value is True

        self.spotify_user_call(
            '/v1/me/player/shuffle',
            method='put',
            params={
                'state': state,
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def history(
        self,
        limit: int = 20,
        before: Optional[Union[datetime, str, int]] = None,
        after: Optional[Union[datetime, str, int]] = None,
    ):
        """
        Get a list of recently played track on the account.

        :param limit: Maximum number of tracks to be retrieved (default: 20, max: 50).
        :param before: Retrieve only the tracks played before this timestamp, specified as a UNIX timestamp, a datetime
            object or an ISO datetime string. If ``before`` is set then ``after`` cannot be set.
        :param after: Retrieve only the tracks played after this timestamp, specified as a UNIX timestamp, a datetime
            object or an ISO datetime string. If ``after`` is set then ``before`` cannot be set.
        :return:
        """
        before = self._parse_datetime(before)
        after = self._parse_datetime(after)
        assert not (before and after), 'before and after cannot both be set'

        results = self._spotify_paginate_results(
            '/v1/me/player/recently-played',
            limit=limit,
            params={
                'limit': min(limit, 50),
                **({'before': before} if before else {}),
                **({'after': after} if after else {}),
            },
        )

        return SpotifyHistoryItemSchema().dump(
            [
                {
                    **item.pop('track'),
                    **item,
                }
                for item in results
            ],
            many=True,
        )

    @action
    def add(self, resource: str, device: Optional[str] = None, **kwargs):
        """
        Add a Spotify resource (track, or episode) to the playing queue.

        :param resource: Spotify resource URI.
        :param device: Device ID or name. If none is specified then the action will target the currently active device.
        """
        if device:
            device = self._get_device(device)['id']

        self.spotify_user_call(
            '/v1/me/player/queue',
            method='post',
            params={
                'uri': resource,
                **({'device_id': device} if device else {}),
            },
        )

    @action
    def clear(self, **kwargs):
        pass

    @action
    def status(self, **kwargs) -> dict:
        """
        Get the status of the currently active player.

        :return: .. schema:: spotify.SpotifyStatusSchema
        """
        status = self.spotify_user_call('/v1/me/player')
        if not status:
            return {
                'state': PlayerState.STOP.value,
            }

        return SpotifyStatusSchema().dump(status)

    @action
    def current_track(self, **kwargs) -> dict:
        """
        Get the track currently playing.

        :return: .. schema:: spotify.SpotifyTrackSchema
        """
        status = self.spotify_user_call('/v1/me/player')
        empty_response = Response(output={})
        if not status:
            # noinspection PyTypeChecker
            return empty_response

        track = status.get('item', {})
        if not track:
            # noinspection PyTypeChecker
            return empty_response

        return SpotifyTrackSchema().dump(track)

    @action
    def get_playlists(
        self, limit: int = 1000, offset: int = 0, user: Optional[str] = None
    ):
        """
        Get the user's playlists.

        :param limit: Maximum number of results (default: 1000).
        :param offset: Return results starting from this index (default: 0).
        :param user: Return the playlist owned by a specific user ID (default: currently logged in user).
        :return: .. schema:: spotify.SpotifyPlaylistSchema
        """
        playlists = self._spotify_paginate_results(
            f'/v1/{"users/" + user if user else "me"}/playlists',
            limit=limit,
            offset=offset,
        )

        return SpotifyPlaylistSchema().dump(playlists, many=True)

    def _get_playlist(self, playlist: str) -> dict:
        playlists = self.get_playlists().output
        playlists = [
            pl
            for pl in playlists
            if (pl['id'] == playlist or pl['uri'] == playlist or pl['name'] == playlist)
        ]

        assert playlists, f'No such playlist ID, URI or name: {playlist}'
        return playlists[0]

    def _get_playlist_tracks_from_cache(
        self, id: str, snapshot_id: str, limit: Optional[int] = None, offset: int = 0
    ) -> Optional[Iterable]:
        snapshot = self._playlist_snapshots.get(id)
        if (
            not snapshot
            or snapshot['snapshot_id'] != snapshot_id
            or (limit is None and snapshot['limit'] is not None)
        ):
            return

        if limit is not None and snapshot['limit'] is not None:
            stored_range = (snapshot['limit'], snapshot['limit'] + snapshot['offset'])
            requested_range = (limit, limit + offset)
            if (
                requested_range[0] < stored_range[0]
                or requested_range[1] > stored_range[1]
            ):
                return

        return snapshot['tracks']

    def _cache_playlist_data(
        self,
        id: str,
        snapshot_id: str,
        tracks: Iterable[dict],
        limit: Optional[int] = None,
        offset: int = 0,
        **_,
    ):
        self._playlist_snapshots[id] = {
            'id': id,
            'tracks': tracks,
            'snapshot_id': snapshot_id,
            'limit': limit,
            'offset': offset,
        }

    @action
    def get_playlist(
        self,
        playlist: str,
        with_tracks: bool = True,
        limit: Optional[int] = None,
        offset: int = 0,
    ):
        """
        Get a playlist content.

        :param playlist: Playlist name, ID or URI.
        :param with_tracks: Return also the playlist tracks (default: false, return only the metadata).
        :param limit: If ``with_tracks`` is True, retrieve this maximum amount of tracks
            (default: None, get all tracks).
        :param offset: If ``with_tracks`` is True, retrieve tracks starting from this index (default: 0).
        :return: .. schema:: spotify.SpotifyPlaylistSchema
        """
        playlist = self._get_playlist(playlist)
        if with_tracks:
            playlist['tracks'] = self._get_playlist_tracks_from_cache(
                playlist['id'],
                snapshot_id=playlist['snapshot_id'],
                limit=limit,
                offset=offset,
            )

            if playlist['tracks'] is None:
                playlist['tracks'] = [
                    {
                        **track,
                        'track': {
                            **track['track'],
                            'position': offset + i + 1,
                        },
                    }
                    for i, track in enumerate(
                        self._spotify_paginate_results(
                            f'/v1/playlists/{playlist["id"]}/tracks',
                            limit=limit,
                            offset=offset,
                        )
                    )
                ]

                self._cache_playlist_data(**playlist, limit=limit, offset=offset)

        return SpotifyPlaylistSchema().dump(playlist)

    @action
    def add_to_playlist(
        self,
        playlist: str,
        resources: Union[str, Iterable[str]],
        position: Optional[int] = None,
    ):
        """
        Add one or more items to a playlist.

        :param playlist: Playlist name, ID or URI.
        :param resources: URI(s) of the resource(s) to be added.
        :param position: At what (1-based) position the tracks should be inserted (default: append to the end).
        """
        playlist = self._get_playlist(playlist)
        response = self.spotify_user_call(
            f'/v1/playlists/{playlist["id"]}/tracks',
            method='post',
            params={
                **({'position': position} if position is not None else {}),
            },
            json={
                'uris': [
                    uri.strip()
                    for uri in (
                        resources.split(',')
                        if isinstance(resources, str)
                        else resources
                    )
                ]
            },
        )

        snapshot_id = response.get('snapshot_id')
        assert snapshot_id is not None, 'Could not save playlist'

    @action
    def remove_from_playlist(self, playlist: str, resources: Union[str, Iterable[str]]):
        """
        Remove one or more items from a playlist.

        :param playlist: Playlist name, ID or URI.
        :param resources: URI(s) of the resource(s) to be removed. A maximum of 100 tracks can be provided at once.
        """
        playlist = self._get_playlist(playlist)
        response = self.spotify_user_call(
            f'/v1/playlists/{playlist["id"]}/tracks',
            method='delete',
            json={
                'tracks': [
                    {'uri': uri.strip()}
                    for uri in (
                        resources.split(',')
                        if isinstance(resources, str)
                        else resources
                    )
                ]
            },
        )

        snapshot_id = response.get('snapshot_id')
        assert snapshot_id is not None, 'Could not save playlist'

    @action
    def playlist_move(
        self,
        playlist: str,
        from_pos: int,
        to_pos: int,
        range_length: int = 1,
        resources: Optional[Union[str, Iterable[str]]] = None,
        **_,
    ):
        """
        Move or replace elements in a playlist.

        :param playlist: Playlist name, ID or URI.
        :param from_pos: Move tracks starting from this position (the first element has index 1).
        :param to_pos: Move tracks to this position (1-based index).
        :param range_length: Number of tracks to move (default: 1).
        :param resources: If specified, then replace the items from `from_pos` to `from_pos+range_length` with the
            specified set of Spotify URIs (it must be a collection with the same length as the range).
        """
        playlist = self._get_playlist(playlist)
        response = self.spotify_user_call(
            f'/v1/playlists/{playlist["id"]}/tracks',
            method='put',
            json={
                'range_start': int(from_pos) + 1,
                'range_length': int(range_length),
                'insert_before': int(to_pos) + 1,
                **(
                    {
                        'uris': [
                            uri.strip()
                            for uri in (
                                resources.split(',')
                                if isinstance(resources, str)
                                else resources
                            )
                        ]
                    }
                    if resources
                    else {}
                ),
            },
        )

        snapshot_id = response.get('snapshot_id')
        assert snapshot_id is not None, 'Could not save playlist'

    # noinspection PyShadowingBuiltins
    @staticmethod
    def _make_filter(query: Union[str, dict], **filter) -> str:
        if filter:
            query = {
                **({'any': query} if isinstance(query, str) else {}),
                **filter,
            }

        if isinstance(query, str):
            return query

        q = query['any'] if 'any' in query else ''
        for attr in ['artist', 'track', 'album', 'year']:
            if attr in query:
                q += f' {attr}:{query[attr]}'

        return q.strip()

    # noinspection PyShadowingBuiltins
    @action
    def search(
        self,
        query: Optional[Union[str, dict]] = None,
        limit: int = 50,
        offset: int = 0,
        type: str = 'track',
        **filter,
    ) -> Iterable[dict]:
        """
        Search for tracks matching a certain criteria.

        :param query: Search filter. It can either be a free-text or a structured query. In the latter case the
            following fields are supported:

                - ``any``: Search for anything that matches this text.
                - ``uri``: Search the following Spotify ID/URI or list of IDs/URIs.
                - ``artist``: Filter by artist.
                - ``track``: Filter by track name.
                - ``album``: Filter by album name.
                - ``year``: Filter by year (dash-separated ranges are supported).

        :param limit: Maximum number of results (default: 50).
        :param offset: Return results starting from this index (default: 0).
        :param type: Type of results to be returned. Supported: ``album``, ``artist``, ``playlist``, ``track``, ``show``
            and ``episode`` (default: ``track``).
        :param filter: Alternative key-value way of representing a structured query.
        :return:
            If ``type=track``:
                .. schema:: spotify.SpotifyTrackSchema(many=True)
            If ``type=album``:
                .. schema:: spotify.SpotifyAlbumSchema(many=True)
            If ``type=artist``:
                .. schema:: spotify.SpotifyArtistSchema(many=True)
            If ``type=playlist``:
                .. schema:: spotify.SpotifyPlaylistSchema(many=True)
            If ``type=episode``:
                .. schema:: spotify.SpotifyEpisodeSchema(many=True)
            If ``type=show``:
                .. schema:: spotify.SpotifyShowSchema(many=True)

        """
        uri = {
            **(query if isinstance(query, dict) else {}),
            **filter,
        }.get('uri', [])

        uris = uri.split(',') if isinstance(uri, str) else uri
        params = (
            {
                'ids': ','.join([uri.split(':')[-1].strip() for uri in uris]),
            }
            if uris
            else {
                'q': self._make_filter(query, **filter),
                'type': type,
            }
        )

        response = self._spotify_paginate_results(
            f'/v1/{type + "s" if uris else "search"}',
            limit=limit,
            offset=offset,
            type=type,
            params=params,
        )

        if type == 'track':
            return sorted(
                SpotifyTrackSchema(many=True).dump(response),
                key=lambda track: (
                    track.get('artist'),
                    track.get('date'),
                    track.get('album'),
                    track.get('track'),
                    track.get('title'),
                    track.get('popularity'),
                ),
            )

        schema_class = None
        if type == 'playlist':
            schema_class = SpotifyPlaylistSchema
        if type == 'album':
            schema_class = SpotifyAlbumSchema
        if type == 'artist':
            schema_class = SpotifyArtistSchema
        if type == 'episode':
            schema_class = SpotifyEpisodeSchema
        if type == 'show':
            schema_class = SpotifyShowSchema

        if schema_class:
            return schema_class(many=True).dump(response)

        return response

    @action
    def create_playlist(
        self, name: str, description: Optional[str] = None, public: bool = False
    ):
        """
        Create a playlist.

        :param name: Playlist name.
        :param description: Optional playlist description.
        :param public: Whether the new playlist should be public
            (default: False).
        :return: .. schema:: spotify.SpotifyPlaylistSchema
        """
        ret = self.spotify_user_call(
            '/v1/users/me/playlists',
            method='post',
            json={
                'name': name,
                'description': description,
                'public': public,
            },
        )

        return SpotifyPlaylistSchema().dump(ret)

    @action
    def follow_playlist(self, playlist: str, public: bool = True):
        """
        Follow a playlist.

        :param playlist: Playlist name, ID or URI.
        :param public: If True (default) then the playlist will appear in the user's list of public playlists, otherwise
            it won't.
        """
        playlist = self._get_playlist(playlist)
        self.spotify_user_call(
            f'/v1/playlists/{playlist["id"]}/followers',
            method='put',
            json={
                'public': public,
            },
        )

    @action
    def unfollow_playlist(self, playlist: str):
        """
        Unfollow a playlist.

        :param playlist: Playlist name, ID or URI.
        """
        playlist = self._get_playlist(playlist)
        self.spotify_user_call(
            f'/v1/playlists/{playlist["id"]}/followers',
            method='delete',
        )

    @staticmethod
    def _uris_to_id(*uris: str) -> Iterable[str]:
        return [uri.split(':')[-1] for uri in uris]

    @action
    def get_albums(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """
        Get the list of albums saved by the user.

        :param limit: Maximum number of results (default: 50).
        :param offset: Return results starting from this index (default: 0).
        :return: .. schema:: spotify.SpotifyAlbumSchema(many=True)
        """
        return SpotifyAlbumSchema().dump(
            self._spotify_paginate_results(
                '/v1/me/albums',
                limit=limit,
                offset=offset,
            ),
            many=True,
        )

    @action
    def save_albums(self, resources: Iterable[str]):
        """
        Save a list of albums to the user's collection.

        :param resources: Spotify IDs or URIs of the albums to save.
        """
        self.spotify_user_call(
            '/v1/me/albums',
            method='put',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def remove_albums(self, resources: Iterable[str]):
        """
        Remove a list of albums from the user's collection.

        :param resources: Spotify IDs or URIs of the albums to remove.
        """
        self.spotify_user_call(
            '/v1/me/albums',
            method='delete',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def get_tracks(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """
        Get the list of tracks saved by the user.

        :param limit: Maximum number of results (default: 100).
        :param offset: Return results starting from this index (default: 0).
        :return: .. schema:: spotify.SpotifyTrackSchema(many=True)
        """
        return [
            SpotifyTrackSchema().dump(item['track'])
            for item in self._spotify_paginate_results(
                '/v1/me/tracks', limit=limit, offset=offset
            )
        ]

    @action
    def save_tracks(self, resources: Iterable[str]):
        """
        Save a list of tracks to the user's collection.

        :param resources: Spotify IDs or URIs of the tracks to save.
        """
        self.spotify_user_call(
            '/v1/me/tracks',
            method='put',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def remove_tracks(self, resources: Iterable[str]):
        """
        Remove a list of tracks from the user's collection.

        :param resources: Spotify IDs or URIs of the tracks to remove.
        """
        self.spotify_user_call(
            '/v1/me/tracks',
            method='delete',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def get_episodes(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """
        Get the list of episodes saved by the user.

        :param limit: Maximum number of results (default: 50).
        :param offset: Return results starting from this index (default: 0).
        :return: .. schema:: spotify.SpotifyEpisodeSchema(many=True)
        """
        return SpotifyEpisodeSchema().dump(
            self._spotify_paginate_results(
                '/v1/me/episodes',
                limit=limit,
                offset=offset,
            ),
            many=True,
        )

    @action
    def save_episodes(self, resources: Iterable[str]):
        """
        Save a list of episodes to the user's collection.

        :param resources: Spotify IDs or URIs of the episodes to save.
        """
        self.spotify_user_call(
            '/v1/me/episodes',
            method='put',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def remove_episodes(self, resources: Iterable[str]):
        """
        Remove a list of episodes from the user's collection.

        :param resources: Spotify IDs or URIs of the episodes to remove.
        """
        self.spotify_user_call(
            '/v1/me/episodes',
            method='delete',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def get_shows(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """
        Get the list of shows saved by the user.

        :param limit: Maximum number of results (default: 50).
        :param offset: Return results starting from this index (default: 0).
        :return: .. schema:: spotify.SpotifyShowSchema(many=True)
        """
        return SpotifyShowSchema().dump(
            self._spotify_paginate_results(
                '/v1/me/shows',
                limit=limit,
                offset=offset,
            ),
            many=True,
        )

    @action
    def save_shows(self, resources: Iterable[str]):
        """
        Save a list of shows to the user's collection.

        :param resources: Spotify IDs or URIs of the shows to save.
        """
        self.spotify_user_call(
            '/v1/me/shows',
            method='put',
            json={'ids': self._uris_to_id(*resources)},
        )

    @action
    def remove_shows(self, resources: Iterable[str]):
        """
        Remove a list of shows from the user's collection.

        :param resources: Spotify IDs or URIs of the shows to remove.
        """
        self.spotify_user_call(
            '/v1/me/shows',
            method='delete',
            json={'ids': self._uris_to_id(*resources)},
        )
