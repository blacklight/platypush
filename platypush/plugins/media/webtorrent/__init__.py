import enum
import os
import re
import select
import subprocess
import threading
import time

from platypush.config import Config
from platypush.context import get_bus, get_plugin
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.torrent import TorrentDownloadStartEvent, \
    TorrentDownloadCompletedEvent, TorrentDownloadedMetadataEvent

from platypush.plugins import action
from platypush.utils import find_bins_in_path, find_files_by_ext, \
    is_process_alive, get_ip_or_hostname


class TorrentState(enum.IntEnum):
    IDLE = 1
    DOWNLOADING_METADATA = 2
    DOWNLOADING = 3
    DOWNLOADED = 4


class MediaWebtorrentPlugin(MediaPlugin):
    """
    Plugin to download and stream videos using webtorrent

    Requires:

        * **webtorrent** installed on your system (``npm install -g webtorrent``)
        * **webtorrent-cli** installed on your system (``npm install -g webtorrent-cli``)
        * A media plugin configured for streaming (e.g. media.mplayer, media.vlc, media.mpv or media.omxplayer)
    """
    _supported_media_plugins = {'media.mplayer', 'media.omxplayer', 'media.mpv',
                                'media.vlc', 'media.webtorrent'}

    # Download at least 15 MBs before starting streaming
    _download_size_before_streaming = 15 * 2**20

    _web_stream_ready_timeout = 120

    def __init__(self, webtorrent_bin=None, webtorrent_port=None, *args,
                 **kwargs):
        """
        media.webtorrent will use the default media player plugin you have
        configured (e.g. mplayer, omxplayer, mpv) to stream the torrent.

        :param webtorrent_bin: Path to your webtorrent executable. If not set,
            then Platypush will search for the right executable in your PATH
        :type webtorrent_bin: str

        :param webtorrent_port: Port where the webtorrent will be running
            streaming server will be running (default: 8000)
        :type webtorrent_port: int
        """

        super().__init__(*args, **kwargs)

        self.webtorrent_port = webtorrent_port
        self._webtorrent_process = None
        self._init_webtorrent_bin(webtorrent_bin=webtorrent_bin)
        self._init_media_player()
        self._download_started_event = threading.Event()
        self._torrent_stream_urls = {}

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

    def _init_media_player(self):
        self._media_plugin = None

        for plugin_name in self._supported_media_plugins:
            try:
                if Config.get(plugin_name):
                    self._media_plugin = get_plugin(plugin_name)
                    break
            except Exception as e:
                self.logger.debug(f'Could not get media plugin {plugin_name}: {str(e)}')

        if not self._media_plugin:
            raise RuntimeError(('No media player specified and no ' +
                                'compatible media plugin configured - ' +
                                'supported media plugins: {}').format(
                                    self._supported_media_plugins))

    def _read_process_line(self):
        line = self._webtorrent_process.stdout.readline().decode().strip()
        # Strip output of the colors
        return re.sub(r'\x1b\[(([0-9]+m)|(.{1,2}))', '', line).strip()

    def _process_monitor(self, resource, download_dir, download_only,
                         player_type, player_args):
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
                    bus.post(TorrentDownloadedMetadataEvent(url=webtorrent_url, resource=resource))
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
                    webtorrent_url = webtorrent_url.replace(
                        'http://localhost', 'http://' + get_ip_or_hostname())

                    self._torrent_stream_urls[resource] = webtorrent_url
                    self._download_started_event.set()
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
                    bus.post(TorrentDownloadStartEvent(
                        resource=resource, media_file=media_file,
                        stream_url=webtorrent_url, url=webtorrent_url))
                    break

            if not output_dir:
                raise RuntimeError('Could not download torrent')
            if not download_only and (not media_file or not webtorrent_url):
                if not media_file:
                    self.logger.warning(
                        'The torrent does not contain any video files')
                else:
                    self.logger.warning('WebTorrent could not start streaming')

                # Keep downloading but don't start the player
                try:
                    self._webtorrent_process.wait()
                except Exception as e:
                    self.logger.warning(f'WebTorrent process error: {str(e)}')

                return

            player = None

            if not download_only:
                # Wait until we have enough chunks to start the player
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

                player = get_plugin('media.' + player_type) if player_type \
                    else self._media_plugin

                media = media_file if player.is_local() else webtorrent_url

                self.logger.info(
                    'Starting playback of {} to {} through {}'.format(
                        media_file, player.__class__.__name__,
                        webtorrent_url))

                subfile = self.get_subtitles(media)
                if subfile:
                    player_args['subtitles'] = subfile

                player.play(media, **player_args)
                self.logger.info('Waiting for player to terminate')

            self._wait_for_player(player)
            self.logger.info('Torrent player terminated')
            bus.post(TorrentDownloadCompletedEvent(resource=resource,
                                                   output_dir=output_dir,
                                                   media_file=media_file,
                                                   url=webtorrent_url))

            try:
                self.quit()
            except Exception as e:
                self.logger.warning(f'Could not terminate WebTorrent process: {str(e)}')

            self.logger.info('WebTorrent process terminated')

        return _thread

    def _wait_for_player(self, player):
        stop_evt = None

        if player:
            media_cls = player.__class__.__name__

            if media_cls == 'MediaMplayerPlugin':
                # noinspection PyProtectedMember
                stop_evt = player._mplayer_stopped_event
            elif media_cls == 'MediaMpvPlugin' or media_cls == 'MediaVlcPlugin':
                stop_evt = threading.Event()

                def stop_callback():
                    stop_evt.set()
                player.on_stop(stop_callback)
            elif media_cls == 'MediaOmxplayerPlugin':
                stop_evt = threading.Event()

                def stop_callback():
                    stop_evt.set()
                player.add_handler('stop', stop_callback)

        if stop_evt:
            stop_evt.wait()
        else:
            # Fallback: wait for the webtorrent process to terminate
            self._webtorrent_process.wait()

    def _get_torrent_download_dir(self):
        if self._media_plugin.download_dir:
            return self._media_plugin.download_dir
        else:
            d = os.path.join(os.path.expanduser('~'), 'Downloads')
            os.makedirs(d, exist_ok=True)
            return d

    def get_subtitles(self, filepath):
        try:
            plugin = get_plugin('media.subtitles')
            if not plugin or not plugin.languages:
                return

            subs = plugin.get_subtitles(filepath).output
            if not subs:
                return

            sub = plugin.download_subtitles(subs[0]['SubDownloadLink'],
                                            filepath).output

            if sub:
                return sub['filename']
        except Exception as e:
            self.logger.warning('Could not get subtitles for {}: {}'.format(
                filepath, str(e)))

    @action
    def play(self, resource, player=None, download_only=False, **player_args):
        """
        Download and stream a torrent

        :param resource: Play a resource, as a magnet link, torrent URL or
            torrent file path
        :type resource: str

        :param player: If set, use this plugin type as a player for the
            torrent. Supported types: 'mplayer', 'vlc', 'omxplayer', 'chromecast', 'mpv'.
            If not set, then the default configured media plugin will be used.
        :type player: str

        :param player_args: Any arguments to pass to the player plugin's
            play() method
        :type player_args: dict

        :param download_only: If false then it will start streaming the torrent on the local player once the
            download starts, otherwise it will just download it (default: false)
        :type download_only: bool
        """

        if self._webtorrent_process:
            try:
                self.quit()
            except Exception as e:
                self.logger.debug('Failed to quit the previous instance: {}'.
                                  format(str(e)))

        download_dir = self._get_torrent_download_dir()
        webtorrent_args = [self.webtorrent_bin, 'download', '-o', download_dir]

        if self.webtorrent_port:
            webtorrent_args += ['-p', self.webtorrent_port]
        webtorrent_args += [resource]

        self._download_started_event.clear()
        self._webtorrent_process = subprocess.Popen(webtorrent_args,
                                                    stdout=subprocess.PIPE)

        threading.Thread(target=self._process_monitor(
            resource=resource, download_dir=download_dir,
            player_type=player, player_args=player_args,
            download_only=download_only)).start()

        stream_url = None
        player_ready_wait_start = time.time()

        while not stream_url:
            triggered = self._download_started_event.wait(
                self._web_stream_ready_timeout)

            if not triggered or time.time() - player_ready_wait_start >= \
                    self._web_stream_ready_timeout:
                break

            stream_url = self._torrent_stream_urls.get(resource)

        if not stream_url:
            return (None, ("The webtorrent process hasn't started " +
                           "streaming after {} seconds").format(
                self._web_stream_ready_timeout))

        return {'resource': resource, 'url': stream_url}

    @action
    def download(self, resource, **kwargs):
        return self.play(resource, download_only=True)

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
            try:
                self._webtorrent_process.kill()
            except Exception as e:
                self.logger.warning(f'Error on WebTorrent process kill: {str(e)}')

        self._webtorrent_process = None

    @action
    def load(self, resource, **kwargs):
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

        return {'state': self._media_plugin.status().get('state', PlayerState.STOP.value)}

    def pause(self, *args, **kwargs):
        raise NotImplementedError

    def voldown(self, *args, **kwargs):
        raise NotImplementedError

    def volup(self, *args, **kwargs):
        raise NotImplementedError

    def back(self, *args, **kwargs):
        raise NotImplementedError

    def forward(self, *args, **kwargs):
        raise NotImplementedError

    def toggle_subtitles(self, *args, **kwargs):
        raise NotImplementedError

    def set_subtitles(self, filename, *args, **kwargs):
        raise NotImplementedError

    def remove_subtitles(self, *args, **kwargs):
        raise NotImplementedError

    def is_playing(self, *args, **kwargs):
        raise NotImplementedError

    def mute(self, *args, **kwargs):
        raise NotImplementedError

    def seek(self, *args, **kwargs):
        raise NotImplementedError

    def set_position(self, *args, **kwargs):
        raise NotImplementedError

    def set_volume(self, volume):
        raise NotImplementedError


# vim:sw=4:ts=4:et:
