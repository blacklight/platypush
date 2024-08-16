from platypush.context import get_plugin
from platypush.plugins.media._search import MediaSearcher


# pylint: disable=too-few-public-methods
class PlexMediaSearcher(MediaSearcher):
    """
    Plex media searcher.
    """

    def supports(self, type: str) -> bool:
        return type == 'plex'

    def search(self, query: str, *_, **__):
        """
        Performs a Plex search using the configured :class:`platypush.plugins.media.plex.MediaPlexPlugin` instance if
        it is available.
        """

        try:
            plex = get_plugin('media.plex')
        except RuntimeError:
            return []

        assert plex, 'No Plex plugin configured'
        self.logger.info('Searching Plex for "%s"', query)
        results = []

        for result in plex.search(title=query).output:
            results.extend(self._flatten_result(result))

        self.logger.info(
            '%d Plex results found for the search query "%s"', len(results), query
        )
        return results

    @staticmethod
    def _flatten_result(result):
        def parse_part(media, part, episode=None, sub_media=None):
            if 'episodes' in media:
                del media['episodes']

            return {
                **{k: v for k, v in result.items() if k not in ['media', 'type']},
                'media_type': result.get('type'),
                'type': 'plex',
                **{k: v for k, v in media.items() if k not in ['parts']},
                **part,
                'title': (
                    result.get('title', '')
                    + (
                        ' [' + (episode or {}).get('season_episode', '') + ']'
                        if (episode or {}).get('season_episode')
                        else ''
                    )
                    + (
                        ' ' + (sub_media or {}).get('title', '')
                        if (sub_media or {}).get('title')
                        else ''
                    ),
                ),
                'summary': (
                    (episode or {}).get('summary')
                    if (episode or {}).get('summary')
                    else media.get('summary')
                ),
            }

        results = []

        for media in result.get('media', []):
            if 'episodes' in media:
                for episode in media['episodes']:
                    for sub_media in episode.get('media', []):
                        for part in sub_media.get('parts', []):
                            results.append(
                                parse_part(
                                    media=media,
                                    episode=episode,
                                    sub_media=sub_media,
                                    part=part,
                                )
                            )
            else:
                for part in media.get('parts', []):
                    results.append(parse_part(media=media, part=part))

        return results


# vim:sw=4:ts=4:et:
