import json
import os
import re
import subprocess
import time

import urllib.request
import urllib.parse

from platypush.context import get_backend, get_plugin
from platypush.plugins.media import PlayerState
from platypush.message.event.video import VideoPlayEvent, VideoPauseEvent, \
    VideoStopEvent, NewPlayingVideoEvent

from platypush.plugins import Plugin, action


class VideoOmxplayerPlugin(Plugin):
    """
    Plugin to control video and media playback on your Raspberry Pi or
    ARM-compatible device using OMXPlayer.

    It can play local files, remote URLs, YouTube URLs and it supports torrents
    search, download and play.

    Requires:

        * **omxplayer** installed on your system (see your distro instructions)
        * **omxplayer-wrapper** (``pip install omxplayer-wrapper``)
        * **python-libtorrent** (``pip install python-libtorrent``), optional for Torrent support
        * **youtube-dl** installed on your system (see your distro instructions), optional for YouTube support
    """

    # Supported video extensions
    video_extensions = {
        '.avi', '.flv', '.wmv', '.mov', '.mp4', '.m4v', '.mpg', '.mpeg',
        '.rm', '.swf', '.vob', '.mkv'
    }

    def __init__(self, args=[], media_dirs=[], download_dir=None, *argv, **kwargs):
        """
        :param args: Arguments that will be passed to the OMXPlayer constructor (e.g. subtitles, volume, start position, window size etc.) see https://github.com/popcornmix/omxplayer#synopsis and http://python-omxplayer-wrapper.readthedocs.io/en/latest/omxplayer/#omxplayer.player.OMXPlayer
        :type args: list

        :param media_dirs: Directories that will be scanned for media files when a search is performed (default: none)
        :type media_dirs: list

        :param download_dir: Directory where the videos/torrents will be downloaded (default: none)
        :type download_dir: str
        """

        super().__init__(*argv, **kwargs)

        self.args = args
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

        self.player = None
        self.videos_queue = []

    @action
    def play(self, resource):
        """
        Play a resource.

        :param resource: Resource to play. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * YouTube videos (format: ``https://www.youtube.com/watch?v=<id>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
        """

        from dbus.exceptions import DBusException

        if resource.startswith('youtube:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            resource = self._get_youtube_content(resource)
        elif resource.startswith('magnet:?'):
            torrents = get_plugin('torrent')
            response = torrents.download(resource, download_dir=self.download_dir)
            resources = [f for f in response.output if self._is_video_file(f)]
            if resources:
                self.videos_queue = sorted(resources)
                resource = self.videos_queue.pop(0)
            else:
                raise RuntimeError('Unable to download torrent {}'.format(resource))

        self.logger.info('Playing {}'.format(resource))

        if self.player:
            try:
                self.player.stop()
                self.player = None
            except Exception as e:
                self.logger.exception(e)
                self.logger.warning('Unable to stop a previously running instance ' +
                                'of OMXPlayer, trying to play anyway')

        try:
            from omxplayer import OMXPlayer
            self.player = OMXPlayer(resource, args=self.args)
            self._init_player_handlers()
        except DBusException as e:
            self.logger.warning('DBus connection failed: you will probably not ' +
                            'be able to control the media')
            self.logger.exception(e)

        return self.status()

    @action
    def pause(self):
        """ Pause the playback """
        if self.player: self.player.play_pause()

    @action
    def stop(self):
        """ Stop the playback """
        if self.player:
            self.player.stop()
            self.player.quit()
            self.player = None

        return {'status':'stop'}

    @action
    def voldown(self):
        """ Volume down by 10% """
        if self.player:
            self.player.set_volume(max(-6000, self.player.volume()-1000))
        return self.status()

    @action
    def volup(self):
        """ Volume up by 10% """
        if self.player:
            self.player.set_volume(min(0, self.player.volume()+1000))
        return self.status()

    @action
    def back(self):
        """ Back by 30 seconds """
        if self.player:
            self.player.seek(-30)
        return self.status()

    @action
    def forward(self):
        """ Forward by 30 seconds """
        if self.player:
            self.player.seek(+30)
        return self.status()

    @action
    def next(self):
        """ Play the next track/video """
        if self.player:
            self.player.stop()

        if self.videos_queue:
            video = self.videos_queue.pop(0)
            return self.play(video)

    @action
    def hide_subtitles(self):
        """ Hide the subtitles """
        if self.player: self.player.hide_subtitles()
        return self.status()

    @action
    def hide_video(self):
        """ Hide the video """
        if self.player: self.player.hide_video()
        return self.status()

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """

        if self.player: return self.player.is_playing()
        else: return False

    @action
    def load(self, resource, pause=False):
        """
        Load a resource/video in the player.

        :param pause: If set, load the video in paused mode (default: False)
        :type pause: bool
        """

        if self.player: self.player.load(resource, pause)
        return self.status()

    @action
    def metadata(self):
        """ Get the metadata of the current video """
        if self.player:
            return self.player.metadata()
        return self.status()

    @action
    def mute(self):
        """ Mute the player """
        if self.player: self.player.mute()
        return self.status()

    @action
    def unmute(self):
        """ Unmute the player """
        if self.player: self.player.unmute()
        return self.status()

    @action
    def seek(self, relative_position):
        """
        Seek backward/forward by the specified number of seconds

        :param relative_position: Number of seconds relative to the current cursor
        :type relative_position: int
        """

        if self.player: self.player.seek(relative_position)
        return self.status()

    @action
    def set_position(self, position):
        """
        Seek backward/forward to the specified absolute position

        :param position: Number of seconds from the start
        :type position: int
        """

        if self.player: self.player.set_seek(position)
        return self.status()

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: int
        """

        # Transform a [0,100] value to an OMXPlayer volume in [-6000,0]
        volume = 60.0*volume - 6000
        if self.player: self.player.set_volume(volume)
        return self.status()

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example::

            output = {
                "source": "https://www.youtube.com/watch?v=7L9KkZoNZkA",
                "state": "play",
                "volume": 80,
                "elapsed": 123,
                "duration": 300,
                "width": 800,
                "height": 600
            }
        """

        state = PlayerState.STOP.value

        if self.player:
            state = self.player.playback_status().lower()
            if state == 'playing': state = PlayerState.PLAY.value
            elif state == 'stopped': state = PlayerState.STOP.value
            elif state == 'paused': state = PlayerState.PAUSE.value

            return {
                'source': self.player.get_source(),
                'state': state,
                'volume': self.player.volume(),
                'elapsed': self.player.position(),
                'duration': self.player.duration(),
                'width': self.player.width(),
                'height': self.player.height(),
            }
        else:
            return {
                'state': PlayerState.STOP.value
            }

    @action
    def send_message(self, msg):
        try:
            redis = get_backend('redis')
            if not redis:
                raise KeyError()
        except KeyError:
            self.logger.warning("Backend {} does not implement send_message " +
                                "and the fallback Redis backend isn't configured")
            return

        redis.send_message(msg)

    def on_play(self):
        def _f(player):
            self.send_message(VideoPlayEvent(video=self.player.get_source()))
        return _f

    def on_pause(self):
        def _f(player):
            self.send_message(VideoPauseEvent(video=self.player.get_source()))
        return _f

    def on_stop(self):
        def _f(player):
            self.send_message(VideoStopEvent())
        return _f


    def _init_player_handlers(self):
        if not self.player:
            return

        self.player.playEvent += self.on_play()
        self.player.pauseEvent += self.on_pause()
        self.player.stopEvent += self.on_stop()

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
                self.videos_queue = [_['url'] for _ in results]
                if autoplay:
                    self.play(self.videos_queue.pop(0))
            elif autoplay:
                self.play(results[0]['url'])

        return results

    @classmethod
    def _is_video_file(cls, filename):
        is_video = False
        for ext in cls.video_extensions:
            if filename.lower().endswith(ext):
                is_video = True
                break

        return is_video

    @action
    def file_search(self, query):
        results = []
        query_tokens = [_.lower() for _ in re.split('\s+', query.strip())]

        for media_dir in self.media_dirs:
            self.logger.info('Scanning {} for "{}"'.format(media_dir, query))
            for path, dirs, files in os.walk(media_dir):
                for f in files:
                    if not self._is_video_file(f):
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

