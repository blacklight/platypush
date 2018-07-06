import re
import subprocess

from platypush.context import get_plugin
from platypush.plugins.media import PlayerState

from platypush.plugins import Plugin, action

class MediaCtrlPlugin(Plugin):
    """
    Wrapper plugin to control audio and video media.
    Examples of supported URL types:
        - file:///media/movies/Movie.mp4 [requires omxplayer Python support]
        - youtube:video:poAk9XgK7Cs [requires omxplayer+youtube-dl]
        - magnet:?torrent_magnet [requires torrentcast]
        - spotify:track:track_id [leverages plugins.music.mpd]
    """

    _supported_plugins = {
        'music.mpd', 'video.omxplayer', 'video.torrentcast'
    }

    def __init__(self, torrentcast_port=9090, *args, **kwargs):
        super().__init__()
        self.torrentcast_port = torrentcast_port
        self.url = None
        self.plugin = None

    @classmethod
    def _get_type_and_resource_by_url(cls, url):
        # MPD/Mopidy media (TODO support more mopidy types)
        m = re.search('^https://open.spotify.com/([^?]+)', url)
        if m: url = 'spotify:{}'.format(m.group(1).replace('/', ':'))
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


    def _get_playing_plugin(self):
        if self.plugin:
            status = self.plugin.status()
            if status['state'] == PlayerState.PLAY or state['state'] == PlayerState.PAUSE:
                return self.plugin

        for plugin in self._supported_plugins:
            try:
                player = get_plugin(plugin)
            except:
                try:
                    player = get_plugin(plugin, reload=True)
                except:
                    continue

            status = player.status().output
            if status['state'] == PlayerState.PLAY.value or status['state'] == PlayerState.PAUSE.value:
                return player

        return None


    @action
    def play(self, url):
        (type, resource) = self._get_type_and_resource_by_url(url)
        plugin_name = None

        if type == 'mpd':
            plugin_name = 'music.mpd'
        elif type == 'youtube:video' or type == 'file':
            plugin_name = 'video.omxplayer'
        elif type == 'torrent':
            plugin_name = 'video.torrentcast'

        if not plugin_name:
            raise RuntimeError("Unsupported type '{}'".format(type))

        try:
            self.plugin = get_plugin(plugin_name)
        except:
            self.plugin = get_plugin(plugin_name, reload=True)

        self.url = resource
        return self.plugin.play(resource)

    @action
    def pause(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.pause()


    @action
    def stop(self):
        plugin = self._get_playing_plugin()
        if plugin:
            ret = plugin.stop()
            self.plugin = None
            return ret


    @action
    def voldown(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.voldown()


    @action
    def volup(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.volup()


    @action
    def back(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.back()


    @action
    def forward(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.forward()


    @action
    def next(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.next()


    @action
    def previous(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.previous()


    @action
    def status(self):
        plugin = self._get_playing_plugin()
        if plugin: return plugin.status()


# vim:sw=4:ts=4:et:

