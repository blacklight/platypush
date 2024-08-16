from platypush.context import get_plugin
from platypush.plugins.media._search import MediaSearcher


class JellyfinMediaSearcher(MediaSearcher):
    """
    Jellyfin media searcher.
    """

    def supports(self, type: str) -> bool:
        return type == 'jellyfin'

    def search(self, query, *_, **__):
        """
        Performs a search on a Jellyfin server using the configured
        :class:`platypush.plugins.media.jellyfin.MediaJellyfinPlugin`
        instance (if configured).
        """

        try:
            media = get_plugin('media.jellyfin')
        except RuntimeError:
            return []

        if not media:
            return []

        self.logger.info('Searching Jellyfin for "%s"', query)
        results = media.search(query=query).output
        self.logger.info(
            '%d Jellyfin results found for the search query "%s"', len(results), query
        )
        return results


# vim:sw=4:ts=4:et:
