import json
import select
import socket
import threading
import time

from platypush.backend import Backend
from platypush.utils import set_thread_name
from platypush.message.event.music.snapcast import ClientVolumeChangeEvent, \
    GroupMuteChangeEvent, ClientConnectedEvent, ClientDisconnectedEvent, \
    ClientLatencyChangeEvent, ClientNameChangeEvent, GroupStreamChangeEvent, \
    StreamUpdateEvent, ServerUpdateEvent


class MusicSnapcastBackend(Backend):
    """
    Backend that listens for notification and status changes on one or more
    [Snapcast](https://github.com/badaix/snapcast) servers.

    Triggers:

        * :class:`platypush.message.event.music.snapcast.ClientConnectedEvent`
        * :class:`platypush.message.event.music.snapcast.ClientDisconnectedEvent`
        * :class:`platypush.message.event.music.snapcast.ClientVolumeChangeEvent`
        * :class:`platypush.message.event.music.snapcast.ClientLatencyChangeEvent`
        * :class:`platypush.message.event.music.snapcast.ClientNameChangeEvent`
        * :class:`platypush.message.event.music.snapcast.GroupMuteChangeEvent`
        * :class:`platypush.message.event.music.snapcast.GroupStreamChangeEvent`
        * :class:`platypush.message.event.music.snapcast.StreamUpdateEvent`
        * :class:`platypush.message.event.music.snapcast.ServerUpdateEvent`
    """

    _DEFAULT_SNAPCAST_PORT = 1705
    _DEFAULT_POLL_SECONDS = 10   # Poll servers each 10 seconds
    _SOCKET_EOL = '\r\n'.encode()

    def __init__(self, hosts=None, ports=None,
                 poll_seconds=_DEFAULT_POLL_SECONDS, *args, **kwargs):
        """
        :param hosts: List of Snapcast server names or IPs to monitor (default:
            `['localhost']`
        :type hosts: list[str]

        :param ports: List of control ports for the configured Snapcast servers
            (default: `[1705]`)
        :type ports: list[int]

        :param poll_seconds: How often the backend will poll remote servers for
            status updated (default: 10 seconds)
        :type poll_seconds: float
        """

        super().__init__(*args, **kwargs)

        if hosts is None:
            hosts = ['localhost']
        if ports is None:
            ports = [self._DEFAULT_SNAPCAST_PORT]

        self.hosts = hosts[:]
        self.ports = ports[:]
        self.poll_seconds = poll_seconds
        self._socks = {}
        self._threads = {}
        self._statuses = {}

        if len(hosts) > len(ports):
            for _ in range(len(ports), len(hosts)):
                self.ports.append(self._DEFAULT_SNAPCAST_PORT)

    def _connect(self, host, port):
        if self._socks.get(host):
            return self._socks[host]

        self.logger.debug('Connecting to {host}:{port}'.format(host=host, port=port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self._socks[host] = sock
        self.logger.info('Connected to {host}:{port}'.format(host=host, port=port))
        return sock

    def _disconnect(self, host, port):
        sock = self._socks.get(host)
        if not sock:
            self.logger.debug('Not connected to {}:{}'.format(host, port))
            return

        try:
            sock.close()
        except Exception as e:
            self.logger.warning(('Exception while disconnecting from {host}:{port}: {error}'.
                                 format(host=host, port=port, error=str(e))))
        finally:
            self._socks[host] = None

    @classmethod
    def _recv(cls, sock):
        sock.setblocking(0)
        buf = b''

        while buf[-2:] != cls._SOCKET_EOL:
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                buf += sock.recv(1)
            else:
                return

        return json.loads(buf.decode().strip())

    @classmethod
    def _parse_msg(cls, host, msg):
        evt = None

        if msg.get('method') == 'Client.OnVolumeChanged':
            client_id = msg.get('params', {}).get('id')
            volume = msg.get('params', {}).get('volume', {}).get('percent')
            muted = msg.get('params', {}).get('volume', {}).get('muted')
            evt = ClientVolumeChangeEvent(host=host, client=client_id,
                                          volume=volume, muted=muted)
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

    def _client(self, host, port, thread_name):
        def _thread():
            set_thread_name(thread_name)

            while not self.should_stop():
                try:
                    sock = self._connect(host, port)
                    msgs = self._recv(sock)

                    if msgs is None:
                        continue
                    if not isinstance(msgs, list):
                        msgs = [msgs]

                    for msg in msgs:
                        self.logger.debug('Received message on {host}:{port}: {msg}'.
                                          format(host=host, port=port, msg=msg))

                        # noinspection PyTypeChecker
                        evt = self._parse_msg(host=host, msg=msg)
                        if evt:
                            self.bus.post(evt)
                except Exception as e:
                    self.logger.warning('Exception while getting the status ' + 'of the Snapcast server {}:{}: {}'.
                                        format(host, port, str(e)))

                    self._disconnect(host, port)
                finally:
                    time.sleep(self.poll_seconds)

        return _thread

    def run(self):
        super().run()

        self.logger.info('Initialized Snapcast backend - hosts: {} ports: {}'.
                         format(self.hosts, self.ports))

        while not self.should_stop():
            for i, host in enumerate(self.hosts):
                port = self.ports[i]
                thread_name = 'Snapcast-{host}-{port}'.format(host=host, port=port)

                self._threads[host] = threading.Thread(
                    target=self._client(host, port, thread_name),
                    name=thread_name
                )

                self._threads[host].start()

            for host in self.hosts:
                self._threads[host].join()

        self.logger.info('Snapcast backend terminated')

    def on_stop(self):
        self.logger.info('Received STOP event on the Snapcast backend')
        for host, sock in self._socks.items():
            if sock:
                try:
                    sock.close()
                except Exception as e:
                    self.logger.warning('Could not close Snapcast connection to {}: {}: {}'.format(
                        host, type(e), str(e)))


# vim:sw=4:ts=4:et:
