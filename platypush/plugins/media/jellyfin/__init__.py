from typing import Collection, Iterable, List, Optional, Type

import requests
from marshmallow import Schema

from platypush.plugins import Plugin, action
from platypush.schemas.media.jellyfin import (
    JellyfinAlbumSchema,
    JellyfinArtistSchema,
    JellyfinBookSchema,
    JellyfinCollectionSchema,
    JellyfinEpisodeSchema,
    JellyfinMovieSchema,
    JellyfinPhotoSchema,
    JellyfinPlaylistSchema,
    JellyfinTrackSchema,
    JellyfinVideoSchema,
)


class MediaJellyfinPlugin(Plugin):
    """
    Plugin to interact with a Jellyfin media server.

    Note: As of February 2022, this plugin also works with Emby
    media server instances. Future back-compatibility if the two
    APIs diverge, however, is not guaranteed.

    Note: At the current state, it is advised to use API keys retrieved from the
    frontend rather than the server-generated API keys (open Developer Tools in
    your browser while logged in to Jellyfin, go to the Network tab, select any
    request, and grab the ``Token`` from the ``Authorization`` header).

    This is because of known limitations in the user session management in the
    Jellyfin API - see `this discussion
    <https://github.com/jellyfin/jellyfin/discussions/12868>`_ and `this issue
    <https://github.com/jellyfin/jellyfin/issues/12999>`_.
    """

    # Maximum number of results returned per query action
    _default_limit = 100

    def __init__(
        self, server: str, api_key: str, username: Optional[str] = None, **kwargs
    ):
        """
        :param server: Jellyfin base server URL (including ``http://`` or ``https://``).
        :param api_key: Server API key. You can generate one from
            ``http(s)://your-server/web/index.html#!/apikeys.html``.
        :param username: Customize results for the specified user
            (default: user associated to the API token if it's a user token, or the first created
            user on the platform).
        """
        super().__init__(**kwargs)
        self.server = server.rstrip('/')
        self.username = username
        self._api_key = api_key
        self.__user_id = None

    def _execute(self, method: str, url: str, *args, **kwargs) -> dict:
        url = '/' + url.lstrip('/')
        url = self.server + url

        kwargs['headers'] = {
            **kwargs.get('headers', {}),
            'X-Emby-Authorization': 'MediaBrowser Client="Platypush", Device="Platypush", '
            f'Token="{self._api_key}"',
        }

        rs = getattr(requests, method.lower())(url, *args, **kwargs)

        if rs.status_code >= 400:
            try:
                error = rs.json()
            except Exception:
                error = rs.text

            self.logger.error(
                'Error while executing %s on %s: %s',
                method,
                url,
                error,
            )
            rs.raise_for_status()

        try:
            return rs.json()
        except Exception:
            return rs.text

    @property
    def _user_id(self) -> str:
        if not self.__user_id:
            try:
                self.__user_id = self._execute('GET', '/Users/Me')['Id']
            except requests.exceptions.HTTPError as e:
                assert (
                    e.response.status_code == 400
                ), f'Could not get the current user: {e}'

                self.__user_id = self._execute('GET', '/Users')[0]['Id']

        return self.__user_id

    def _query(
        self,
        url: str,
        schema_class: Optional[Type[Schema]] = None,
        query: Optional[str] = None,
        limit: Optional[int] = _default_limit,
        offset: int = 0,
        parent_id: Optional[str] = None,
        recursive: bool = True,
        is_played: Optional[bool] = None,
        is_favourite: Optional[bool] = None,
        is_liked: Optional[bool] = None,
        genres: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
        **kwargs,
    ) -> Iterable[dict]:
        filters = []
        if is_played is not None:
            filters.append('IsPlayed' if is_played else 'IsUnplayed')
        if is_liked is not None:
            filters.append('Likes' if is_liked else 'Dislikes')

        kwargs['params'] = {
            **({'isFavorite': is_favourite} if is_favourite is not None else {}),
            **({'searchTerm': query} if query else {}),
            **({'limit': limit} if limit else {}),
            'startIndex': offset,
            'includeMedia': True,
            'includeOverview': True,
            'recursive': recursive,
            **({'parentId': parent_id} if parent_id else {}),
            **({'genres': '|'.join(genres)} if genres else {}),
            **({'tags': '|'.join(tags)} if tags else {}),
            **({'years': ','.join(map(str, years))} if years else {}),
            **kwargs.get('params', {}),
        }

        results = self._execute(method='get', url=url, **kwargs).get('Items', [])
        if schema_class:
            results = schema_class().dump(results, many=True)

        return results

    def _flatten_series_result(self, search_result: dict) -> Iterable[dict]:
        episodes = []
        show_id = search_result['Id']
        seasons = self._execute(
            'get',
            f'/Shows/{show_id}/Seasons',
            params={
                'userId': self._user_id,
            },
        ).get('Items', [])

        for i, season in enumerate(seasons):
            episodes.extend(
                JellyfinEpisodeSchema().dump(
                    [
                        {**episode, 'SeasonIndex': i + 1}
                        for episode in self._execute(
                            'get',
                            f'/Shows/{show_id}/Episodes',
                            params={
                                'userId': self._user_id,
                                'seasonId': season['Id'],
                            },
                        ).get('Items', [])
                    ],
                    many=True,
                )
            )

        return episodes

    def _serialize_search_results(self, search_results: Iterable[dict]) -> List[dict]:
        serialized_results = []
        for result in search_results:
            if result['Type'] == 'Movie':
                result = JellyfinMovieSchema().dump(result)
            elif result['Type'] == 'Video':
                result = JellyfinVideoSchema().dump(result)
            elif result['Type'] == 'Photo':
                result = JellyfinPhotoSchema().dump(result)
            elif result['Type'] == 'Book':
                result = JellyfinBookSchema().dump(result)
            elif result['Type'] == 'Episode':
                result = JellyfinEpisodeSchema().dump(result)
            elif result['Type'] == 'Audio':
                result = JellyfinTrackSchema().dump(result)
            elif result['Type'] == 'Playlist':
                result = JellyfinPlaylistSchema().dump(result)
            elif result['Type'] == 'MusicArtist':
                result = JellyfinArtistSchema().dump(result)
            elif result['Type'] == 'MusicAlbum':
                result = JellyfinAlbumSchema().dump(result)
            elif result['Type'] == 'Series':
                serialized_results += self._flatten_series_result(result)
                for r in serialized_results:
                    r['type'] = 'episode'
            elif result.get('IsFolder'):
                result = JellyfinCollectionSchema().dump(result)

            if isinstance(result, dict) and result.get('type'):
                serialized_results.append(result)

        return serialized_results

    @action
    def get_artists(
        self,
        limit: Optional[int] = _default_limit,
        offset: int = 0,
        query: Optional[str] = None,
        is_played: Optional[bool] = None,
        is_favourite: Optional[bool] = None,
        is_liked: Optional[bool] = None,
        genres: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
    ) -> Iterable[dict]:
        """
        Get a list of artists on the server.

        :param limit: Maximum number of items to return (default: 100).
        :param offset: Return results starting from this (0-based) index (default: 0).
        :param query: Filter items by this term.
        :param is_played: Return only played items (or unplayed if set to False).
        :param is_liked: Return only liked items (or not liked if set to False).
        :param is_favourite: Return only favourite items (or not favourite if set to False).
        :param genres: Filter results by (a list of) genres.
        :param tags: Filter results by (a list of) tags.
        :param years: Filter results by (a list of) years.
        :return: .. schema:: media.jellyfin.JellyfinArtistSchema(many=True)
        """
        return self._query(
            '/Artists',
            schema_class=JellyfinArtistSchema,
            limit=limit,
            offset=offset,
            is_favourite=is_favourite,
            is_played=is_played,
            is_liked=is_liked,
            genres=genres,
            query=query,
            tags=tags,
            years=years,
        )

    @action
    def get_collections(
        self, parent_id: Optional[str] = None, recursive: bool = False
    ) -> Iterable[dict]:
        """
        Get the list of collections associated to the user on the server (Movies, Series, Channels etc.)

        :param parent_id: Filter collections under the specified parent ID.
        :param recursive: If true, return all the collections recursively under the parent.
        :return: .. schema:: media.jellyfin.JellyfinCollectionSchema(many=True)
        """
        return self._query(
            f'/Users/{self._user_id}/Items',
            parent_id=parent_id,
            schema_class=JellyfinCollectionSchema,
            recursive=recursive,
        )

    @action
    def get_playlists(self) -> Iterable[dict]:
        """
        Get the list of playlists associated to the user on the server.

        :return: .. schema:: media.jellyfin.JellyfinPlaylistSchema(many=True)
        """
        return self._query(
            '/Items',
            schema_class=JellyfinPlaylistSchema,
            recursive=True,
            params={
                'userId': self._user_id,
                'includeItemTypes': 'Playlist',
                'sortBy': 'SortName',
            },
        )

    @action
    def get_items(
        self,
        parent_id: str,
        recursive: bool = False,
        limit: Optional[int] = _default_limit,
    ) -> Iterable[dict]:
        """
        Get all the items under the specified parent ID.

        :param parent_id: ID of the parent item.
        :param recursive: If true, return all the items recursively under the parent.
        :param limit: Maximum number of items to return (default: 100).
        """
        return self._serialize_search_results(
            self._query(
                f'/Users/{self._user_id}/Items',
                parent_id=parent_id,
                limit=limit,
                recursive=recursive,
            )
        )

    @action
    def get_playlist_items(
        self,
        playlist_id: str,
        limit: Optional[int] = 10000,
    ) -> Iterable[dict]:
        """
        Get the items in a playlist.

        :param playlist_id: ID of the playlist.
        :param limit: Maximum number of items to return (default: 10000).
        """
        return self._serialize_search_results(
            self._query(
                f'/Playlists/{playlist_id}/Items',
                limit=limit,
                params={'UserId': self._user_id},
            )
        )

    @action
    def info(self, item_id: str) -> dict:
        """
        Get the metadata for a specific item.

        :param parent_id: ID of the parent item.
        """
        ret = self._serialize_search_results(
            [self._execute('get', f'/Users/{self._user_id}/Items/{item_id}')]
        )

        if not ret:
            return {}

        return ret[0]

    @action
    def search(
        self,
        limit: Optional[int] = _default_limit,
        offset: int = 0,
        sort_desc: Optional[bool] = None,
        query: Optional[str] = None,
        collection: Optional[str] = None,
        parent_id: Optional[str] = None,
        has_subtitles: Optional[bool] = None,
        minimum_community_rating: Optional[int] = None,
        minimum_critic_rating: Optional[int] = None,
        is_played: Optional[bool] = None,
        is_favourite: Optional[bool] = None,
        is_liked: Optional[bool] = None,
        genres: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
    ) -> Iterable[dict]:
        """
        Perform a search on the server.

        :param limit: Maximum number of items to return (default: 100).
        :param offset: Return results starting from this (0-based) index (default: 0).
        :param sort_desc: Return results in descending order if true, ascending if false.
        :param query: Filter items by this term.
        :param collection: ID/name of the collection to search (Movies, TV, Channels etc.)
        :param parent_id: Filter items under the specified parent ID.
        :param has_subtitles: Filter items with/without subtitles.
        :param minimum_community_rating: Filter by minimum community rating.
        :param minimum_critic_rating: Filter by minimum critic rating.
        :param is_played: Return only played items (or unplayed if set to False).
        :param is_liked: Return only liked items (or not liked if set to False).
        :param is_favourite: Return only favourite items (or not favourite if set to False).
        :param genres: Filter results by (a list of) genres.
        :param tags: Filter results by (a list of) tags.
        :param years: Filter results by (a list of) years.
        :return: The list of matching results.

        Schema for artists:
            .. schema:: media.jellyfin.JellyfinArtistSchema

        Schema for collections:
            .. schema:: media.jellyfin.JellyfinCollectionSchema

        Schema for movies:
            .. schema:: media.jellyfin.JellyfinMovieSchema

        Schema for episodes:
            .. schema:: media.jellyfin.JellyfinEpisodeSchema

        """
        if collection:
            collections: List[dict] = self.get_collections().output  # type: ignore
            matching_collections = [
                c
                for c in collections
                if c['id'] == collection or c['name'].lower() == collection.lower()
            ]

            if not parent_id:
                parent_id = (
                    matching_collections[0]['id'] if matching_collections else None
                )

        results = self._query(
            f'/Users/{self._user_id}/Items',
            limit=limit,
            offset=offset,
            is_favourite=is_favourite,
            is_played=is_played,
            is_liked=is_liked,
            genres=genres,
            query=query,
            tags=tags,
            years=years,
            parent_id=parent_id,
            params={
                **(
                    {'sortOrder': 'Descending' if sort_desc else 'Ascending'}
                    if sort_desc is not None
                    else {}
                ),
                **(
                    {'hasSubtitles': has_subtitles} if has_subtitles is not None else {}
                ),
                **(
                    {'minCriticRating': minimum_critic_rating}
                    if minimum_critic_rating is not None
                    else {}
                ),
                **(
                    {'minCommunityRating': minimum_community_rating}
                    if minimum_community_rating is not None
                    else {}
                ),
            },
        )

        return self._serialize_search_results(results)

    @action
    def create_playlist(
        self, name: str, public: bool = True, item_ids: Optional[Collection[str]] = None
    ) -> dict:
        """
        Create a new playlist.

        :param name: Name of the playlist.
        :param public: Whether the playlist should be visible to any logged-in user.
        :param item_ids: List of item IDs to add to the playlist.
        """
        playlist = self._execute(
            'POST',
            '/Playlists',
            json={
                'Name': name,
                'UserId': self._user_id,
                'IsPublic': public,
                'Items': item_ids or [],
            },
        )

        return dict(
            JellyfinPlaylistSchema().dump(
                {
                    'Name': name,
                    'IsPublic': public,
                    **playlist,
                }
            )
        )

    @action
    def delete_item(self, item_id: str) -> dict:
        """
        Delete an item from the server.

        :param item_id: ID of the item to delete.
        """
        return self._execute('DELETE', f'/Items/{item_id}')

    @action
    def add_to_playlist(self, playlist_id: str, item_ids: Collection[str]) -> dict:
        """
        Add items to a playlist.

        :param playlist_id: ID of the playlist.
        :param item_ids: List of item IDs to add to the playlist.
        """
        return self._execute(
            'POST',
            f'/Playlists/{playlist_id}/Items',
            params={'ids': ','.join(item_ids)},
        )

    @action
    def remove_from_playlist(self, playlist_id: str, item_ids: Collection[str]) -> dict:
        """
        Remove items from a playlist.

        :param playlist_id: ID of the playlist.
        :param item_ids: List of item IDs to remove from the playlist. **Note**: These
            are the ``playlist_item_id`` on the response of :meth:`.get_playlist_items`,
            not the ``id``.
        """
        return self._execute(
            'DELETE',
            f'/Playlists/{playlist_id}/Items',
            params={'EntryIds': ','.join(item_ids)},
        )

    @action
    def playlist_move(
        self,
        playlist_id: str,
        *_,
        from_pos: Optional[int] = None,
        to_pos: int,
        item_id: Optional[str] = None,
        **__,
    ):
        """
        Move items in a playlist.

        Either ``from_pos`` or ``item`` must be specified.

        :param playlist_id: ID of the playlist.
        :param from_pos: Starting position of the item to move (0-based).
        :param to_pos: New position of the item (0-based).
        :param item_id: Playlist ID of the item to move, as returned
            by :meth:`.get_playlist_items`. **Note**: This is the
            ``playlist_item_id`` on the response, not the ``id``.
        """
        assert (
            from_pos is not None or item_id is not None
        ), 'Either from_pos or item must be set'
        assert (
            from_pos is None or item_id is None
        ), 'Either from_pos or item must be set'
        assert to_pos >= 0, 'to_pos must be >= 0'

        if from_pos is not None:
            assert from_pos >= 0, 'from_pos must be >= 0'
            if from_pos == to_pos:
                self.logger.info(
                    'from_pos and to_pos are the same, no need to move the item'
                )
                return

            items = self._execute(
                'GET',
                f'/Playlists/{playlist_id}/Items',
                params={
                    'userId': self._user_id,
                    'limit': 25000,
                },
            ).get('Items', [])

            if len(items) <= from_pos:
                self.logger.warning(
                    'Invalid from_pos %d, playlist has only %d items',
                    from_pos,
                    len(items),
                )
                return

            item_id = items[from_pos]['PlaylistItemId']

        self._execute(
            'POST',
            f'/Playlists/{playlist_id}/Items/{item_id}/Move/{to_pos}',
        )
