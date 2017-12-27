import re
import subprocess

from omxplayer import OMXPlayer

from platypush.context import get_plugin
from platypush.message.response import Response

from .. import Plugin

class MediaCtrlPlugin(Plugin):
    """
    Wrapper plugin to control audio and video media.
    Examples of supported URL types:
        - file:///media/movies/Movie.mp4 [requires omxplayer Python support]
        - youtube:video:poAk9XgK7Cs [requires omxplayer+youtube-dl]
        - magnet:?torrent_magnet [requires torrentcast]
        - spotify:track:track_id [leverages plugins.music.mpd]
    """

    def __init__(self, omxplayer_args=[], torrentcast_port=9090, *args, **kwargs):
        self.omxplayer_args = omxplayer_args
        self.torrentcast_port = torrentcast_port
        self.url = None
        self.plugin = None

    @classmethod
    def _get_type_and_resource_by_url(cls, url):
        # MPD/Mopidy media (TODO support more mopidy types)
        m = re.match('^https://open.spotify.com/([^/]+)/(.*)', url)
        if m: url = 'spotify:{}:{}'.format(m.group(1), m.group(2))
        if url.startswith('spotify:') \
                or url.startswith('tunein:') \
                or url.startswith('soundcloud:'):
            return ('mpd', url)

        # YouTube video
        m = re.match('youtube:video:(.*)', url)
        if m: url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))
        if url.startswith('https://www.youtube.com/watch?v='):
            return ('youtube:video', url)

        # Local media
        if url.startswith('file://'):
            m = re.match('^file://(.*)', url)
            return ('file', m.group(1))

        # URL to a .torrent media or Magnet link
        if url.startswith('magnet:') or url.endswith('.torrent'):
            return ('torrent', url)

        raise RuntimeError('Unknown URL type: {}'.format(url))


    def play(self, url):
        (type, resource) = self._get_type_and_resource_by_url(url)
        response = Response(output='', errors = [])

        if type == 'mpd':
            self.plugin = get_plugin('music.mpd')
        elif type == 'youtube:video' or type == 'file':
            self.plugin = get_plugin('video.omxplayer')
        elif type == 'torrent':
            self.plugin = get_plugin('video.torrentcast')

        self.url = resource
        return self.plugin.play(resource)

    def pause(self):
        if self.plugin: return self.plugin.pause()


    def stop(self):
        if self.plugin: return self.plugin.stop()


    def voldown(self):
        if self.plugin: return self.plugin.voldown()


    def volup(self):
        if self.plugin: return self.plugin.volup()


    def back(self):
        if self.plugin: return self.plugin.back()


    def forward(self):
        if self.plugin: return self.plugin.forward()


# vim:sw=4:ts=4:et:

