import datetime
import os
import select
import subprocess
import tempfile
import threading
import time

from platypush.config import Config
from platypush.context import get_bus, get_plugin
from platypush.message.response import Response
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.torrent import TorrentDownloadStartEvent, \
    TorrentDownloadCompletedEvent

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
        * A media plugin configured for streaming (e.g. media.mplayer
            or media.omxplayer)
    """

    _supported_media_plugins = { 'media.mplayer', 'media.omxplayer' }

    # Download at least 10 MBs before starting streaming
    _download_size_before_streaming = 10 * 2**20

    def __init__(self, webtorrent_bin=None, *args, **kwargs):
        """
        media.webtorrent will use the default media player plugin you have
        configured (e.g. mplayer, omxplayer) to stream the torrent.

        :param webtorrent_bin: Path to your webtorrent executable. If not set,
            then Platypush will search for the right executable in your PATH
        :type webtorrent_bin: str
        """

        super().__init__(*args, **kwargs)

        self._init_webtorrent_bin(webtorrent_bin=webtorrent_bin)
        self._init_media_player()


    def _init_webtorrent_bin(self, webtorrent_bin=None):
        self._webtorrent_process = None

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

    def _init_media_player(self):
        self._media_plugin = None
        plugin_name = None

        for plugin_name in self._supported_media_plugins:
            try:
                if Config.get(plugin_name):
                    self._media_plugin = get_plugin(plugin_name)
                    break
            except:
                pass

        if not self._media_plugin:
            raise RuntimeError(('No media player specified and no ' +
                                'compatible media plugin configured - ' +
                                'supported media plugins: {}').format(
                                    self._supported_media_plugins))


    def _process_monitor(self, resource, output_file):
        def _thread():
            if not self._webtorrent_process:
                return

            bus = get_bus()
            bus.post(TorrentDownloadStartEvent(resource=resource))

            while True:
                try:
                    if os.path.getsize(output_file) > \
                            self._download_size_before_streaming:
                        break
                except FileNotFoundError:
                    pass

            self._media_plugin.play(output_file)
            self._webtorrent_process.wait()
            bus.post(TorrentDownloadCompletedEvent(resource=resource))
            self._webtorrent_process = None

        return _thread


    def _get_torrent_download_path(self):
        if self._media_plugin.download_dir:
            # TODO set proper file name based on the torrent metadata
            return os.path.join(self._media_plugin.download_dir,
                                'torrent_media_' + datetime.datetime.
                                today().strftime('%Y-%m-%d_%H-%M-%S-%f'))
        else:
            return tempfile.NamedTemporaryFile(delete=False).name


    @action
    def play(self, resource):
        """
        Download and stream a torrent

        :param resource: Play a resource, as a magnet link, torrent URL or
            torrent file path
        :type resource: str
        """

        if self._webtorrent_process:
            try:
                self.quit()
            except:
                self.logger.debug('Failed to quit the previous instance: {}'.
                                  format(str))

        output_file = self._get_torrent_download_path()
        webtorrent_args = [self.webtorrent_bin, '--stdout', resource]

        with open(output_file, 'w') as f:
            self._webtorrent_process = subprocess.Popen(webtorrent_args,
                                                        stdout=f)

            threading.Thread(target=self._process_monitor(
                resource=resource, output_file=output_file)).start()

        return { 'resource': resource }


    @action
    def stop(self):
        """ Stop the playback """
        return self.quit()

    @action
    def quit(self):
        """ Quit the player """
        if self._webtorrent_process and self._is_process_alive(
                self._webtorrent_process.pid):
            self._webtorrent_process.terminate()
            self._webtorrent_process.wait()
            try: self._webtorrent_process.kill()
            except: pass
            bus.post(MediaStopEvent())

        self._webtorrent_process = None

    @action
    def load(self, resource):
        """
        Load a torrent resource in the player.
        """
        return self.play(resource)

    def _is_process_alive(self):
        if not self._webtorrent_process:
            return False

        try:
            os.kill(self._webtorrent_process.pid, 0)
            return True
        except OSError:
            self._webtorrent_process = None
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

        return {'state': self._media_plugin.status()
                .get('state', PlayerState.STOP.value)}


# vim:sw=4:ts=4:et:
