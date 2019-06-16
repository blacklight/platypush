import json
import socket
import threading
import time

from platypush.backend import Backend
from platypush.context import get_plugin
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

        self.logger.debug('Connecting to {}:{}'.format(host, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self._socks[host] = sock
        self.logger.info('Connected to {}:{}'.format(host, port))
        return sock

    def _disconnect(self, host, port):
        sock = self._socks.get(host)
        if not sock:
            self.logger.debug('Not connected to {}:{}'.format(host, port))
            return

        try: sock.close()
        except: pass
        finally: self._socks[host] = None

    @classmethod
    def _recv(cls, sock):
        buf = b''
        while buf[-2:] != cls._SOCKET_EOL:
            buf += sock.recv(1)
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

    def _client(self, host, port):
        def _thread():
            set_thread_name('Snapcast-' + host)

            try:
                self._status(host, port)
            except Exception as e:
                self.logger.warning(('Exception while getting the status ' +
                                     'of the Snapcast server {}:{}: {}').
                                    format(host, port, str(e)))

                try:
                    self._disconnect(host, port)
                    time.sleep(self.poll_seconds)
                except:
                    pass

            while not self.should_stop():
                try:
                    sock = self._connect(host, port)
                    msgs = self._recv(sock)

                    if not isinstance(msgs, list):
                        msgs = [msgs]

                    for msg in msgs:
                        self.logger.debug('Received message on {}:{}: {}'.format(
                            host, port, msg))

                        evt = self._parse_msg(host=host, msg=msg)
                        if evt:
                            self.bus.post(evt)
                except Exception as e:
                    self.logger.warning(('Exception while getting the status ' +
                                         'of the Snapcast server {}:{}: {}').
                                        format(host, port, str(e)))

                    try:
                        self._disconnect(host, port)
                    except:
                        pass
                    finally:
                        time.sleep(self.poll_seconds)

        return _thread

    @classmethod
    def _get_req_id(cls):
        return get_plugin('music.snapcast')._get_req_id()

    def _status(self, host, port):
        sock = self._connect(host, port)

        request = {
            'id': self._get_req_id(),
            'jsonrpc':'2.0',
            'method':'Server.GetStatus'
        }

        get_plugin('music.snapcast')._send(sock, request)
        try:
            return self._recv(sock).get('result', {}).get('server', {})
        except Exception as e:
            self.logger.warning('Unable to connect to {}:{}: {}'.format(
                host, port, str(e)))
            self._socks[host] = None

    def run(self):
        super().run()

        self.logger.info('Initialized Snapcast backend - hosts: {} ports: {}'.
                         format(self.hosts, self.ports))

        while not self.should_stop():
            for i, host in enumerate(self.hosts):
                port = self.ports[i]
                self._threads[host] = threading.Thread(
                    target=self._client(host, port),
                    name='Snapcast-' + host
                )

                self._threads[host].start()

            for host in self.hosts:
                self._threads[host].join()


# vim:sw=4:ts=4:et:
