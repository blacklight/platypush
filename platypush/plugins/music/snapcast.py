import json
import socket
import threading

from platypush.config import Config
from platypush.context import get_backend
from platypush.plugins import Plugin, action


class MusicSnapcastPlugin(Plugin):
    """
    Plugin to interact with a [Snapcast](https://github.com/badaix/snapcast)
    instance, control clients mute status, volume, playback etc.

    See https://github.com/badaix/snapcast/blob/master/doc/json_rpc_api/v2_0_0.md
    for further reference about the returned API types.
    """

    _DEFAULT_SNAPCAST_PORT = 1705
    _SOCKET_EOL = '\r\n'.encode()

    def __init__(self, host='localhost', port=_DEFAULT_SNAPCAST_PORT,
                 *args, **kwargs):
        """
        :param host: Default Snapcast server host (default: localhost)
        :type host: str

        :param port: Default Snapcast server control port (default: 1705)
        :type port: int
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

    def _connect(self, host=None, port=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info('Connecting to Snapcast host {}:{}'.format(host, port))
        sock.connect((host or self.host, port or self.port))
        return sock

    @classmethod
    def _send(cls, sock, req):
        if isinstance(req, dict):
            req = json.dumps(req)
        if isinstance(req, str):
            req = req.encode()
        if not isinstance(req, bytes):
            raise RuntimeError('Unsupported type {} for Snapcast request: {}'.
                               format(type(req), req))

        sock.send(req + cls._SOCKET_EOL)

    @classmethod
    def _recv(cls, sock):
        buf = b''
        while buf[-2:] != cls._SOCKET_EOL:
            buf += sock.recv(1)
        return json.loads(buf.decode().strip()).get('result')

    def _get_group(self, sock, group):
        for g in self._status(sock).get('groups', []):
            if group == g.get('id') or group == g.get('name'):
                return g

    def _get_client(self, sock, client):
        for g in self._status(sock).get('groups', []):
            clients = g.get('clients', [])

            for c in clients:
                if client == c.get('id') or \
                        client == c.get('name') or \
                        client == c.get('host', {}).get('name') or \
                        client == c.get('host', {}).get('ip'):
                    c['group_id'] = g.get('id')
                    return c

    def _status(self, sock):
        request = {
            'id': self._get_req_id(),
            'jsonrpc':'2.0',
            'method':'Server.GetStatus'
        }

        self._send(sock, request)
        return (self._recv(sock) or {}).get('server', {})

    @action
    def status(self, host=None, port=None, client=None, group=None):
        """
        Get the status either of a Snapcast server, client or group

        :param host: Snapcast server to query (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int

        :param client: Client ID or name (default: None)
        :type client: str

        :param group: Group ID or name (default: None)
        :type group: str

        :returns: dict.

        Example::

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
                            "raw": "pipe:////tmp/snapfifo?buffer_ms=20&codec=pcm&name=mopidy&sampleformat=48000:16:2",
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
            try: sock.close()
            except: pass


    @action
    def mute(self, client=None, group=None, mute=None, host=None, port=None):
        """
        Set the mute status of a connected client or group

        :param client: Client name or ID to mute
        :type client: str

        :param group: Group ID to mute
        :type group: str

        :param mute: Mute status. If not set, the mute status of the selected
            client/group will be toggled.
        :type mute: bool

        :param host: Snapcast server to query (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        if not client and not group:
            raise RuntimeError('Please specify either a client or a group')

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Group.SetMute' if group else 'Client.SetVolume',
                'params': {}
            }

            if group:
                group = self._get_group(sock, group)
                cur_muted = group['muted']
                request['params']['id'] = group['id']
                request['params']['mute'] = not cur_muted if mute is None else mute
            else:
                client = self._get_client(sock, client)
                cur_muted = client['config']['volume']['muted']
                request['params']['id'] = client['id']
                request['params']['volume'] = {}
                request['params']['volume']['percent'] = client['config']['volume']['percent']
                request['params']['volume']['muted'] = not cur_muted if mute is None else mute

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass

    @action
    def volume(self, client, volume=None, delta=None, mute=None, host=None,
               port=None):
        """
        Set the volume of a connected client

        :param client: Client name or ID
        :type client: str

        :param volume: Absolute volume to set between 0 and 100
        :type volume: int

        :param delta: Relative volume change in percentage (e.g. +10 or -10)
        :type delta: int

        :param mute: Set to true or false if you want to toggle the muted status
        :type mute: bool

        :param host: Snapcast server (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        if volume is None and delta is None and mute is None:
            raise RuntimeError('Please specify either an absolute volume or ' +
                               'relative delta')

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Client.SetVolume',
                'params': {}
            }

            client = self._get_client(sock, client)
            cur_volume = int(client['config']['volume']['percent'])
            cur_mute = bool(client['config']['volume']['muted'])

            if volume is not None:
                volume = int(volume)
            elif delta is not None:
                volume = cur_volume + int(delta)

            if volume is not None:
                if volume > 100: volume = 100
                if volume < 0: volume = 0
            else:
                volume = cur_volume

            if mute is None:
                mute = cur_mute

            request['params']['id'] = client['id']
            request['params']['volume'] = {}
            request['params']['volume']['percent'] = volume
            request['params']['volume']['muted'] = mute
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass

    @action
    def set_client_name(self, client, name, host=None, port=None):
        """
        Set/change the name of a connected client

        :param client: Current client name or ID to rename
        :type client: str

        :param name: New name
        :type name: str

        :param host: Snapcast server (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Client.SetName',
                'params': {}
            }

            client = self._get_client(sock, client)
            request['params']['id'] = client['id']
            request['params']['name'] = name
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass

    @action
    def set_latency(self, client, latency, host=None, port=None):
        """
        Set/change the latency of a connected client

        :param client: Client name or ID
        :type client: str

        :param latency: New latency in milliseconds
        :type latency: float

        :param host: Snapcast server (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Client.SetLatency',
                'params': {
                    'latency': latency
                }
            }

            client = self._get_client(sock, client)
            request['params']['id'] = client['id']
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass

    @action
    def delete_client(self, client, host=None, port=None):
        """
        Delete a client from the Snapcast server

        :param client: Client name or ID
        :type client: str

        :param host: Snapcast server (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Server.DeleteClient',
                'params': {}
            }

            client = self._get_client(sock, client)
            request['params']['id'] = client['id']
            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass

    @action
    def group_set_clients(self, group, clients, host=None, port=None):
        """
        Sets the clients for a group on a Snapcast server

        :param group: Group name or ID
        :type group: str

        :param clients: List of client names or IDs
        :type clients: list[str]

        :param host: Snapcast server (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            group = self._get_group(sock, group)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Group.SetClients',
                'params': {
                    'id': group['id'],
                    'clients': []
                }
            }

            for client in clients:
                client = self._get_client(sock, client)
                request['params']['clients'].append(client['id'])

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass


    @action
    def group_set_stream(self, group, stream_id, host=None, port=None):
        """
        Sets the active stream for a group.

        :param group: Group name or ID
        :type group: str

        :param stream_id: Stream ID
        :type stream_id: str

        :param host: Snapcast server (default: default configured host)
        :type host: str

        :param port: Snapcast server port (default: default configured port)
        :type port: int
        """

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            group = self._get_group(sock, group)
            request = {
                'id': self._get_req_id(),
                'jsonrpc':'2.0',
                'method': 'Group.SetStream',
                'params': {
                    'id': group['id'],
                    'stream_id': stream_id,
                }
            }

            self._send(sock, request)
            return self._recv(sock)
        finally:
            try: sock.close()
            except: pass


    @action
    def get_backend_hosts(self):
        """
        :return: A dict with the Snapcast hosts configured on the backend
            in the format host -> port
        """

        hosts = {}
        for i in range(len(self.backend_hosts)):
            hosts[self.backend_hosts[i]] = self.backend_ports[i]
        return hosts

    @action
    def get_playing_streams(self, exclude_local=False):
        """
        Returns the remote streams configured in the `music.snapcast` backend
        that are currently active and unmuted.

        :param exclude_local: Exclude localhost connections (default: False)
        :type exclude_local: bool

        :returns: dict with the host->port mapping.

        Example::

            {
                "hosts": {
                    "server_1": 1705,
                    "server_2": 1705,
                    "server_3": 1705
                }
            }

        """

        backend_hosts = self.get_backend_hosts().output
        playing_hosts = {}

        def _worker(host, port):
            try:
                if exclude_local and (host == 'localhost'
                                    or  host == Config.get('device_id')):
                    return

                server_status = self.status(host=host, port=port).output
                client_status = self.status(host=host, port=port,
                                            client=Config.get('device_id')).output

                if client_status.get('config', {}).get('volume', {}).get('muted'):
                    return

                group = [g for g in server_status.get('groups', {})
                        if g.get('id') == client_status.get('group_id')].pop(0)

                if group.get('muted'):
                    return

                stream = [s for s in server_status.get('streams')
                        if s.get('id') == group.get('stream_id')].pop(0)

                if stream.get('status') != 'playing':
                    return

                playing_hosts[host] = port
            except Exception as e:
                self.logger.warning(('Error while retrieving the status of ' +
                                     'Snapcast host at {}:{}: {}').format(
                                         host, port, str(e)))

        workers = []

        for host, port in backend_hosts.items():
            w = threading.Thread(target=_worker, args=(host,port))
            w.start()
            workers.append(w)

        while workers:
            w = workers.pop()
            w.join()

        return {'hosts': playing_hosts}


# vim:sw=4:ts=4:et:
