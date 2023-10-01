import json
import socket
import threading
from typing import Collection, Optional

from platypush.config import Config
from platypush.context import get_backend
from platypush.plugins import Plugin, action


class MusicSnapcastPlugin(Plugin):
    """
    Plugin to interact with a `Snapcast <https://github.com/badaix/snapcast>`_
    instance, control clients mute status, volume, playback etc.

    See https://github.com/badaix/snapcast/blob/master/doc/json_rpc_api/v2_0_0.md
    for further reference about the returned API types.
    """

    _DEFAULT_SNAPCAST_PORT = 1705
    _SOCKET_EOL = '\r\n'.encode()

    def __init__(
        self, host: str = 'localhost', port: int = _DEFAULT_SNAPCAST_PORT, **kwargs
    ):
        """
        :param host: Default Snapcast server host (default: localhost)
        :param port: Default Snapcast server control port (default: 1705)
        """
        super().__init__(**kwargs)

        self.host = host
        self.port = port
        self._latest_req_id = 0
        self._latest_req_id_lock = threading.RLock()

        backend = get_backend('music.snapcast')
        backend_hosts = backend.hosts if backend else [self.host]
        backend_ports = backend.ports if backend else [self.port]
        self.backend_hosts = backend_hosts
        self.backend_ports = backend_ports

    def _get_req_id(self):
        with self._latest_req_id_lock:
            self._latest_req_id += 1
            return self._latest_req_id

    def _connect(self, host: Optional[str] = None, port: Optional[int] = None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info('Connecting to Snapcast host %s:%d', host, port)
        sock.connect((host or self.host, port or self.port))
        return sock

    @classmethod
    def _send(cls, sock: socket.socket, req: dict):
        if isinstance(req, dict):
            r = json.dumps(req)
        if isinstance(req, str):
            r = req.encode()
        if not isinstance(r, bytes):
            raise RuntimeError(
                f'Unsupported type {type(req)} for Snapcast request: {req}'
            )

        sock.send(r + cls._SOCKET_EOL)

    @classmethod
    def _recv(cls, sock):
        buf = b''
        while buf[-2:] != cls._SOCKET_EOL:
            buf += sock.recv(1)
        return json.loads(buf.decode().strip()).get('result')

    def _get_group(self, sock: socket.socket, group: str):
        for g in self._status(sock).get('groups', []):
            if group == g.get('id') or group == g.get('name'):
                return g

        return None

    def _get_client(self, sock: socket.socket, client: str):
        for g in self._status(sock).get('groups', []):
            clients = g.get('clients', [])

            for c in clients:
                if (
                    client == c.get('id')
                    or client == c.get('name')
                    or client == c.get('host', {}).get('name')
                    or client == c.get('host', {}).get('ip')
                ):
                    c['group_id'] = g.get('id')
                    return c

        return None

    def _status(self, sock: socket.socket):
        request = {
            'id': self._get_req_id(),
            'jsonrpc': '2.0',
            'method': 'Server.GetStatus',
        }

        self._send(sock, request)
        return (self._recv(sock) or {}).get('server', {})

    @action
    def status(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        client: Optional[str] = None,
        group: Optional[str] = None,
    ):
        """
        Get the status either of a Snapcast server, client or group

        :param host: Snapcast server to query (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        :param client: Client ID or name (default: None)
        :param group: Group ID or name (default: None)

        :returns: dict. Example:

            .. code-block:: json

                "output": {
                    "groups": [
                        {
                        "clients": [
                            {
                            "config": {
                                "instance": 1,
                                "latency": 0,
                                "name": "",
                                "volume": {
                                "muted": false,
                                "percent": 96
                                }
                            },
                            "connected": true,
                            "host": {
                                "arch": "x86_64",
                                "ip": "YOUR_IP",
                                "mac": "YOUR_MAC",
                                "name": "YOUR_NAME",
                                "os": "YOUR_OS"
                            },
                            "id": "YOUR_ID",
                            "lastSeen": {
                                "sec": 1546648311,
                                "usec": 86011
                            },
                            "snapclient": {
                                "name": "Snapclient",
                                "protocolVersion": 2,
                                "version": "0.15.0"
                            }
                            }
                        ],
                        "id": "YOUR_ID",
                        "muted": false,
                        "name": "",
                        "stream_id": "mopidy"
                        }
                    ],
                    "server": {
                        "host": {
                        "arch": "armv7l",
                        "ip": "",
                        "mac": "",
                        "name": "YOUR_NAME",
                        "os": "YOUR_OS"
                        },
                        "snapserver": {
                        "controlProtocolVersion": 1,
                        "name": "Snapserver",
                        "protocolVersion": 1,
                        "version": "0.15.0"
                        }
                    },
                    "streams": [
                        {
                            "id": "mopidy",
                            "meta": {
                                "STREAM": "mopidy"
                            },
                            "status": "playing",
                            "uri": {
                                "fragment": "",
                                "host": "",
                                "path": "/tmp/snapfifo",
                                "query": {
                                "buffer_ms": "20",
                                "codec": "pcm",
                                "name": "mopidy",
                                "sampleformat": "48000:16:2"
                                },
                                "raw": "pipe:////tmp/fifo?buffer_ms=20&codec=pcm&name=mopidy&sampleformat=48000:16:2",
                                "scheme": "pipe"
                            }
                        }
                    ]
                }

        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            if client:
                return self._get_client(sock, client)
            if group:
                return self._get_group(sock, group)

            return self._status(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def mute(
        self,
        client: Optional[str] = None,
        group: Optional[str] = None,
        mute: Optional[bool] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Set the mute status of a connected client or group

        :param client: Client name or ID to mute
        :param group: Group ID to mute
        :param mute: Mute status. If not set, the mute status of the selected
            client/group will be toggled.
        :param host: Snapcast server to query (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        if not (client and group):
            raise RuntimeError('Please specify either a client or a group')

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetMute' if group else 'Client.SetVolume',
                'params': {},
            }

            if group:
                g = self._get_group(sock, group)
                assert g, f'No such group: {group}'
                cur_muted = g['muted']
                request['params']['id'] = g['id']
                request['params']['mute'] = not cur_muted if mute is None else mute
            elif client:
                c = self._get_client(sock, client)
                assert c, f'No such client: {client}'
                cur_muted = c['config']['volume']['muted']
                request['params']['id'] = c['id']
                request['params']['volume'] = {}
                request['params']['volume']['percent'] = c['config']['volume'][
                    'percent'
                ]
                request['params']['volume']['muted'] = (
                    not cur_muted if mute is None else mute
                )

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def volume(
        self,
        client: str,
        volume: Optional[int] = None,
        delta: Optional[int] = None,
        mute: Optional[bool] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Set the volume of a connected client.

        :param client: Client name or ID
        :param volume: Absolute volume to set between 0 and 100
        :param delta: Relative volume change in percentage (e.g. +10 or -10)
        :param mute: Set to true or false if you want to toggle the muted status
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        if volume is None and delta is None and mute is None:
            raise RuntimeError(
                'Please specify either an absolute volume or ' + 'relative delta'
            )

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Client.SetVolume',
                'params': {},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            cur_volume = int(c['config']['volume']['percent'])
            cur_mute = bool(c['config']['volume']['muted'])

            if volume is not None:
                volume = int(volume)
            elif delta is not None:
                volume = cur_volume + int(delta)

            volume = max(0, min(100, volume)) if volume is not None else cur_volume
            if mute is None:
                mute = cur_mute

            request['params']['id'] = c['id']
            request['params']['volume'] = {}
            request['params']['volume']['percent'] = volume
            request['params']['volume']['muted'] = mute
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def set_client_name(
        self,
        client: str,
        name: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Set/change the name of a connected client

        :param client: Current client name or ID to rename
        :param name: New name
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Client.SetName',
                'params': {},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            request['params']['id'] = c['id']
            request['params']['name'] = name
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def set_group_name(
        self,
        group: str,
        name: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Set/change the name of a group

        :param group: Group ID to rename
        :param name: New name
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetName',
                'params': {
                    'id': group,
                    'name': name,
                },
            }

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def set_latency(
        self,
        client: str,
        latency: float,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Set/change the latency of a connected client

        :param client: Client name or ID
        :param latency: New latency in milliseconds
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Client.SetLatency',
                'params': {'latency': latency},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            request['params']['id'] = c['id']
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def delete_client(
        self, client: str, host: Optional[str] = None, port: Optional[int] = None
    ):
        """
        Delete a client from the Snapcast server

        :param client: Client name or ID
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Server.DeleteClient',
                'params': {},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            request['params']['id'] = c['id']
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def group_set_clients(
        self,
        group: str,
        clients: Collection[str],
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Sets the clients for a group on a Snapcast server

        :param group: Group name or ID
        :param clients: List of client names or IDs
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            g = self._get_group(sock, group)
            assert g, f'No such group: {group}'
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetClients',
                'params': {'id': g['id'], 'clients': []},
            }

            for client in clients:
                c = self._get_client(sock, client)
                assert c, f'No such client: {client}'
                request['params']['clients'].append(c['id'])

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def group_set_stream(
        self,
        group: str,
        stream_id: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Sets the active stream for a group.

        :param group: Group name or ID
        :param stream_id: Stream ID
        :param host: Snapcast server (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            g = self._get_group(sock, group)
            assert g, f'No such group: {group}'
            request = {
                'id': self._get_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetStream',
                'params': {
                    'id': g['id'],
                    'stream_id': stream_id,
                },
            }

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def get_backend_hosts(self):
        """
        :return: A dict with the Snapcast hosts configured on the backend
            in the format ``host -> port``.
        """

        return {
            host: self.backend_ports[i] for i, host in enumerate(self.backend_hosts)
        }

    @action
    def get_playing_streams(self, exclude_local: bool = False):
        """
        Returns the remote streams configured in the `music.snapcast` backend
        that are currently active and unmuted.

        :param exclude_local: Exclude localhost connections (default: False)

        :returns: dict with the host->port mapping. Example:

            .. code-block:: json

                {
                    "hosts": {
                        "server_1": 1705,
                        "server_2": 1705,
                        "server_3": 1705
                    }
                }

        """

        backend_hosts: dict = self.get_backend_hosts().output  # type: ignore
        playing_hosts = {}

        def _worker(host, port):
            try:
                if exclude_local and (
                    host == 'localhost' or host == Config.get('device_id')
                ):
                    return

                server_status: dict = self.status(host=host, port=port).output  # type: ignore
                client_status: dict = self.status(  # type: ignore
                    host=host, port=port, client=Config.get('device_id')
                ).output

                if client_status.get('config', {}).get('volume', {}).get('muted'):
                    return

                group = next(
                    iter(
                        g
                        for g in server_status.get('groups', {})
                        if g.get('id') == client_status.get('group_id')
                    )
                )

                if group.get('muted'):
                    return

                stream = next(
                    iter(
                        s
                        for s in server_status.get('streams', {})
                        if s.get('id') == group.get('stream_id')
                    )
                )

                if stream.get('status') != 'playing':
                    return

                playing_hosts[host] = port
            except Exception as e:
                self.logger.warning(
                    'Error while retrieving the status of Snapcast host at %s:%d: %s',
                    host,
                    port,
                    e,
                )

        workers = []

        for host, port in backend_hosts.items():
            w = threading.Thread(target=_worker, args=(host, port))
            w.start()
            workers.append(w)

        while workers:
            w = workers.pop()
            w.join()

        return {'hosts': playing_hosts}


# vim:sw=4:ts=4:et:
