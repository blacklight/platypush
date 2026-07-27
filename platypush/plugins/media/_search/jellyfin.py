from platypush.context import get_plugin
from platypush.plugins.media._search import MediaSearcher


class JellyfinMediaSearcher(MediaSearcher):
    """
    Jellyfin media searcher.
    """

    def supports(self, type: str) -> bool:
        return type == 'jellyfin'

    def search(self, query, *_, limit=None, page_state=None, **__):
        """
        Performs a search on a Jellyfin server using the configured
        :class:`platypush.plugins.media.jellyfin.MediaJellyfinPlugin`
        instance (if configured).
        """

        try:
            media = get_plugin('media.jellyfin')
        except RuntimeError:
            return [], None

        if not media:
            return [], None

        limit = limit or self._default_limit
        offset = (page_state or {}).get('offset', 0)

        self.logger.info('Searching Jellyfin for "%s"', query)
        results = media.search(query=query, limit=limit, offset=offset).output
        self.logger.info(
            '%d Jellyfin results found for the search query "%s"', len(results), query
        )

        next_state = {'offset': offset + limit} if len(results) >= limit else None
        return results, next_state


# vim:sw=4:ts=4:et:
