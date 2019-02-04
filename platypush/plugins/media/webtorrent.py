import datetime
import enum
import os
import re
import select
import subprocess
import threading
import time

from platypush.config import Config
from platypush.context import get_bus, get_plugin
from platypush.message.response import Response
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.torrent import TorrentDownloadStartEvent, \
    TorrentDownloadCompletedEvent, TorrentDownloadProgressEvent, \
    TorrentDownloadingMetadataEvent

from platypush.plugins import action
from platypush.utils import find_bins_in_path, find_files_by_ext, \
    is_process_alive


class TorrentState(enum.Enum):
    IDLE = 1
    DOWNLOADING_METADATA = 2
    DOWNLOADING = 3
    DOWNLOADED = 4

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

    def __init__(self, webtorrent_bin=None, webtorrent_port=None, *args,
                 **kwargs):
        """
        media.webtorrent will use the default media player plugin you have
        configured (e.g. mplayer, omxplayer) to stream the torrent.

        :param webtorrent_bin: Path to your webtorrent executable. If not set,
            then Platypush will search for the right executable in your PATH
        :type webtorrent_bin: str

        :param webtorrent_port: Port where the webtorrent will be running
            streaming server will be running (default: 8000)
        :type webtorrent_port: int
        """

        super().__init__(*args, **kwargs)

        self.webtorrent_port = webtorrent_port
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


    def _read_process_line(self):
        line = self._webtorrent_process.stdout.readline().decode().strip()
        # Strip output of the colors
        return re.sub('\x1b\[((\d+m)|(.{1,2}))', '', line).strip()


    def _process_monitor(self, resource, download_dir):
        def _thread():
            if not self._webtorrent_process:
                return

            ######
            state = TorrentState.IDLE
            bus = get_bus()
            webtorrent_url = None
            output_dir = None
            media_file = None

            poll = select.poll()
            poll.register(self._webtorrent_process.stdout, select.POLLIN)

            # First wait for the metadata to be ready and the streaming started
            while True:
                result = poll.poll(0)
                if not result:
                    continue

                if not self._is_process_alive():
                    break

                line = self._read_process_line()

                if 'fetching torrent metadata from' in line.lower() \
                        and state == TorrentState.IDLE:
                    # IDLE -> DOWNLOADING_METADATA
                    state = TorrentState.DOWNLOADING_METADATA
                    bus.post(TorrentDownloadingMetadataEvent(resource=resource))
                elif 'downloading: ' in line.lower() \
                        and media_file is None:
                    # Find video files in torrent directory
                    output_dir = os.path.join(
                        download_dir, re.search(
                            'downloading: (.+?)$', line, flags=re.IGNORECASE
                        ).group(1))

                elif 'server running at: ' in line.lower() \
                        and webtorrent_url is None:
                    # Streaming started
                    webtorrent_url = re.search('server running at: (.+?)$',
                                               line, flags=re.IGNORECASE).group(1)
                    self.logger.info('Torrent stream started on {}'.format(
                        webtorrent_url))

                if output_dir and not media_file:
                    media_files = sorted(find_files_by_ext(
                        output_dir, *self._media_plugin.video_extensions))

                    if media_files:
                        # TODO support for queueing multiple media
                        media_file = os.path.join(output_dir, media_files[0])
                    else:
                        time.sleep(1)  # Wait before the media file is created

                if state.value <= TorrentState.DOWNLOADING_METADATA.value \
                        and media_file and webtorrent_url:
                    # DOWNLOADING_METADATA -> DOWNLOADING
                    state = TorrentState.DOWNLOADING
                    bus.post(TorrentDownloadStartEvent(
                        resource=resource, media_file=media_file,
                        stream_url=webtorrent_url))
                    break


            if not output_dir:
                raise RuntimeError('Could not download torrent')
            if not media_file or not webtorrent_url:
                if not media_file:
                    self.logger.warning(
                        'The torrent does not contain any video files')
                else:
                    self.logger.warning('WebTorrent could not start streaming')

                # Keep downloading but don't start the player
                try: self._webtorrent_process.wait()
                except: pass
                return

            # Then wait until we have enough chunks to start the player
            while True:
                result = poll.poll(0)
                if not result:
                    continue

                if not self._is_process_alive():
                    break

                try:
                    if os.path.getsize(media_file) > \
                            self._download_size_before_streaming:
                        break
                except FileNotFoundError:
                    continue

            self.logger.info(
                'Starting playback of {} to {} through {}'.format(
                    media_file, self._media_plugin.__class__.__name__,
                    webtorrent_url))

            media = media_file if self._media_plugin.is_local() \
                else webtorrent_url

            self._media_plugin.play(media)
            self.logger.info('Waiting for player to terminate')
            self._wait_for_player()
            self.logger.info('Torrent player terminated')
            bus.post(TorrentDownloadCompletedEvent(resource=resource))

            try: self.quit()
            except: pass
            self.logger.info('WebTorrent process terminated')

        return _thread

    def _wait_for_player(self):
        media_cls = self._media_plugin.__class__.__name__
        stop_evt = None

        if media_cls == 'MediaMplayerPlugin':
            stop_evt = self._media_plugin._mplayer_stopped_event
        elif media_cls == 'MediaOmxplayerPlugin':
            stop_evt = threading.Event()
            def stop_callback():
                stop_evt.set()
            self._media_plugin.add_handler('stop', stop_callback)

        if stop_evt:
            stop_evt.wait()
        else:
            # Fallback: wait for the webtorrent process to terminate
            self._webtorrent_process.wait()


    def _get_torrent_download_dir(self):
        if self._media_plugin.download_dir:
            return self._media_plugin.download_dir
        else:
            d = os.path.join(os.environ['HOME'], 'Downloads')
            os.makedirs(d, exist_ok=True)
            return d


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

        download_dir = self._get_torrent_download_dir()
        webtorrent_args = [self.webtorrent_bin, 'download', '-o', download_dir]

        if self.webtorrent_port:
            webtorrent_args += ['-p', self.webtorrent_port]

        webtorrent_args += [resource]
        self._webtorrent_process = subprocess.Popen(webtorrent_args,
                                                    stdout=subprocess.PIPE)

        threading.Thread(target=self._process_monitor(
            resource=resource, download_dir=download_dir)).start()
        return { 'resource': resource }


    @action
    def stop(self):
        """ Stop the playback """
        return self.quit()

    @action
    def quit(self):
        """ Quit the player """
        if self._is_process_alive():
            self._webtorrent_process.terminate()
            self._webtorrent_process.wait()
            try: self._webtorrent_process.kill()
            except: pass

        self._webtorrent_process = None

    @action
    def load(self, resource):
        """
        Load a torrent resource in the player.
        """
        return self.play(resource)

    def _is_process_alive(self):
        return is_process_alive(self._webtorrent_process.pid) \
            if self._webtorrent_process else False

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
