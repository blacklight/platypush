import datetime
import os
import re
import requests
import threading
import xmlrpc.client

from pathlib import Path
from typing import List, Optional

from platypush.context import get_bus
from platypush.plugins import action
from platypush.plugins.torrent import TorrentPlugin
from platypush.message.event.torrent import \
    TorrentDownloadStartEvent, TorrentDownloadedMetadataEvent, TorrentDownloadProgressEvent, \
    TorrentDownloadCompletedEvent, TorrentPausedEvent, TorrentResumedEvent, TorrentQueuedEvent, TorrentRemovedEvent, \
    TorrentEvent


class RtorrentPlugin(TorrentPlugin):
    """
    Plugin to interact search, download and manage torrents through RTorrent.
    The usage of this plugin is advised over :class:`platypush.plugins.torrent.TorrentPlugin`, as RTorrent is a more
    flexible and optimized solution for downloading and managing torrents compared to the Platypush native plugin.

    Configuration:

        - Install ``rtorrent`` on your system - on Debian/Ubuntu/Raspbian::

            apt-get install rtorrent

        - Configure the ``rtorrent`` XML/RPC interface, usually by adding the following lines to your
          ``~/.rtorrent.rc``:

            .. code-block:: yaml

              # Enable XML/RPC
              scgi_local = /home/user/.rpc.socket

        - Use a web server to bridge the RPC interface exposed by RTorrent over HTTP. Some configuration examples are
          available `here <https://github.com/rakshasa/rtorrent/wiki/RPC-Setup-XMLRPC>`_. I usually use ``lighttpd``
          because it's easy to configure and it comes with a built-in SCGI module. Install the server e.g. using
          ``apt``::

            apt-get install lighttpd

        - Create a base configuration file like this under e.g. ``~/.config/rtorrent/lighttpd.conf``:

          .. code-block:: python

            ### Base configuration
            server.modules = (
                "mod_indexfile",
                "mod_access",
                "mod_alias",
                "mod_redirect",
            )

            # Make sure that all the directories exist.

            # server.document-root isn't really needed, but lighttpd
            # won't start if it doesn't find a document root.
            server.document-root        = "/home/user/.local/share/rtorrent/html"
            server.upload-dirs          = ( "/home/user/.cache/uploads" )
            server.errorlog             = "/home/user/.local/log/rtorrent/error.log"
            server.pid-file             = "/home/user/.local/run/lighttpd.pid"
            server.username             = "your-user"
            server.groupname            = "your-group"
            server.port                 = 5000

            index-file.names            = ( "index.html" )

            ### Configure the RTorrent XML/RPC endpoint
            server.modules += ( "mod_scgi" )
            scgi.server = (
                # Bind an endpoint called /RPC2 to your local interface
                "/RPC2" =>
                  ( "127.0.0.1" =>
                    (
                      # Read from the RTorrent XML/RPC socket
                      "socket" => "/home/user/.rpc.socket",
                      "check-local" => "disable",
                      "disable-time" => 0,  # don't disable scgi if connection fails
                    )
                  )
              )

        - Start the HTTP service, and optionally enable it as a system/user service::

            lighttpd -f ~/.config/rtorrent/lighttpd.conf

        - Start RTorrent and check that the XML/RPC interface works:

          .. code-block:: bash

            $ xmlrpc localhost:8000 system.listMethods
            # Should return a list with all the methods exposed by RTorrent.
            $ xmlrpc localhost:5000 download_list
            Result:
            Array of 0 items:

        - It is advised to let the RTorrent instance run in e.g. ``screen`` or ``tmux`` on the server machine - it is
          more reliable than letting the plugin start/stop the instance, and you have an easy CLI interface to attach
          to manage/monitor your torrents.

        - In this example, the URL to configure in the plugin would be ``http://localhost:5000/RPC2``.

    Triggers:

        * :class:`platypush.message.event.torrent.TorrentQueuedEvent` when a new torrent transfer is queued.
        * :class:`platypush.message.event.torrent.TorrentRemovedEvent` when a torrent transfer is removed.
        * :class:`platypush.message.event.torrent.TorrentDownloadStartEvent` when a torrent transfer starts.
        * :class:`platypush.message.event.torrent.TorrentDownloadedMetadataEvent` when the metadata of a torrent
            transfer has been downloaded.
        * :class:`platypush.message.event.torrent.TorrentDownloadProgressEvent` when a transfer is progressing.
        * :class:`platypush.message.event.torrent.TorrentPausedEvent` when a transfer is paused.
        * :class:`platypush.message.event.torrent.TorrentResumedEvent` when a transfer is resumed.
        * :class:`platypush.message.event.torrent.TorrentDownloadCompletedEvent` when a transfer is completed.

    """

    def __init__(self, url: str, poll_seconds: float = 5.0, torrent_files_dir: str = '~/.rtorrent/watch', **kwargs):
        """
        :param url: HTTP URL that exposes the XML/RPC interface of RTorrent (e.g. ``http://localhost:5000/RPC2``).
        :param poll_seconds: How often the plugin will monitor for changes in the torrent state (default: 5 seconds).
        :param torrent_files_dir: Directory where torrents and metadata files will be downloaded
            (default: ``~/.rtorrent/watch``).
        """
        super().__init__(**kwargs)
        self.torrent_files_dir = os.path.abspath(os.path.expanduser(torrent_files_dir))
        Path(self.torrent_files_dir).mkdir(parents=True, exist_ok=True, mode=0o755)

        self._monitor_stop = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_status = {}
        self._torrent_urls = {}
        self._status_lock = threading.RLock()

        self.poll_seconds = poll_seconds
        self.url = url
        self.client = xmlrpc.client.Server(self.url)
        self.methods = set(self._list_methods())
        self.start_monitor()

    def _get_client(self) -> xmlrpc.client.Server:
        return xmlrpc.client.Server(self.url)

    def _fire_event(self, event: TorrentEvent, *_, **__):
        bus = get_bus()
        bus.post(event)

    def _process_events(self, status: dict, last_status: dict):
        if not status:
            self._fire_event(TorrentRemovedEvent(**last_status))
            return

        if not last_status:
            self._fire_event(TorrentQueuedEvent(**status))

        progress = status.get('progress', 0)
        name = status.get('name')
        start_date = status.get('start_date')
        finish_date = status.get('finish_date')
        is_active = status.get('is_active')

        if name and not last_status.get('name'):
            self._fire_event(TorrentDownloadedMetadataEvent(**status))

        if start_date and not last_status.get('start_date'):
            self._fire_event(TorrentDownloadStartEvent(**status))

        if is_active and not last_status.get('is_active'):
            self._fire_event(TorrentResumedEvent(**status))
        elif not is_active and last_status.get('is_active'):
            self._fire_event(TorrentPausedEvent(**status))

        if progress > 0:
            if progress > last_status.get('progress', 0):
                self._fire_event(TorrentDownloadProgressEvent(**status))

        if finish_date and not last_status.get('finish_date'):
            self._fire_event(TorrentDownloadCompletedEvent(**status))

    def _torrent_monitor(self, *_, **__):
        def thread():
            self.logger.info('Starting torrent monitoring')

            while not self._monitor_stop.is_set():
                try:
                    # noinspection PyUnresolvedReferences
                    statuses = self.status().output
                    last_statuses = self._last_status.copy()
                    self._last_status = statuses
                    torrent_hashes = set(statuses.keys()).union(last_statuses.keys())

                    for torrent_hash in torrent_hashes:
                        self._process_events(statuses.get(torrent_hash, {}), last_statuses.get(torrent_hash, {}))
                except Exception as e:
                    self.logger.warning('Error while monitoring torrent status')
                    self.logger.exception(e)
                finally:
                    self._monitor_stop.wait(timeout=self.poll_seconds)

            self.logger.info('Stopped torrent monitoring')

        return thread

    def _multicall(self, *args) -> List[list]:
        if 'd.multicall2' in self.methods:
            return self.client.d.multicall2('', *args)
        if 'd.multicall' in self.methods:
            return self.client.d.multicall(*args)

        raise AssertionError('No multicall method available on the rtorrent interface')

    @action
    def start_monitor(self):
        """
        Start monitoring the status of the RTorrent instance.
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.info('Torrent monitoring already running')
            return

        self._monitor_stop.clear()
        self._monitor_thread = threading.Thread(target=self._torrent_monitor())
        self._monitor_thread.start()

    @action
    def stop_monitor(self):
        """
        Stop monitoring the status of the RTorrent instance.
        """
        if not (self._monitor_thread and self._monitor_thread.is_alive()):
            self.logger.info('Torrent monitoring already stopped')
        else:
            self._monitor_stop.set()
            self._monitor_thread.join(timeout=60.0)

        self._monitor_thread = None

    @action
    def download_torrent_file(self, torrent: str) -> str:
        """
        Download a torrent link to ``torrent_files_dir``.

        :param torrent: Torrent URL, magnet link or local file.
        :return: Path to the locally downloaded .torrent file.
        """
        if torrent.startswith('magnet:?'):
            # Magnet link: extract and download
            m = re.search(r'xt=urn:btih:([^&/]+)', torrent)
            assert m, 'Invalid magnet link: {}'.format(torrent)
            torrent_hash = m.group(1)
            torrent_file = os.path.join(self.torrent_files_dir, '{}.torrent'.format(torrent_hash))

            with open(torrent_file, 'w') as f:
                f.write('d10:magnet-uri{length}:{info}e'.format(length=len(torrent), info=torrent))

            self._torrent_urls[torrent_hash] = torrent
            return torrent_file

        if torrent.startswith('http://') or torrent.startswith('https://'):
            # HTTP resource
            info = requests.get(torrent).text
            torrent_file = os.path.join(self.torrent_files_dir, torrent.split('/')[-1])
            if not torrent_file.endswith('.torrent'):
                torrent_file += '.torrent'

            with open(torrent_file, 'w') as f:
                f.write(info)

            self._torrent_urls[torrent_file.split('.')[0]] = torrent
            return torrent_file

        # Local torrent file
        torrent_file = os.path.abspath(os.path.expanduser(torrent))
        assert os.path.isfile(torrent_file), 'No such torrent file: {}'.format(torrent)

        self._torrent_urls[os.path.basename(torrent_file).split('.')[0]] = 'file://' + torrent
        return torrent_file

    @action
    def download(self, torrent: str, is_media: bool = False, *_, **__):
        """
        Download a torrent.

        :param torrent: Torrent to download. Supported formats:

            * Magnet URLs
            * Torrent URLs
            * Local torrent files

        :param is_media: Set it to true if you're downloading a media file that you'd like to stream as soon as the
            first chunks are available. If so, then the events and the status method will only include media files
        :return: The status of the torrent.
        """
        # noinspection PyUnresolvedReferences
        torrent_file = self.download_torrent_file(torrent).output
        client = self._get_client()
        client.load.start('', torrent_file)

    def _list_methods(self) -> List[str]:
        return self.client.system.listMethods()

    @action
    def list_methods(self) -> List[str]:
        """
        :return: The list of methods exposed by the RTorrent instance
        """
        return list(self.methods)

    @action
    def status(self, torrent: str = None) -> dict:
        """
        Get the status of the current transfers.

        :param torrent: Torrent hash.
        :returns: A dictionary:

          .. code-block:: json

            {
              "HASH1234567890": {
                "hash": "HASH1234567890",
                "name": "Your torrent name",
                "save_path": "/home/user/Downloads/Your torrent name",
                "is_active": true,
                "is_open": true,
                "completed_bytes": 666894336,
                "download_rate": 451345,
                "is_multi_file": true,
                "remaining_bytes": 1482827011,
                "size_bytes": 2149721347,
                "load_date": "2020-09-02T18:42:19",
                "peers": 0,
                "state": "paused",
                "start_date": "2020-09-02T18:42:19",
                "finish_date": null,
                "upload_rate": 143967,
                "progress": 31.0,
                "files": ["list", "of", "downloaded", "files"]
              }
            }

        """
        attrs = ['hash', 'name', 'save_path', 'is_active', 'is_open', 'completed_bytes', 'download_rate',
                 'is_multi_file', 'remaining_bytes', 'size_bytes', 'load_date', 'peers', 'start_date',
                 'finish_date', 'upload_rate']
        cmds = ['d.hash=', 'd.name=', 'd.directory=', 'd.is_active=', 'd.is_open=', 'd.completed_bytes=',
                'd.down.rate=', 'd.is_multi_file=', 'd.left_bytes=', 'd.size_bytes=', 'd.load_date=',
                'd.peers_connected=', 'd.timestamp.started=', 'd.timestamp.finished=', 'd.up.rate=']

        mappers = {
            'is_active': lambda v: bool(v),
            'is_open': lambda v: bool(v),
            'is_multi_file': lambda v: bool(v),
            'load_date': lambda v: datetime.datetime.fromtimestamp(v) if v else None,
            'start_date': lambda v: datetime.datetime.fromtimestamp(v) if v else None,
            'finish_date': lambda v: datetime.datetime.fromtimestamp(v) if v else None,
        }

        with self._status_lock:
            torrents = {
                info[0]: {
                    attr: mappers[attr](info[i]) if attr in mappers else info[i]
                    for i, attr in enumerate(attrs)
                }
                for info in self._multicall('', *cmds)
            }

        for torrent_id, info in torrents.items():
            torrents[torrent_id]['progress'] = round(100. * (info['completed_bytes']/info['size_bytes']), 1)
            torrents[torrent_id]['url'] = self._torrent_urls.get(torrent_id, torrent_id)
            torrents[torrent_id]['is_paused'] = not info['is_active']
            torrents[torrent_id]['paused'] = not info['is_active']  # Back compatibility with TorrentPlugin
            torrents[torrent_id]['size'] = info['size_bytes']  # Back compatibility with TorrentPlugin
            torrents[torrent_id]['files'] = []

            if not info['is_open']:
                torrents[torrent_id]['state'] = 'stopped'
            elif not info['is_active']:
                torrents[torrent_id]['state'] = 'paused'
            else:
                torrents[torrent_id]['state'] = 'downloading'

            if info.get('save_path'):
                torrents[torrent_id]['files'] = list(str(f) for f in Path(info['save_path']).rglob('*')) \
                    if info.get('is_multi_file') else info['save_path']

        return torrents.get(torrent, {}) if torrent else torrents

    @action
    def open(self, torrent: str) -> dict:
        """
        Open a loaded torrent transfer.

        :param torrent: Torrent hash.
        :return: The status of the torrent.
        """
        self.client.d.open(torrent)
        return self.status(torrent).output

    @action
    def pause(self, torrent: str) -> dict:
        """
        Pause a torrent transfer.

        :param torrent: Torrent hash.
        :return: The status of the torrent.
        """
        self.client.d.pause(torrent)
        return self.status(torrent).output

    @action
    def resume(self, torrent) -> dict:
        """
        Resume a torrent transfer.

        :param torrent: Torrent hash.
        :return: The status of the torrent.
        """
        self.client.d.resume(torrent)
        return self.status(torrent).output

    @action
    def stop(self, torrent) -> dict:
        """
        Stop a torrent transfer.

        :param torrent: Torrent hash.
        :return: The status of the torrent.
        """
        self.client.d.stop(torrent)
        return self.status(torrent).output

    @action
    def remove(self, torrent):
        """
        Stop and remove a torrent transfer (without removing the downloaded files).

        :param torrent: Torrent hash.
        """
        self.client.d.stop(torrent)
        self.client.d.erase(torrent)

    @action
    def quit(self):
        """
        Terminate all the active transfers and quit the monitor.
        """
        # noinspection PyUnresolvedReferences
        torrents = list(self.status().output.keys()).copy()
        for torrent in torrents:
            self.remove(torrent)

        self.stop_monitor()

    @action
    def execute(self, method: str, *args, **kwargs):
        """
        Execute a raw command over the RTorrent RPC interface.

        :param method: Method name.
        :param args: Method arguments.
        :param kwargs: Method keyword-arguments.
        :return: Anything returned by the RPC method.
        """
        method = getattr(self.client, method)
        return method(*args, **kwargs)


# vim:sw=4:ts=4:et:
