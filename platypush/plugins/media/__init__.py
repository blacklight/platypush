import enum
import os
import re
import subprocess

import urllib.request
import urllib.parse

from platypush.context import get_plugin
from platypush.plugins import Plugin, action

class PlayerState(enum.Enum):
    STOP  = 'stop'
    PLAY  = 'play'
    PAUSE = 'pause'


class MediaPlugin(Plugin):
    """
    Generic plugin to interact with a media player.
    """

    # Supported audio extensions
    audio_extensions = {
        '3gp', 'aa', 'aac', 'aax', 'act', 'aiff', 'amr', 'ape', 'au',
        'awb', 'dct', 'dss', 'dvf', 'flac', 'gsm', 'iklax', 'ivs',
        'm4a', 'm4b', 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'nmf', 'nsf',
        'ogg,', 'opus', 'ra,', 'raw', 'sln', 'tta', 'vox', 'wav',
        'wma', 'wv', 'webm', '8svx',
    }

    # Supported video extensions
    video_extensions = {
        'webm', 'mkv', 'flv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif',
        'gifv', 'mng', 'avi', 'mts', 'm2ts', 'mov', 'qt', 'wmv', 'yuv',
        'rm', 'rmvb', 'asf', 'amv', 'mp4', 'm4p', 'm4v', 'mpg', 'mp2',
        'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'm4v', 'svi',
        '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a',
        'f4b',
    }

    def __init__(self, player, media_dirs=[], download_dir=None, *args, **kwargs):
        """
        :param player: Name of the player plugin to be used as a backend.
            Example: 'media.mplayer', 'media.vlc' or 'media.omxplayer'.
            The plugin needs to be configured as well if required.
        :type player: str

        :param media_dirs: Directories that will be scanned for media files when
            a search is performed (default: none)
        :type media_dirs: list

        :param download_dir: Directory where external resources/torrents will be
            downloaded (default: none)
        :type download_dir: str
        """

        super().__init__(*args, **kwargs)

        self._player_name = player
        self.media_dirs = set(
            filter(
                lambda _: os.path.isdir(_),
                map(
                    lambda _: os.path.abspath(os.path.expanduser(_)),
                    media_dirs
                )
            )
        )

        if download_dir:
            self.download_dir = os.path.abspath(os.path.expanduser(download_dir))
            if not os.path.isdir(self.download_dir):
                raise RuntimeError('download_dir [{}] is not a valid directory'
                                   .format(self.download_dir))

            self.media_dirs.add(self.download_dir)

        self._videos_queue = []

    def _get_resource(self, resource):
        """
        :param resource: Resource to play/parse. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * YouTube videos (format: ``https://www.youtube.com/watch?v=<id>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
        """

        if resource.startswith('youtube:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            resource = self._get_youtube_content(resource)
        elif resource.startswith('magnet:?'):
            torrents = get_plugin('torrent')
            self.logger.info('Downloading torrent {} to {}'.format(resource,
                                                                   download_dir))

            response = torrents.download(resource, download_dir=self.download_dir)
            resources = [f for f in response.output if self._is_video_file(f)]
            if resources:
                self._videos_queue = sorted(resources)
                resource = self._videos_queue.pop(0)
            else:
                raise RuntimeError('Unable to download torrent {}'.format(resource))

        return resource

    @action
    def play(self, resource, *args, **kwargs):
        return get_plugin(self._player_name).play(resource, *args, **kwargs)

    @action
    def pause(self, *args, **kwargs):
        return get_plugin(self._player_name).pause(*args, **kwargs)

    @action
    def stop(self, *args, **kwargs):
        return get_plugin(self._player_name).stop(*args, **kwargs)

    @action
    def voldown(self, *args, **kwargs):
        return get_plugin(self._player_name).voldown(*args, **kwargs)

    @action
    def volup(self, *args, **kwargs):
        return get_plugin(self._player_name).volup(*args, **kwargs)

    @action
    def back(self, *args, **kwargs):
        return get_plugin(self._player_name).back(*args, **kwargs)

    @action
    def forward(self, *args, **kwargs):
        return get_plugin(self._player_name).forward(*args, **kwargs)

    @action
    def next(self):
        """ Play the next item in the queue """
        if self.player:
            self.player.stop()

        if self._videos_queue:
            video = self._videos_queue.pop(0)
            return self.play(video)

    @action
    def toggle_subtitles(self, *args, **kwargs):
        return get_plugin(self._player_name).toggle_subtitles(*args, **kwargs)

    @action
    def is_playing(self, *args, **kwargs):
        return get_plugin(self._player_name).is_playing(*args, **kwargs)

    @action
    def load(self, resource, *args, **kwargs):
        return get_plugin(self._player_name).load(resource, *args, **kwargs)

    @action
    def mute(self, *args, **kwargs):
        return get_plugin(self._player_name).mute(*args, **kwargs)

    @action
    def seek(self, *args, **kwargs):
        return get_plugin(self._player_name).seek(*args, **kwargs)

    @action
    def set_position(self, *args, **kwargs):
        return get_plugin(self._player_name).set_position(*args, **kwargs)

    @action
    def set_volume(self, volume, *args, **kwargs):
        return get_plugin(self._player_name).set_volume(volume, *args, **kwargs)

    @action
    def search(self, query, types=None, queue_results=False, autoplay=False):
        """
        Perform a video search.

        :param query: Query string, video name or partial name
        :type query: str

        :param types: Video types to search (default: ``["youtube", "file", "torrent"]``)
        :type types: list

        :param queue_results: Append the results to the current playing queue (default: False)
        :type queue_results: bool

        :param autoplay: Play the first result of the search (default: False)
        :type autoplay: bool
        """

        results = []
        if types is None:
            types = { 'youtube', 'file', 'torrent' }

        if 'file' in types:
            file_results = self.file_search(query).output
            results.extend(file_results)

        if 'torrent' in types:
            torrents = get_plugin('torrent')
            torrent_results = torrents.search(query).output
            results.extend(torrent_results)

        if 'youtube' in types:
            yt_results = self.youtube_search(query).output
            results.extend(yt_results)

        if results:
            if queue_results:
                self._videos_queue = [_['url'] for _ in results]
                if autoplay:
                    self.play(self._videos_queue.pop(0))
            elif autoplay:
                self.play(results[0]['url'])

        return results

    @classmethod
    def _is_video_file(cls, filename):
        return filename.lower().split('.') in cls.video_extensions

    @classmethod
    def _is_audio_file(cls, filename):
        return filename.lower().split('.') in cls.audio_extensions

    @action
    def file_search(self, query):
        results = []
        query_tokens = [_.lower() for _ in re.split('\s+', query.strip())]

        for media_dir in self.media_dirs:
            self.logger.info('Scanning {} for "{}"'.format(media_dir, query))
            for path, dirs, files in os.walk(media_dir):
                for f in files:
                    if not self._is_video_file(f) and not self._is_audio_file(f):
                        continue

                    matches_query = True
                    for token in query_tokens:
                        if token not in f.lower():
                            matches_query = False
                            break

                    if not matches_query:
                        continue

                    results.append({
                        'url': 'file://' + path + os.sep + f,
                        'title': f,
                    })

        return results

    @action
    def youtube_search(self, query):
        """
        Performs a YouTube search either using the YouTube API (faster and
        recommended, it requires the :mod:`platypush.plugins.google.youtube`
        plugin to be configured) or parsing the HTML search results (fallback
        slower method)
        """

        self.logger.info('Searching YouTube for "{}"'.format(query))

        try:
            return self._youtube_search_api(query=query)
        except Exception as e:
            self.logger.warning('Unable to load the YouTube plugin, falling ' +
                                'back to HTML parse method: {}'.format(str(e)))

            return self._youtube_search_html_parse(query=query)


    def _youtube_search_api(self, query):
        return [
            {
                'url': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                'title': item.get('snippet', {}).get('title', '<No Title>'),
            }
            for item in get_plugin('google.youtube').search(query=query).output
            if item.get('id', {}).get('kind') == 'youtube#video'
        ]

    def _youtube_search_html_parse(self, query):
        query = urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        results = []

        while html:
            m = re.search('(<a href="(/watch\?v=.+?)".+?yt-uix-tile-link.+?title="(.+?)".+?>)', html)
            if m:
                results.append({
                    'url': 'https://www.youtube.com' + m.group(2),
                    'title': m.group(3)
                })

                html = html.split(m.group(1))[1]
            else:
                html = ''

        self.logger.info('{} YouTube video results for the search query "{}"'
                     .format(len(results), query))

        return results


    @classmethod
    def _get_youtube_content(cls, url):
        m = re.match('youtube:video:(.*)', url)
        if m: url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

        proc = subprocess.Popen(['youtube-dl','-f','best', '-g', url],
                                stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8", "strict")[:-1]


# vim:sw=4:ts=4:et:
