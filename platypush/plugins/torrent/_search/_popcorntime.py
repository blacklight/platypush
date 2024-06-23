import queue
import threading
from urllib.parse import quote_plus
from typing import Iterable, List, Optional, Union

import requests

from ._base import TorrentSearchProvider
from ._model import TorrentSearchResult


class PopcornTimeSearchProvider(TorrentSearchProvider):
    """
    Torrent search provider that uses the PopcornTime API to search for movies
    and TV shows.
    """

    _http_timeout = 20

    def __init__(
        self,
        api_url: str,
        **kwargs,
    ):
        """
        :param api_url: PopcornTime API base URL.
        """
        super().__init__(**kwargs)
        self.api_url = api_url
        self.torrent_base_urls = {
            'movies': f'{api_url}/movie/{{}}',
            'tv': f'{api_url}/show/{{}}',
        }

    @classmethod
    def provider_name(cls) -> str:
        return 'popcorntime'

    def _search(
        self,
        query: str,
        *args,
        category: Optional[Union[str, Iterable[str]]] = None,
        language: Optional[str] = None,
        **kwargs,
    ) -> List[TorrentSearchResult]:
        """
        Perform a search of video torrents using the PopcornTime API.

        :param query: Query string, video name or partial name
        :param category: Category to search. Supported types: `movies`, `tv`.
            Default: None (search all categories)
        :param language: Language code for the results - example: "en" (default: None, no filter)
        """

        results = []
        if isinstance(category, str):
            category = [category]

        def worker(cat):
            if cat not in self.categories:
                raise RuntimeError(
                    f'Unsupported category {cat}. Supported categories: '
                    f'{list(self.categories.keys())}'
                )

            self.logger.info('Searching %s torrents for "%s"', cat, query)
            results.extend(
                self.categories[cat](self, query, *args, language=language, **kwargs)
            )

        workers = [
            threading.Thread(target=worker, kwargs={'cat': category})
            for category in (category or self.categories.keys())
        ]

        for wrk in workers:
            wrk.start()
        for wrk in workers:
            wrk.join()

        return results

    def _imdb_query(self, query: str, category: str):
        if not query:
            return []

        if category == 'movies':
            imdb_category = 'movie'
        elif category == 'tv':
            imdb_category = 'tvSeries'
        else:
            raise RuntimeError(f'Unsupported category: {category}')

        imdb_url = f'https://v3.sg.media-imdb.com/suggestion/x/{quote_plus(query)}.json?includeVideos=1'
        response = requests.get(imdb_url, timeout=self._http_timeout)
        response.raise_for_status()
        response = response.json()
        assert not response.get('errorMessage'), response['errorMessage']
        return [
            item for item in response.get('d', []) if item.get('qid') == imdb_category
        ]

    def _torrent_search_worker(self, imdb_id: str, category: str, q: queue.Queue):
        base_url = self.torrent_base_urls.get(category)
        assert base_url, f'No such category: {category}'
        try:
            self.logger.debug('Searching torrents for %s', imdb_id)
            response = requests.get(
                base_url.format(imdb_id), timeout=self._http_timeout
            )

            self.logger.debug('Got response for %s: %s', imdb_id, response.text)
            result = response.json()
            q.put(
                result if result.get('code') != 404 and result.get('imdb_id') else None
            )
        except Exception as e:
            q.put(e)

    def _search_torrents(self, query, category):
        imdb_results = self._imdb_query(query, category)
        result_queues = [queue.Queue()] * len(imdb_results)
        workers = [
            threading.Thread(
                target=self._torrent_search_worker,
                kwargs={
                    'imdb_id': imdb_results[i]['id'],
                    'category': category,
                    'q': result_queues[i],
                },
            )
            for i in range(len(imdb_results))
        ]

        results = []
        errors = []

        for worker in workers:
            worker.start()
        for q in result_queues:
            res_ = q.get()
            if isinstance(res_, Exception):
                errors.append(res_)
            else:
                results.append(res_)
        for worker in workers:
            worker.join()

        if errors:
            self.logger.warning('Torrent search errors: %s', [str(e) for e in errors])

        return results

    @classmethod
    def _results_to_movies_response(
        cls, results: List[dict], language: Optional[str] = None
    ):
        return sorted(
            [
                TorrentSearchResult(
                    provider=cls.provider_name(),
                    is_media=True,
                    imdb_id=result.get('imdb_id'),
                    type='movies',
                    title=result.get('title', '[No Title]')
                    + f' [movies][{lang}][{quality}]',
                    file=item.get('file'),
                    duration=int(result.get('runtime') or 0) * 60,
                    year=int(result.get('year') or 0),
                    description=result.get('synopsis'),
                    trailer=result.get('trailer'),
                    genres=result.get('genres', []),
                    image=result.get('images', {}).get('poster'),
                    rating=result.get('rating', {}).get('percentage'),
                    votes=result.get('rating', {}).get('votes'),
                    language=lang,
                    quality=quality,
                    size=item.get('size'),
                    seeds=item.get('seed'),
                    peers=item.get('peer'),
                    url=item.get('url'),
                )
                for result in results
                for (lang, items) in ((result or {}).get('torrents', {}) or {}).items()
                if not language or language == lang
                for (quality, item) in items.items()
                if result
            ],
            key=lambda item: item.seeds,
            reverse=True,
        )

    @classmethod
    def _results_to_tv_response(cls, results: List[dict]):
        return sorted(
            [
                TorrentSearchResult(
                    provider=cls.provider_name(),
                    is_media=True,
                    imdb_id=result.get('imdb_id'),
                    tvdb_id=result.get('tvdb_id'),
                    type='tv',
                    file=item.get('file'),
                    series=result.get('title'),
                    title=(
                        result.get('title', '[No Title]')
                        + f'[S{episode.get("season", 0):02d}E{episode.get("episode", 0):02d}] '
                        + f'{episode.get("title", "[No Title]")} [tv][{quality}]'
                    ),
                    duration=int(result.get('runtime') or 0) * 60,
                    year=int(result.get('year') or 0),
                    description=result.get('synopsis'),
                    overview=episode.get('overview'),
                    season=episode.get('season'),
                    episode=episode.get('episode'),
                    num_seasons=result.get('num_seasons'),
                    country=result.get('country'),
                    network=result.get('network'),
                    series_status=result.get('status'),
                    genres=result.get('genres', []),
                    image=result.get('images', {}).get('fanart'),
                    rating=result.get('rating', {}).get('percentage'),
                    votes=result.get('rating', {}).get('votes'),
                    quality=quality,
                    seeds=item.get('seeds'),
                    peers=item.get('peers'),
                    url=item.get('url'),
                )
                for result in results
                for episode in (result or {}).get('episodes', [])
                for quality, item in (episode.get('torrents', {}) or {}).items()
                if quality != '0'
            ],
            key=lambda item: (  # type: ignore
                '.'.join(
                    [  # type: ignore
                        (item.series or ''),
                        (item.quality or ''),
                        str(item.season or 0).zfill(2),
                        str(item.episode or 0).zfill(2),
                    ]
                )
            ),
        )

    def search_movies(self, query, language=None, **_):
        return self._results_to_movies_response(
            self._search_torrents(query, 'movies'), language=language
        )

    def search_tv(self, query, **_):
        return self._results_to_tv_response(self._search_torrents(query, 'tv'))

    categories = {
        'movies': search_movies,
        'tv': search_tv,
    }


# vim:sw=4:ts=4:et:
