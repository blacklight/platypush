import json
import os
import pathlib

from datetime import datetime
from typing import Iterable, Optional, Union

from platypush.config import Config
from platypush.context import Variable, get_bus
from platypush.message.event.music.tidal import TidalPlaylistUpdatedEvent
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.music.tidal.workers import get_items
from platypush.schemas.tidal import (
    TidalAlbumSchema,
    TidalPlaylistSchema,
    TidalArtistSchema,
    TidalSearchResultsSchema,
    TidalTrackSchema,
)


class MusicTidalPlugin(RunnablePlugin):
    """
    Plugin to interact with the user's Tidal account and library.

    Upon the first login, the application will prompt you with a link to
    connect to your Tidal account. Once authorized, you should no longer be
    required to explicitly login.

    Triggers:

        * :class:`platypush.message.event.music.TidalPlaylistUpdatedEvent`: when a user playlist
          is updated.

    Requires:

        * **tidalapi** (``pip install 'tidalapi >= 0.7.0'``)

    """

    _base_url = 'https://api.tidalhifi.com/v1/'
    _default_credentials_file = os.path.join(
        str(Config.get('workdir')), 'tidal', 'credentials.json'
    )

    def __init__(
        self,
        quality: str = 'high',
        credentials_file: str = _default_credentials_file,
        **kwargs,
    ):
        """
        :param quality: Default audio quality. Default: ``high``.
            Supported: [``loseless``, ``master``, ``high``, ``low``].
        :param credentials_file: Path to the file where the OAuth session
            parameters will be stored (default:
            ``<WORKDIR>/tidal/credentials.json``).
        """
        from tidalapi import Quality

        super().__init__(**kwargs)
        self._credentials_file = os.path.expanduser(credentials_file)
        self._user_playlists = {}

        try:
            self._quality = getattr(Quality, quality.lower())
        except AttributeError:
            raise AssertionError(
                f'Invalid quality: {quality}. Supported values: '
                f'{[q.name for q in Quality]}'
            )

        self._session = None

    def _oauth_open_saved_session(self):
        if not self._session:
            return

        try:
            with open(self._credentials_file, 'r') as f:
                data = json.load(f)
                self._session.load_oauth_session(
                    data['token_type'], data['access_token'], data['refresh_token']
                )
        except Exception as e:
            self.logger.warning('Could not load %s: %s', self._credentials_file, e)

    def _oauth_create_new_session(self):
        if not self._session:
            return

        self._session.login_oauth_simple(function=self.logger.warning)  # type: ignore
        if self._session.check_login():
            data = {
                'token_type': self._session.token_type,
                'session_id': self._session.session_id,
                'access_token': self._session.access_token,
                'refresh_token': self._session.refresh_token,
            }

            pathlib.Path(os.path.dirname(self._credentials_file)).mkdir(
                parents=True, exist_ok=True
            )

            with open(self._credentials_file, 'w') as outfile:
                json.dump(data, outfile)

    @property
    def session(self):
        from tidalapi import Config, Session

        if self._session and self._session.check_login():
            return self._session

        # Attempt to reload the existing session from file
        self._session = Session(config=Config(quality=self._quality))
        self._oauth_open_saved_session()
        if not self._session.check_login():
            # Create a new session if we couldn't load an existing one
            self._oauth_create_new_session()

        assert (
            self._session.user and self._session.check_login()
        ), 'Could not connect to TIDAL'

        return self._session

    @property
    def user(self):
        user = self.session.user
        assert user, 'Not logged in'
        return user

    @action
    def create_playlist(self, name: str, description: Optional[str] = None):
        """
        Create a new playlist.

        :param name: Playlist name.
        :param description: Optional playlist description.
        :return: .. schema:: tidal.TidalPlaylistSchema
        """
        ret = self.user.create_playlist(name, description)
        return TidalPlaylistSchema().dump(ret)

    @action
    def delete_playlist(self, playlist_id: str):
        """
        Delete a playlist by ID.

        :param playlist_id: ID of the playlist to delete.
        """
        pl = self.session.playlist(playlist_id)
        pl.delete()

    @action
    def edit_playlist(self, playlist_id: str, title=None, description=None):
        """
        Edit a playlist's metadata.

        :param name: New name.
        :param description: New description.
        """
        pl = self.session.playlist(playlist_id)
        pl.edit(title=title, description=description)

    @action
    def get_playlists(self):
        """
        Get the user's playlists (track lists are excluded).

        :return: .. schema:: tidal.TidalPlaylistSchema(many=True)
        """
        ret = self.user.playlists() + self.user.favorites.playlists()
        return TidalPlaylistSchema().dump(ret, many=True)

    @action
    def get_playlist(self, playlist_id: str):
        """
        Get the details of a playlist (including tracks).

        :param playlist_id: Playlist ID.
        :return: .. schema:: tidal.TidalPlaylistSchema
        """
        pl = self.session.playlist(playlist_id)
        pl._tracks = get_items(pl.tracks)
        return TidalPlaylistSchema().dump(pl)

    @action
    def get_artist(self, artist_id: Union[str, int]):
        """
        Get the details of an artist.

        :param artist_id: Artist ID.
        :return: .. schema:: tidal.TidalArtistSchema
        """
        ret = self.session.artist(artist_id)
        ret.albums = get_items(ret.get_albums)
        return TidalArtistSchema().dump(ret)

    @action
    def get_album(self, album_id: Union[str, int]):
        """
        Get the details of an album.

        :param artist_id: Album ID.
        :return: .. schema:: tidal.TidalAlbumSchema
        """
        ret = self.session.album(album_id)
        return TidalAlbumSchema(with_tracks=True).dump(ret)

    @action
    def get_track(self, track_id: Union[str, int]):
        """
        Get the details of an track.

        :param artist_id: Track ID.
        :return: .. schema:: tidal.TidalTrackSchema
        """
        ret = self.session.album(track_id)
        return TidalTrackSchema().dump(ret)

    @action
    def search(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        type: Optional[str] = None,
    ):
        """
        Perform a search.

        :param query: Query string.
        :param limit: Maximum results that should be returned (default: 50).
        :param offset: Search offset (default: 0).
        :param type: Type of results that should be returned. Default: None
            (return all the results that match the query). Supported:
            ``artist``, ``album``, ``track`` and ``playlist``.
        :return: .. schema:: tidal.TidalSearchResultsSchema
        """
        from tidalapi.artist import Artist
        from tidalapi.album import Album
        from tidalapi.media import Track
        from tidalapi.playlist import Playlist

        models = None
        if type is not None:
            if type == 'artist':
                models = [Artist]
            elif type == 'album':
                models = [Album]
            elif type == 'track':
                models = [Track]
            elif type == 'playlist':
                models = [Playlist]
            else:
                raise AssertionError(f'Unsupported search type: {type}')

        ret = self.session.search(query, models=models, limit=limit, offset=offset)

        return TidalSearchResultsSchema().dump(ret)

    @action
    def get_download_url(self, track_id: str) -> str:
        """
        Get the direct download URL of a track.

        :param artist_id: Track ID.
        """
        return self.session.track(track_id).get_url()

    @action
    def add_to_playlist(self, playlist_id: str, track_ids: Iterable[Union[str, int]]):
        """
        Append one or more tracks to a playlist.

        :param playlist_id: Target playlist ID.
        :param track_ids: List of track IDs to append.
        """
        pl = self.session.playlist(playlist_id)
        pl.add(track_ids)

    @action
    def remove_from_playlist(
        self,
        playlist_id: str,
        track_id: Optional[Union[str, int]] = None,
        index: Optional[int] = None,
    ):
        """
        Remove a track from a playlist.

        Specify either the ``track_id`` or the ``index``.

        :param playlist_id: Target playlist ID.
        :param track_id: ID of the track to remove.
        :param index: Index of the track to remove.
        """
        assert not (
            track_id is None and index is None
        ), 'Please specify either track_id or index'

        pl = self.session.playlist(playlist_id)
        if index:
            pl.remove_by_index(index)
        if track_id:
            pl.remove_by_id(track_id)

    @action
    def add_track(self, track_id: Union[str, int]):
        """
        Add a track to the user's collection.

        :param track_id: Track ID.
        """
        self.user.favorites.add_track(track_id)

    @action
    def add_album(self, album_id: Union[str, int]):
        """
        Add an album to the user's collection.

        :param album_id: Album ID.
        """
        self.user.favorites.add_album(album_id)

    @action
    def add_artist(self, artist_id: Union[str, int]):
        """
        Add an artist to the user's collection.

        :param artist_id: Artist ID.
        """
        self.user.favorites.add_artist(artist_id)

    @action
    def add_playlist(self, playlist_id: str):
        """
        Add a playlist to the user's collection.

        :param playlist_id: Playlist ID.
        """
        self.user.favorites.add_playlist(playlist_id)

    @action
    def remove_track(self, track_id: Union[str, int]):
        """
        Remove a track from the user's collection.

        :param track_id: Track ID.
        """
        self.user.favorites.remove_track(track_id)

    @action
    def remove_album(self, album_id: Union[str, int]):
        """
        Remove an album from the user's collection.

        :param album_id: Album ID.
        """
        self.user.favorites.remove_album(album_id)

    @action
    def remove_artist(self, artist_id: Union[str, int]):
        """
        Remove an artist from the user's collection.

        :param artist_id: Artist ID.
        """
        self.user.favorites.remove_artist(artist_id)

    @action
    def remove_playlist(self, playlist_id: str):
        """
        Remove a playlist from the user's collection.

        :param playlist_id: Playlist ID.
        """
        self.user.favorites.remove_playlist(playlist_id)

    def main(self):
        while not self.should_stop():
            playlists = self.session.user.playlists()  # type: ignore

            for pl in playlists:
                last_updated_var = Variable(f'TIDAL_PLAYLIST_LAST_UPDATE[{pl.id}]')
                prev_last_updated = last_updated_var.get()
                if prev_last_updated:
                    prev_last_updated = datetime.fromisoformat(prev_last_updated)
                    if pl.last_updated > prev_last_updated:
                        get_bus().post(TidalPlaylistUpdatedEvent(playlist_id=pl.id))

                if not prev_last_updated or pl.last_updated > prev_last_updated:
                    last_updated_var.set(pl.last_updated.isoformat())

            self.wait_stop(self.poll_interval)
