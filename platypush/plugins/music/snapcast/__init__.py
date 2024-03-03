import json
import select
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Collection, Iterable, List, Optional, Tuple, Union

from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.music.snapcast import (
    ClientVolumeChangeEvent,
    GroupMuteChangeEvent,
    ClientConnectedEvent,
    ClientDisconnectedEvent,
    ClientLatencyChangeEvent,
    ClientNameChangeEvent,
    GroupStreamChangeEvent,
    StreamUpdateEvent,
    ServerUpdateEvent,
)
from platypush.plugins import RunnablePlugin, action


class MusicSnapcastPlugin(RunnablePlugin):
    """
    Plugin to interact with a `Snapcast <https://github.com/badaix/snapcast>`_
    instance, control clients mute status, volume, playback etc.

    See https://github.com/badaix/snapcast/blob/master/doc/json_rpc_api/v2_0_0.md
    for further reference about the returned API types.
    """

    _DEFAULT_SNAPCAST_PORT = 1705
    _DEFAULT_POLL_SECONDS = 10  # Poll servers each 10 seconds
    _SOCKET_EOL = '\r\n'.encode()

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = _DEFAULT_SNAPCAST_PORT,
        hosts: Optional[Iterable[dict]] = None,
        poll_interval: Optional[float] = _DEFAULT_POLL_SECONDS,
        **kwargs,
    ):
        """
        :param host: Default Snapcast server host.
        :param port: Default Snapcast server control port (default: 1705).
        :param hosts: If specified, then the provided list of Snapcast servers
            will be monitored, rather than just the one provided on ``host``.
            This setting can be used either in conjunction with ``host`` (in
            that case, if the ``host`` is not specified on a request then
            ``host`` will be used as a fallback), or on its own (in that case
            requests with no host specified will target the first server in the
            list). Note however that either ``host`` or ``hosts`` must be
            provided. Format:

                .. code-block:: yaml

                    hosts:
                        - host: localhost
                          port: 1705  # Default port

                        - host: snapcast.example.com
                          port: 9999

        :param poll_seconds: How often the plugin will poll remote servers for
            status updates (default: 10 seconds).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)

        self._hosts = self._get_hosts(host=host, port=port, hosts=hosts)
        assert self._hosts, 'No Snapcast hosts specified'
        self._latest_req_id = 0
        self._latest_req_id_lock = threading.RLock()

        self._socks = {}
        self._threads = {}
        self._statuses = {}

    @property
    def host(self) -> str:
        return self._hosts[0][0]

    @property
    def port(self) -> int:
        if not getattr(self, '_hosts', None):
            return self._DEFAULT_SNAPCAST_PORT

        return self._hosts[0][1]

    def _get_hosts(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        hosts: Optional[Iterable[dict]] = None,
    ) -> List[Tuple[str, int]]:
        ret = []
        if hosts:
            assert all(
                isinstance(h, dict) and h.get('host') for h in hosts
            ), f'Expected a list of dicts with host and port keys, got: {hosts}'

            ret.extend((h['host'], h.get('port', self.port)) for h in hosts)

        if host and port:
            ret.insert(0, (host, port))

        return list(dict.fromkeys(ret))

    def _next_req_id(self):
        with self._latest_req_id_lock:
            self._latest_req_id += 1
            return self._latest_req_id

    def _connect(self, host: str, port: int, reuse: bool = False):
        if reuse and self._socks.get(host) and self._socks[host].fileno() >= 0:
            return self._socks[host]

        self.logger.debug('Connecting to %s:%d', host, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        if reuse:
            self._socks[host] = sock

        self.logger.info('Connected to %s:%d', host, port)
        return sock

    def _disconnect(self, host: str, port: int):
        sock = self._socks.get(host)
        if not sock:
            self.logger.debug('Not connected to %s:%d', host, port)
            return

        try:
            sock.close()
        except Exception as e:
            self.logger.warning(
                'Exception while disconnecting from %s:%d: %s', host, port, e
            )
        finally:
            self._socks[host] = None

    @classmethod
    def _send(cls, sock: socket.socket, req: Union[dict, str, bytes]):
        if isinstance(req, dict):
            req = json.dumps(req)
        if isinstance(req, str):
            req = req.encode()

        assert isinstance(
            req, bytes
        ), f'Unsupported type {type(req)} for Snapcast request'
        sock.send(req + cls._SOCKET_EOL)

    @classmethod
    def _recv_result(cls, sock: socket.socket):
        msg = cls._recv(sock)
        if not msg:
            return None

        return msg.get('result')

    @classmethod
    def _recv(cls, sock: socket.socket):
        sock.setblocking(False)
        buf = b''

        while buf[-2:] != cls._SOCKET_EOL:
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                ch = sock.recv(1)
                if not ch:
                    raise ConnectionError('Connection reset by peer')

                buf += ch
            else:
                return None

        return json.loads(buf)

    @classmethod
    def _parse_event(cls, host, msg):
        evt = None

        if msg.get('method') == 'Client.OnVolumeChanged':
            client_id = msg.get('params', {}).get('id')
            volume = msg.get('params', {}).get('volume', {}).get('percent')
            muted = msg.get('params', {}).get('volume', {}).get('muted')
            evt = ClientVolumeChangeEvent(
                host=host, client=client_id, volume=volume, muted=muted
            )
        elif msg.get('method') == 'Group.OnMute':
            group_id = msg.get('params', {}).get('id')
            muted = msg.get('params', {}).get('mute')
            evt = GroupMuteChangeEvent(host=host, group=group_id, muted=muted)
        elif msg.get('method') == 'Client.OnConnect':
            client = msg.get('params', {}).get('client')
            evt = ClientConnectedEvent(host=host, client=client)
        elif msg.get('method') == 'Client.OnDisconnect':
            client = msg.get('params', {}).get('client')
            evt = ClientDisconnectedEvent(host=host, client=client)
        elif msg.get('method') == 'Client.OnLatencyChanged':
            client = msg.get('params', {}).get('id')
            latency = msg.get('params', {}).get('latency')
            evt = ClientLatencyChangeEvent(host=host, client=client, latency=latency)
        elif msg.get('method') == 'Client.OnNameChanged':
            client = msg.get('params', {}).get('id')
            name = msg.get('params', {}).get('name')
            evt = ClientNameChangeEvent(host=host, client=client, name=name)
        elif msg.get('method') == 'Group.OnStreamChanged':
            group_id = msg.get('params', {}).get('id')
            stream_id = msg.get('params', {}).get('stream_id')
            evt = GroupStreamChangeEvent(host=host, group=group_id, stream=stream_id)
        elif msg.get('method') == 'Stream.OnUpdate':
            stream_id = msg.get('params', {}).get('stream_id')
            stream = msg.get('params', {}).get('stream')
            evt = StreamUpdateEvent(host=host, stream_id=stream_id, stream=stream)
        elif msg.get('method') == 'Server.OnUpdate':
            server = msg.get('params', {}).get('server')
            evt = ServerUpdateEvent(host=host, server=server)

        return evt

    def _event_listener(self, host: str, port: int):
        def _thread():
            while not self.should_stop():
                try:
                    sock = self._connect(host, port, reuse=True)
                    msgs = self._recv(sock)

                    if msgs is None:
                        continue
                    if not isinstance(msgs, list):
                        msgs = [msgs]

                    for msg in msgs:
                        self.logger.debug(
                            'Received message on %s:%d: %s', host, port, msg
                        )

                        evt = self._parse_event(host=host, msg=msg)
                        if evt:
                            get_bus().post(evt)
                except Exception as e:
                    self.logger.warning(
                        'Exception while getting the status of the Snapcast server %s:%d: %s',
                        host,
                        port,
                        e,
                    )

                    self._disconnect(host, port)
                finally:
                    if self.poll_interval:
                        time.sleep(self.poll_interval)

        return _thread

    def _get_group(self, sock: socket.socket, group: str):
        for g in self._get_status(sock).get('groups', []):
            if group == g.get('id') or group == g.get('name'):
                return g

        return None

    def _get_client(self, sock: socket.socket, client: str):
        for g in self._get_status(sock).get('groups', []):
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

    def _get_status(self, sock: socket.socket) -> dict:
        request = {
            'id': self._next_req_id(),
            'jsonrpc': '2.0',
            'method': 'Server.GetStatus',
        }

        self._send(sock, request)
        return (self._recv_result(sock) or {}).get('server', {})

    def _status(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        client: Optional[str] = None,
        group: Optional[str] = None,
    ):
        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            if client:
                return self._get_client(sock, client)
            if group:
                return self._get_group(sock, group)

            return self._get_status(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    def _status_response(
        self,
        host: str,
        port: int,
        client: Optional[str] = None,
        group: Optional[str] = None,
    ):
        sock = None
        try:
            sock = self._connect(host, port)
            if client:
                return self._get_client(sock, client)
            if group:
                return self._get_group(sock, group)

            return {'host': host, 'port': port, **self._get_status(sock)}
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def status(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        client: Optional[str] = None,
        group: Optional[str] = None,
    ):
        """
        Get the current status of a Snapcast server, client or group.

        If not host, client or group is specified, the action will return the
        status of all the Snapcast servers.

        :param host: Snapcast server to query (default: default configured host)
        :param port: Snapcast server port (default: default configured port)
        :param client: Client ID or name (default: None)
        :param group: Group ID or name (default: None)

        :returns: dict. Example:

            .. code-block:: json

                "output": {
                    "host": "localhost",
                    "port": 1705,
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

        if client or group or host:
            return self._status_response(
                host=host or self.host,
                port=port or self.port,
                client=client,
                group=group,
            )

        # Run status in parallel on all the hosts and return a list with all the
        # results
        with ThreadPoolExecutor(max_workers=len(self._hosts)) as executor:
            return list(
                executor.map(lambda h: self._status_response(h[0], h[1]), self._hosts)
            )

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

        assert client or group, 'Please specify either a client or a group'
        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._next_req_id(),
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
            return self._recv_result(sock)
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

        assert not (volume is None and delta is None and mute is None), (
            'Please specify either an absolute volume, a relative delta or '
            + 'a mute status'
        )

        sock = None

        try:
            sock = self._connect(host or self.host, port or self.port)
            request = {
                'id': self._next_req_id(),
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
            return self._recv_result(sock)
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
                'id': self._next_req_id(),
                'jsonrpc': '2.0',
                'method': 'Client.SetName',
                'params': {},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            request['params']['id'] = c['id']
            request['params']['name'] = name
            self._send(sock, request)
            return self._recv_result(sock)
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
                'id': self._next_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetName',
                'params': {
                    'id': group,
                    'name': name,
                },
            }

            self._send(sock, request)
            return self._recv_result(sock)
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
                'id': self._next_req_id(),
                'jsonrpc': '2.0',
                'method': 'Client.SetLatency',
                'params': {'latency': latency},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            request['params']['id'] = c['id']
            self._send(sock, request)
            return self._recv_result(sock)
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
                'id': self._next_req_id(),
                'jsonrpc': '2.0',
                'method': 'Server.DeleteClient',
                'params': {},
            }

            c = self._get_client(sock, client)
            assert c, f'No such client: {client}'
            request['params']['id'] = c['id']
            self._send(sock, request)
            return self._recv_result(sock)
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
                'id': self._next_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetClients',
                'params': {'id': g['id'], 'clients': []},
            }

            for client in clients:
                c = self._get_client(sock, client)
                assert c, f'No such client: {client}'
                request['params']['clients'].append(c['id'])

            self._send(sock, request)
            return self._recv_result(sock)
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
                'id': self._next_req_id(),
                'jsonrpc': '2.0',
                'method': 'Group.SetStream',
                'params': {
                    'id': g['id'],
                    'stream_id': stream_id,
                },
            }

            self._send(sock, request)
            return self._recv_result(sock)
        finally:
            try:
                if sock:
                    sock.close()
            except Exception as e:
                self.logger.warning('Error on socket close: %s', e)

    @action
    def get_playing_streams(self, exclude_local: bool = False):
        """
        Returns the configured remote streams that are currently active and
        unmuted.

        .. warning:: This action is deprecated and mostly kept for
            backward-compatibility purposes, as it doesn't allow the case where
            multiple Snapcast instances can be running on the same host, nor it
            provides additional information other that something is playing on a
            certain host and port. Use :meth:`.status` instead.

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

        playing_hosts = {}

        def _worker(host: str, port: int):
            try:
                if exclude_local and (
                    host == 'localhost' or host == Config.get('device_id')
                ):
                    return

                server_status = self._status(host=host, port=port) or {}
                device_id: str = Config.get('device_id')  # type: ignore
                client_status = (
                    self._status(host=host, port=port, client=device_id) or {}
                )

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

        for host, port in self._hosts:
            w = threading.Thread(target=_worker, args=(host, port))
            w.start()
            workers.append(w)

        while workers:
            w = workers.pop()
            w.join()

        return {'hosts': playing_hosts}

    def main(self):
        while not self.should_stop():
            for host, port in self._hosts:
                thread_name = f'Snapcast-{host}-{port}'

                self._threads[host] = threading.Thread(
                    target=self._event_listener(host, port), name=thread_name
                )

                self._threads[host].start()

            for thread in self._threads.values():
                thread.join()

            self._threads = {}

    def stop(self):
        for host, sock in self._socks.items():
            if sock:
                try:
                    sock.close()
                except Exception as e:
                    self.logger.warning(
                        'Could not close Snapcast connection to %s: %s: %s',
                        host,
                        type(e),
                        e,
                    )

        super().stop()


# vim:sw=4:ts=4:et:
