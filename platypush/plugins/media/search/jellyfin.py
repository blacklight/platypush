from platypush.context import get_plugin
from platypush.plugins.media.search import MediaSearcher


class JellyfinMediaSearcher(MediaSearcher):
    def search(self, query, **_):
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

        self.logger.info('Searching Jellyfin for "{}"'.format(query))
        results = media.search(query=query).output
        self.logger.info('{} Jellyfin results found for the search query "{}"'.format(len(results), query))
        return results


# vim:sw=4:ts=4:et:
