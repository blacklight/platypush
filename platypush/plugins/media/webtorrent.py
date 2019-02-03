import os
import select
import subprocess
import threading
import time

from platypush.context import get_bus, get_plugin
from platypush.message.response import Response
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import MediaPlayEvent, MediaPauseEvent, \
    MediaStopEvent, NewPlayingMediaEvent

from platypush.plugins import action
from platypush.utils import find_bins_in_path


class MediaWebtorrentPlugin(MediaPlugin):
    """
    Plugin to download and stream videos using webtorrent

    Requires:

        * **webtorrent** installed on your system (``npm install -g webtorrent``)
        * **webtorrent-cli** installed on your system
            (``npm install -g webtorrent-cli`` or better
             ``npm install -g BlackLight/webtorrent-cli`` as my fork contains
             the ``--[player]-args`` options to pass custom arguments to your
             installed player)
    """

    _supported_media_plugins = { 'media.mplayer', 'media.omxplayer' }
    _supported_webtorrent_players = {'airplay', 'chromecast', 'mplayer',
                                     'mpv', 'omxplayer', 'vlc', 'xbmc'}


    def __init__(self, player_type=None, player_args=None, webtorrent_bin=None,
                 *args, **kwargs):
        """
        Create the webtorrent wrapper

        :param player_type: Player type to be used for streaming. Check
            https://www.npmjs.com/package/webtorrent for a full list of the
            supported players. If no player is specified then it will search in
            your Platypush configuration for any enabled and supported media
            plugin (either ``media.mplayer`` or ``media.omxplayer``) to
            configure the streaming player. Currently supported options:
                - airplay
                - chromecast
                - mplayer
                - mpv
                - omxlayer
                - vlc
                - xbmc

        :type player_type: str

        :param player_args: Extra arguments to pass to the player as a list.
            For mplayer, vlc, omxplayer and mpv this will be a list of extra
            arguments to be passed to the executable (e.g. fullscreen, volume,
            audio sink etc.).
        :type player_args: list[str]

        :param webtorrent_bin: Path to your webtorrent executable. If not set,
            then Platypush will search for the right executable in your PATH
        :type webtorrent_bin: str
        """

        super().__init__(*args, **kwargs)

        self._init_webtorrent_bin(webtorrent_bin=webtorrent_bin)
        self._init_media_player(player_type=player_type,
                                player_args=player_args or [])


    def _init_webtorrent_bin(self, webtorrent_bin=None):
        if not webtorrent_bin:
            bin_name = 'webtorrent.exe' if os.name == 'nt' else 'webtorrent'
            bins = find_bins_in_path(bin_name)

            if not bins:
                raise RuntimeError('Webtorrent executable not specified and ' +
                                   'not found in your PATH. Make sure that ' +
                                   'webtorrent is either installed or ' +
                                   'configured and that both webtorrent and ' +
                                   'webtorrent-cli are installed')

            self.webtorrent_bin = bins[0]
        else:
            webtorrent_bin = os.path.expanduser(webtorrent_bin)
            if not (os.path.isfile(webtorrent_bin)
                    and (os.name == 'nt' or os.access(webtorrent_bin, os.X_OK))):
                raise RuntimeError('{} is does not exist or is not a valid ' +
                                   'executable file'.format(webtorrent_bin))

            self.webtorrent_bin = webtorrent_bin

    def _init_media_player(self, player_type, player_args):
        if player_type is None:
            media_plugin = None
            plugin_name = None

            for plugin_name in self._supported_media_plugins:
                try:
                    media_plugin = get_plugin(plugin_name)
                    break
                except:
                    pass

            if not media_plugin:
                raise RuntimeError(('No media player specified and no ' +
                                    'compatible media plugin configured - ' +
                                    'supported media plugins: {}').format(
                                        self._supported_media_plugins))

            self.player_type = plugin_name[len('media.'):]
            self.player_args = media_plugin.args
        else:
            if player_type not in self._supported_webtorrent_players:
                raise RuntimeError(('{} is not a supported player (supported ' +
                                    'players: {})').format(
                                        player_type,
                                        self._supported_webtorrent_players))

            self.player_type = player_type
            self.player_args = player_args or []

            if not self.player_args:
                try:
                    plugin = get_plugin('media.' + player_type)
                    self.player_args = plugin.args
                except:
                    pass

        self._player = None


    def _start_webtorrent(self, resource):
        if self._player:
            try:
                self.quit()
            except:
                self.logger.debug('Failed to quit the previous instance: {}'.
                                  format(str))

        webtorrent_args = [self.webtorrent_bin, '--' + self.player_type,
                           resource]

        if self.player_args:
            webtorrent_args += ['--' + self.player_type + "-args='" + \
                repr(' '.join(self.player_args)) + "'"]

        popen_args = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
        }

        if self._env:
            popen_args['env'] = self._env
        else:
            try:
                plugin = get_plugin('media.' + player_type)
                if plugin._env:
                    popen_args['env'] = plugin._env
            except:
                pass

        self._player = subprocess.Popen(webtorrent_args, **popen_args)

    def _process_monitor(self):
        def _thread():
            if not self._player:
                return

            self._player.wait()
            get_bus().post(MediaStopEvent())
            self._player = None

        return _thread

    @action
    def play(self, resource):
        """
        Download and stream a torrent

        :param resource: Play a resource, as a magnet link, torrent URL or
            torrent file path
        :type resource: str
        """

        self._start_webtorrent(resource)
        bus = get_bus()
        bus.post(NewPlayingMediaEvent(resource=resource))
        threading.Thread(target=self._process_monitor()).start()

    @action
    def stop(self):
        """ Stop the playback """
        return self.quit()

    @action
    def quit(self):
        """ Quit the player """
        if self._player and self._is_process_alive(self._player.pid):
            self._player.terminate()
            self._player.wait()
            try: self._player.kill()
            except: pass
            bus.post(MediaStopEvent())

        self._player = None

    @action
    def load(self, resource):
        """
        Load a torrent resource in the player.
        """
        return self.play(resource)

    def _is_process_alive(self):
        if not self._player:
            return False

        try:
            os.kill(self._player.pid, 0)
            return True
        except OSError:
            self._player = None
            return False

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example::

            output = {
                "state": "play"  # or "stop" or "pause"
            }
        """

        return {'state': PlayerState.PLAY.value
                if self._player and self._is_process_alive()
                else PlayerState.STOP.value}


# vim:sw=4:ts=4:et:
