import json
import logging
import os
import re
import subprocess
import time

import urllib.request
import urllib.parse

from bs4 import BeautifulSoup
from dbus.exceptions import DBusException
from omxplayer import OMXPlayer

from platypush.context import get_bus
from platypush.plugins.media import PlayerState
from platypush.message.response import Response
from platypush.message.event.video import VideoPlayEvent, VideoPauseEvent, \
    VideoStopEvent, NewPlayingVideoEvent

from .. import Plugin

class VideoOmxplayerPlugin(Plugin):
    video_extensions = {
        '.avi', '.flv', '.wmv', '.mov', '.mp4', '.m4v', '.mpg', '.mpeg',
        '.rm', '.swf', '.vob'
    }

    default_torrent_ports = [6881, 6891]
    torrent_state = {}

    def __init__(self, args=[], media_dirs=[], download_dir=None, torrent_ports=[], *argv, **kwargs):
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
        self.torrent_ports = torrent_ports if torrent_ports else self.default_torrent_ports

    def play(self, resource):
        if resource.startswith('youtube:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            resource = self._get_youtube_content(resource)
        elif resource.startswith('magnet:?'):
            response = self.download_torrent(resource)
            resources = response.output
            if resources:
                self.videos_queue = resources
                resource = self.videos_queue.pop(0)
            else:
                error = 'Unable to download torrent {}'.format(resource)
                logging.warning(error)
                return Response(errors=[error])

        logging.info('Playing {}'.format(resource))

        if self.player:
            try:
                self.player.stop()
                self.player = None
            except Exception as e:
                logging.exception(e)
                logging.warning('Unable to stop a previously running instance ' +
                                'of OMXPlayer, trying to play anyway')

        try:
            self.player = OMXPlayer(resource, args=self.args)
            self._init_player_handlers()
        except DBusException as e:
            logging.warning('DBus connection failed: you will probably not ' +
                            'be able to control the media')
            logging.exception(e)

        return self.status()

    def pause(self):
        if self.player: self.player.play_pause()

    def stop(self):
        if self.player:
            self.player.stop()
            self.player.quit()
            self.player = None

        return self.status()

    def voldown(self):
        if self.player:
            self.player.set_volume(max(-6000, self.player.volume()-1000))
        return self.status()

    def volup(self):
        if self.player:
            self.player.set_volume(min(0, self.player.volume()+1000))
        return self.status()

    def back(self):
        if self.player:
            self.player.seek(-30)
        return self.status()

    def forward(self):
        if self.player:
            self.player.seek(+30)
        return self.status()

    def next(self):
        if self.player:
            self.player.stop()

        if self.videos_queue:
            video = self.videos_queue.pop(0)
            return self.play(video)

        return Response(output={'status': 'no media'}, errors = [])


    def hide_subtitles(self):
        if self.player: self.player.hide_subtitles()
        return self.status()

    def hide_video(self):
        if self.player: self.player.hide_video()
        return self.status()

    def is_playing(self):
        if self.player: return self.player.is_playing()
        else: return False

    def load(self, source, pause=False):
        if self.player: self.player.load(source, pause)
        return self.status()

    def metadata(self):
        if self.player: return Response(output=self.player.metadata())
        return self.status()

    def mute(self):
        if self.player: self.player.mute()
        return self.status()

    def unmute(self):
        if self.player: self.player.unmute()
        return self.status()

    def seek(self, relative_position):
        if self.player: self.player.seek(relative_position)
        return self.status()

    def set_position(self, position):
        if self.player: self.player.set_seek(position)
        return self.status()

    def set_volume(self, volume):
        # Transform a [0,100] value to an OMXPlayer volume in [-6000,0]
        volume = 60.0*volume - 6000
        if self.player: self.player.set_volume(volume)
        return self.status()

    def status(self):
        state = PlayerState.STOP.value

        if self.player:
            state = self.player.playback_status().lower()
            if state == 'playing': state = PlayerState.PLAY.value
            elif state == 'stopped': state = PlayerState.STOP.value
            elif state == 'paused': state = PlayerState.PAUSE.value

            return Response(output=json.dumps({
                'source': self.player.get_source(),
                'state': state,
                'volume': self.player.volume(),
                'elapsed': self.player.position(),
                'duration': self.player.duration(),
                'width': self.player.width(),
                'height': self.player.height(),
            }))
        else:
            return Response(output=json.dumps({
                'state': PlayerState.STOP.value
            }))

    def on_play(self):
        def _f(player):
            get_bus().post(VideoPlayEvent(video=self.player.get_source()))
        return _f

    def on_pause(self):
        def _f(player):
            get_bus().post(VideoPauseEvent(video=self.player.get_source()))
        return _f

    def on_stop(self):
        def _f(player):
            get_bus().post(VideoStopEvent())
        return _f


    def _init_player_handlers(self):
        if not self.player:
            return

        self.player.playEvent += self.on_play()
        self.player.pauseEvent += self.on_pause()
        self.player.stopEvent += self.on_stop()

    def search(self, query, types=None, queue_results=False, autoplay=False):
        results = []
        if types is None:
            types = { 'youtube', 'file', 'torrent' }

        if 'file' in types:
            file_results = self.file_search(query).output
            results.extend(file_results)

        if 'torrent' in types:
            torrent_results = self.torrent_search(query).output
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

        return Response(output=results)

    @classmethod
    def _is_video_file(cls, filename):
        is_video = False
        for ext in cls.video_extensions:
            if filename.lower().endswith(ext):
                is_video = True
                break

        return is_video

    def file_search(self, query):
        results = []
        query_tokens = [_.lower() for _ in re.split('\s+', query.strip())]

        for media_dir in self.media_dirs:
            logging.info('Scanning {} for "{}"'.format(media_dir, query))
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

        return Response(output=results)

    def youtube_search(self, query):
        logging.info('Searching YouTube for "{}"'.format(query))

        query = urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'lxml')
        results = []

        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            m = re.match('(/watch\?v=[^&]+)', vid['href'])
            if m:
                results.append({
                    'url': 'https://www.youtube.com' + m.group(1),
                    'title': vid['title'],
                })

        logging.info('{} YouTube video results for the search query "{}"'
                     .format(len(results), query))

        return Response(output=results)


    @classmethod
    def _get_youtube_content(cls, url):
        m = re.match('youtube:video:(.*)', url)
        if m: url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

        proc = subprocess.Popen(['youtube-dl','-f','best', '-g', url],
                                stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8", "strict")[:-1]

    def torrent_search(self, query):
        logging.info('Searching matching movie torrents for "{}"'.format(query))
        request = urllib.request.urlopen(urllib.request.Request(
            'https://api.apidomain.info/list?' + urllib.parse.urlencode({
                'sort': 'relevance',
                'quality': '720p,1080p,3d',
                'page': 1,
                'keywords': query,
            }),
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
                    '(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            })
        )

        results = [
            {
                'url': _['items'][0]['torrent_magnet'],
                'title': _['title'],
            }

            for _ in json.loads(request.read())['MovieList']
        ]

        return Response(output=results)

    def download_torrent(self, magnet):
        import libtorrent as lt

        if not self.download_dir:
            raise RuntimeError('No download_dir specified in video.omxplayer configuration')

        ses = lt.session()
        ses.listen_on(*self.torrent_ports)

        info = lt.parse_magnet_uri(magnet)
        logging.info('Downloading "{}" to "{}" from [{}]'
                     .format(info['name'], self.download_dir, magnet))

        params = {
            'save_path': self.download_dir,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        }

        transfer = lt.add_magnet_uri(ses, magnet, params)
        status = transfer.status()
        files = []

        self.torrent_state = {
            'url': magnet,
            'title': info['name'],
        }

        while (not status.is_seeding):
            status = transfer.status()
            torrent_file = transfer.torrent_file()
            if torrent_file:
                files = [os.path.join(
                            self.download_dir,
                            torrent_file.files().file_path(i))
                    for i in range(0, torrent_file.files().num_files())
                    if self._is_video_file(torrent_file.files().file_name(i))
                ]

            self.torrent_state['progress'] = 100 * status.progress
            self.torrent_state['download_rate'] = status.download_rate
            self.torrent_state['upload_rate'] = status.upload_rate
            self.torrent_state['num_peers'] = status.num_peers
            self.torrent_state['state'] = status.state

            logging.info(('Torrent download: {:.2f}% complete (down: {:.1f} kb/s ' +
                         'up: {:.1f} kB/s peers: {} state: {})')
                         .format(status.progress * 100,
                                 status.download_rate / 1000,
                                 status.upload_rate / 1000,
                                 status.num_peers, status.state))

            time.sleep(5)

        return Response(output=files)


    def get_torrent_state(self):
        return self.torrent_state


# vim:sw=4:ts=4:et:

