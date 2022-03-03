from typing import Iterable, Optional, Type

import requests
from marshmallow import Schema

from platypush.plugins import Plugin, action
from platypush.schemas.media.jellyfin import JellyfinArtistSchema, \
    JellyfinCollectionSchema, JellyfinMovieSchema, JellyfinEpisodeSchema


class MediaJellyfinPlugin(Plugin):
    """
    Plugin to interact with a Jellyfin media server.

    Note: As of February 2022, this plugin also works with Emby
    media server instances. Future back-compatibility if the two
    APIs diverge, however, is not guaranteed.
    """

    # Maximum number of results returned per query action
    _default_limit = 100

    def __init__(self, server: str, api_key: str, username: Optional[str] = None, **kwargs):
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

    def _execute(
        self, method: str, url: str, *args, **kwargs
    ) -> dict:
        url = '/' + url.lstrip('/')
        url = self.server + url

        kwargs['headers'] = {
            **kwargs.get('headers', {}),
            'X-Emby-Authorization': 'MediaBrowser Client="Platypush", Device="Platypush", '
            f'Token="{self._api_key}"'
        }

        rs = getattr(requests, method.lower())(url, *args, **kwargs)
        rs.raise_for_status()

        return rs.json()

    @property
    def _user_id(self) -> str:
        if not self.__user_id:
            try:
                self.__user_id = self._execute('GET', '/Users/Me')['Id']
            except requests.exceptions.HTTPError as e:
                assert e.response.status_code == 400, (
                    f'Could not get the current user: {e}'
                )

                self.__user_id = self._execute('GET', '/Users')[0]['Id']

        return self.__user_id

    def _query(
        self, url: str,
        schema_class: Optional[Type[Schema]] = None,
        query: Optional[str] = None,
        limit: Optional[int] = _default_limit, offset: int = 0,
        parent_id: Optional[str] = None,
        is_played: Optional[bool] = None,
        is_favourite: Optional[bool] = None,
        is_liked: Optional[bool] = None,
        genres: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
        **kwargs
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
            'recursive': True,
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

    def _flatten_series_result(
        self, search_result: dict
    ) -> Iterable[dict]:
        episodes = []
        show_id = search_result['Id']
        seasons = self._execute(
            'get', f'/Shows/{show_id}/Seasons',
            params={
                'userId': self._user_id,
            }
        ).get('Items', [])

        for i, season in enumerate(seasons):
            episodes.extend(
                JellyfinEpisodeSchema().dump([
                    {**episode, 'SeasonIndex': i+1}
                    for episode in self._execute(
                        'get', f'/Shows/{show_id}/Episodes',
                        params={
                            'userId': self._user_id,
                            'seasonId': season['Id'],
                        }
                    ).get('Items', [])
                ], many=True)
            )

        return episodes

    def _serialize_search_results(self, search_results: Iterable[dict]) -> Iterable[dict]:
        serialized_results = []
        for result in search_results:
            if result['Type'] == 'CollectionFolder':
                result = JellyfinCollectionSchema().dump(result)
                result['type'] = 'collection'    # type: ignore
            elif result['Type'] == 'Movie':
                result = JellyfinMovieSchema().dump(result)
                result['type'] = 'movie'         # type: ignore
            elif result['Type'] == 'Movie':
                result = JellyfinMovieSchema().dump(result)
                result['type'] = 'movie'         # type: ignore
            elif result['Type'] == 'Series':
                serialized_results += self._flatten_series_result(result)
                for r in serialized_results:
                    r['type'] = 'episode'

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
            '/Artists', schema_class=JellyfinArtistSchema,
            limit=limit, offset=offset, is_favourite=is_favourite,
            is_played=is_played, is_liked=is_liked, genres=genres,
            query=query, tags=tags, years=years
        )

    @action
    def get_collections(self) -> Iterable[dict]:
        """
        Get the list of collections associated to the user on the server (Movies, Series, Channels etc.)

        :return: .. schema:: media.jellyfin.JellyfinCollectionSchema(many=True)
        """
        return self._query(
            f'/Users/{self._user_id}/Items',
            parent_id=None,
            schema_class=JellyfinCollectionSchema,
            params=dict(recursive=False),
        )

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
            collections = self.get_collections().output   # type: ignore
            matching_collections = [
                c for c in collections
                if c['id'] == collection or c['name'].lower() == collection.lower()
            ]

            if not matching_collections:
                return []  # No matching collections

            if not parent_id:
                parent_id = matching_collections[0]['id']

        results = self._query(
            f'/Users/{self._user_id}/Items',
            limit=limit, offset=offset, is_favourite=is_favourite,
            is_played=is_played, is_liked=is_liked, genres=genres,
            query=query, tags=tags, years=years, parent_id=parent_id,
            params={
                **(
                    {'sortOrder': 'Descending' if sort_desc else 'Ascending'}
                    if sort_desc is not None else {}
                ),
                **(
                    {'hasSubtitles': has_subtitles}
                    if has_subtitles is not None else {}
                ),
                **(
                    {'minCriticRating': minimum_critic_rating}
                    if minimum_critic_rating is not None else {}
                ),
                **(
                    {'minCommunityRating': minimum_community_rating}
                    if minimum_community_rating is not None else {}
                ),
            }
        )

        return self._serialize_search_results(results)

