import contextlib
import logging
import multiprocessing
import os
import pathlib
import re
import select
import socket
import ssl as _ssl
import struct
from typing import Iterable, Optional, Type, Sequence, Dict, Tuple

import irc.bot
from irc.client import Connection, Event as _IRCEvent, ServerConnection, DCCConnection, ip_numstr_to_quad, \
    ip_quad_to_numstr
from irc.connection import Factory as ConnectionFactory
from irc.events import codes as irc_event_codes

from platypush.context import get_bus
from platypush.message.event.irc import IRCEvent, IRCChannelJoinEvent, IRCChannelKickEvent, IRCDisconnectEvent, \
    IRCModeEvent, IRCNickChangeEvent, IRCPartEvent, IRCQuitEvent, IRCConnectEvent, IRCPrivateMessageEvent, \
    IRCPublicMessageEvent, IRCDCCRequestEvent, IRCDCCMessageEvent, IRCDCCFileRequestEvent, IRCCTCPMessageEvent, \
    IRCDCCFileRecvCompletedEvent, IRCDCCFileRecvCancelledEvent, IRCDCCFileSendCompletedEvent, \
    IRCDCCFileSendCancelledEvent


class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(
            self, server: str, port: int, nickname: str, alias: str,
            channels: Iterable[str],
            response_timeout: Optional[float],
            dcc_file_transfer_timeout: Optional[float],
            dcc_accept_timeout: Optional[float],
            dcc_downloads_dir: str, realname: Optional[str] = None,
            password: Optional[str] = None, ssl: bool = False,
            ipv6: bool = False, stop_message: Optional[str] = None,
            dcc_ip_whitelist: Optional[Sequence[str]] = None,
            dcc_ip_blacklist: Optional[Sequence[str]] = None,
            dcc_nick_whitelist: Optional[Sequence[str]] = None,
            dcc_nick_blacklist: Optional[Sequence[str]] = None,
            dcc_max_connections: Optional[int] = None,
    ):
        connection_factory = ConnectionFactory()
        if ssl:
            connection_factory.wrapper = _ssl.wrap_socket
        if ipv6:
            connection_factory.family = socket.AF_INET6

        super().__init__(
            server_list=[(server, port)], nickname=nickname,
            realname=realname, connect_factory=connection_factory
        )

        self.server = server
        self.port = port
        self.alias = alias
        self._password = password
        self.channels.update({channel: None for channel in channels})
        self._stop_message = stop_message
        self.dcc_ip_whitelist = set(dcc_ip_whitelist or [])
        self.dcc_ip_blacklist = set(dcc_ip_blacklist or [])
        self.dcc_nick_whitelist = set(dcc_nick_whitelist or [])
        self.dcc_nick_blacklist = set(dcc_nick_blacklist or [])
        self.dcc_downloads_dir = dcc_downloads_dir
        self.response_timeout = response_timeout
        self.dcc_file_transfer_timeout = dcc_file_transfer_timeout
        self.dcc_accept_timeout = dcc_accept_timeout
        self.dcc_max_connections = dcc_max_connections
        self._dcc_send_procs: Dict[Tuple[str, int], multiprocessing.Process] = {}
        self._dcc_recv_procs: Dict[Tuple[str, int], multiprocessing.Process] = {}
        self._dcc_proc_completion_queue = multiprocessing.Queue()
        self._dcc_processor: Optional[multiprocessing.Process] = None
        self.logger = logging.getLogger(f'irc@{server}')
        # Maps <matching_event_type> -> <response_queue>
        self._pending_requests: Dict[str, multiprocessing.Queue] = {}

    @property
    def stop_message(self) -> Optional[str]:
        return self._stop_message

    def _post_event(self, connection: Connection, output_event_type: Type[IRCEvent], **kwargs):
        if isinstance(connection, ServerConnection):
            kwargs['server'] = connection.server
            kwargs['port'] = connection.port

        kwargs['connected'] = connection.connected
        kwargs['alias'] = self.alias
        event = output_event_type(**kwargs)
        get_bus().post(event)

    def on_join(self, connection: ServerConnection, event: _IRCEvent):
        self._post_event(connection, IRCChannelJoinEvent, channel=event.target, nick=event.source.nick)
        super()._on_join(connection, event)

    def on_kick(self, connection: ServerConnection, event: _IRCEvent):
        self._post_event(
            connection, IRCChannelKickEvent, channel=event.target,
            source_nick=event.arguments[1], target_nick=event.arguments[0]
        )

        super()._on_kick(connection, event)

    def on_nick(self, connection: ServerConnection, event: _IRCEvent):
        self._post_event(
            connection, IRCNickChangeEvent, before=event.source.nick, after=event.target.nick
        )
        super()._on_nick(connection, event)

    def on_mode(self, connection: ServerConnection, event: _IRCEvent):
        self._post_event(
            connection, IRCModeEvent, mode=event.arguments[0],
            source=event.source.nick,
            target_=(event.arguments[1] if len(event.arguments) > 1 else None),
            channel=event.target,
        )

        super()._on_mode(connection, event)

    def on_part(self, connection: Connection, event: _IRCEvent):
        self._post_event(connection, IRCPartEvent, nick=event.source.nick)
        super()._on_part(connection, event)

    def on_quit(self, connection: Connection, event: _IRCEvent):
        self._post_event(connection, IRCQuitEvent, nick=event.source.nick)
        super()._on_quit(connection, event)

    def on_welcome(self, connection: Connection, *_):
        self._post_event(connection, IRCConnectEvent)
        for channel in self.channels:
            self.logger.info(f'Joining channel {channel}')
            self.connection.join(channel)

    @staticmethod
    def on_nicknameinuse(connection: ServerConnection, *_):
        connection.nick(connection.nickname + '_')

    @staticmethod
    def _mentions_me(connection: ServerConnection, text: str) -> bool:
        return bool(re.search(fr'(^|\s|@){connection.nickname}(:|\s|!|\?|$)', text))

    def on_pubmsg(self, connection: ServerConnection, event: _IRCEvent):
        self._post_event(
            connection, IRCPublicMessageEvent,
            text=event.arguments[0], nick=event.source.nick,
            channel=event.target,
            mentions_me=self._mentions_me(connection, event.arguments[0])
        )

    def on_privmsg(self, connection: ServerConnection, event: _IRCEvent):
        self._post_event(
            connection, IRCPrivateMessageEvent,
            text=event.arguments[0], nick=event.source.nick,
            channel=event.target,
            mentions_me=self._mentions_me(connection, event.arguments[0])
        )

    def on_dccchat(self, connection: DCCConnection, event: _IRCEvent):
        if len(event.arguments) != 2:
            return

        args = event.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return

            nick = event.source.nick
            if not self._is_dcc_connection_request_allowed(address=address, nick=nick):
                self.logger.info(f'Refused DCC connection from address={address} nick={nick}')
                connection.disconnect('Unauthorized peer')
                return

            self._post_event(
                connection, IRCDCCRequestEvent, address=address, port=port, nick=nick
            )

            self.dcc('chat').connect(address, port)

    def _read(self, sock: socket.socket, bufsize: int = 4096) -> bytes:
        if self.dcc_file_transfer_timeout:
            sock.setblocking(False)
            has_data = select.select([sock], [], [], self.dcc_file_transfer_timeout)
            if has_data[0]:
                return sock.recv(bufsize)
            raise TimeoutError(f'Time out ({self.dcc_file_transfer_timeout}s)')

        return sock.recv(bufsize)

    def _dcc_connect_processor(self):
        while True:
            proc_type, addr, port = self._dcc_proc_completion_queue.get()
            conn_map = getattr(self, f'_dcc_{proc_type}_procs', {})
            conn_map.pop((addr, port), None)

    def _process_dcc_recv(self, connection: DCCConnection, filename: str, address: str, port: int, size: int):
        pathlib.Path(self.dcc_downloads_dir).mkdir(parents=True, exist_ok=True)
        filename = os.path.abspath(os.path.join(self.dcc_downloads_dir, filename))
        assert filename.startswith(self.dcc_downloads_dir), (
            'Attempt to save a file outside the downloads directory'
        )

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock, \
                open(filename, 'wb') as f:
            try:
                sock.connect((address, port))
                processed_bytes = 0

                while processed_bytes < size:
                    buf = self._read(sock)
                    processed_bytes += len(buf)
                    f.write(buf)
                    sock.send(f'{socket.htonl(processed_bytes)}'.encode())

                self._post_event(
                    connection, IRCDCCFileRecvCompletedEvent, address=address,
                    port=port, file=filename, size=size
                )
            except Exception as e:
                self.logger.error(f'DCC transfer error from {address}:{port}: {e}')
                self.logger.exception(e)
                self._post_event(
                    connection, IRCDCCFileRecvCancelledEvent, address=address,
                    port=port, file=filename, error=str(e)
                )
            finally:
                connection.disconnect()
                self._dcc_proc_completion_queue.put(('recv', address, port))

    def _process_dcc_send(self, connection: DCCConnection, filename: str):
        try:
            dcc_sock, addr = connection.socket.accept()
            self._set_accept_timeout(dcc_sock)
            self.logger.info(f'Accepted DCC connection from {addr}')

            # Create a new server socket for the file transfer
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv_sock:
                srv_sock.bind((connection.localaddress, 0))
                address, transfer_port = srv_sock.getsockname()
                dcc_sock.send(
                    (
                        f'CTCP_MESSAGE \x01'
                        f'DCC SEND {os.path.basename(filename)} '
                        f'{ip_quad_to_numstr(address)} {transfer_port} '
                        f'{os.path.getsize(filename)}\x01\r\n'
                    ).encode()
                )

                # Wait for a connection on the file transfer port
                self._set_accept_timeout(srv_sock)
                srv_sock.listen(1)
                client_sock, addr = srv_sock.accept()
                self.logger.info(f'DCC file transfer for {filename} accepted on {addr}')

                try:
                    with open(filename, 'rb') as f:
                        buf = f.read(4096)
                        while buf:
                            client_sock.send(buf)
                            recv_bytes = struct.unpack('>i', self._read(client_sock))[0]
                            buf = buf[recv_bytes:]

                            if not buf:
                                buf = f.read(4096)

                    self._post_event(
                        connection, IRCDCCFileSendCompletedEvent,
                        file=filename, address=address, port=transfer_port
                    )
                finally:
                    client_sock.close()
                    dcc_sock.close()
        except Exception as e:
            self.logger.error(f'DCC transfer error to {connection.peeraddress}:{connection.peerport}: {e}')
            self.logger.exception(e)
            self._post_event(
                connection, IRCDCCFileSendCancelledEvent, address=connection.peeraddress,
                port=connection.peerport, file=filename, error=str(e)
            )
        finally:
            connection.disconnect()
            self._dcc_proc_completion_queue.put(('send', connection.localaddress, connection.localport))

    def _set_accept_timeout(self, sock: socket.socket):
        if self.dcc_accept_timeout:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(self.dcc_accept_timeout)

    def _stop_dcc_connection(self, address: str, port: int):
        self.logger.info(f'Stopping DCC connection to {address}:{port}')
        proc = self._dcc_recv_procs.pop((address, port), None)
        if proc and proc.is_alive():
            proc.terminate()

    def _accept_dcc_file_request(self, connection: DCCConnection, ctcp_msg: str, nick: str):
        ctcp_msg = [
            token.strip()
            for token in ctcp_msg.split(' ')
            if token
        ]

        filename = ' '.join(ctcp_msg[2:-3])
        address, port, size = ctcp_msg[-3:]

        if not (filename and address and port):
            return

        address = ip_numstr_to_quad(address)
        port = int(port)
        size = int(size)

        if port == 0:
            self.logger.warning('Passive CTCP file transfer is currently not supported')
            return

        self._post_event(
            connection, IRCDCCFileRequestEvent,
            address=address,
            port=port, file=filename,
            size=size, nick=nick
        )

        # Accept the file request
        # (if we're here then the peer is whitelisted/not blacklisted)
        self._dcc_recv_procs[(address, port)] = multiprocessing.Process(
            target=self._process_dcc_recv, kwargs={
                'connection': connection,
                'address': address,
                'port': port,
                'filename': filename,
                'size': size,
            }
        )

        self._dcc_recv_procs[(address, port)].start()

    def _handle_ctcp_message(self, connection: DCCConnection, event: _IRCEvent):
        body = event.arguments[0]
        sep_pos = [i for i, ch in enumerate(body) if ch == ord(b'\x01')]
        msg = []

        try:
            msg = [
                body[(0 if i == 0 else sep_pos[i - 1] + 1):pos].decode().strip()
                for i, pos in enumerate(sep_pos)
            ][1:]
        except (ValueError, TypeError):
            pass

        if not msg:
            return

        # Check if this is a DCC file send request
        if msg[0].startswith('DCC SEND '):
            self._accept_dcc_file_request(connection, msg[0], event.source)
        else:
            self._post_event(
                connection, IRCCTCPMessageEvent, address=event.source, message=msg
            )

    def on_dccmsg(self, connection: DCCConnection, event: _IRCEvent):
        ctcp_header = b'CTCP_MESSAGE'
        if event.arguments[0][:len(ctcp_header)] == ctcp_header:
            return self._handle_ctcp_message(connection, event)

        self._post_event(connection, IRCDCCMessageEvent, address=event.source, body=event.arguments[0])

    def on_disconnect(self, connection: Connection, event: _IRCEvent):
        self._post_event(connection, IRCDisconnectEvent)
        # Cache channels for reconnect logic
        channels = {ch: None for ch in self.channels.keys()}
        super()._on_disconnect(connection, event)
        self.channels.update(channels)

    def on_whoisuser(self, _, event: _IRCEvent):
        self._process_event_on_queue(event)

    def on_currenttopic(self, _, event: _IRCEvent):
        self._process_event_on_queue(event)

    def _process_event_on_queue(self, event: _IRCEvent):
        q = self._pending_requests.get(event.type)
        if q:
            q.put(event)

    def _on_generic_event(self, _, event: _IRCEvent):
        self.logger.debug(f'Received raw unhandled IRC event on {self.server}: {event.__dict__}')

    def _is_dcc_connection_request_allowed(self, address: str, nick: str) -> bool:
        if self.dcc_ip_whitelist and address not in self.dcc_ip_whitelist:
            return False
        if self.dcc_ip_blacklist and address in self.dcc_ip_blacklist:
            return False
        if self.dcc_nick_whitelist and nick not in self.dcc_nick_whitelist:
            return False
        if self.dcc_nick_blacklist and nick in self.dcc_nick_blacklist:
            return False

        if self.dcc_max_connections and len(self._dcc_recv_procs) >= self.dcc_max_connections:
            self.logger.warning(
                f'Refused new DCC connection: maximum number of concurrent '
                f'connections ({self.dcc_max_connections}) reached'
            )

            return False

        return True

    def dcc_file_transfer(self, file: str, nick: str, bind_address: Optional[str] = None):
        conn: DCCConnection = self.dcc('chat')
        bind_address = (bind_address, 0) if bind_address else None
        conn.listen(bind_address)
        conn.passive = False
        self.connection.privmsg(
            nick,
            f'\x01DCC CHAT chat {ip_quad_to_numstr(conn.localaddress)} {conn.localport}\x01'
        )

        send_proc = self._dcc_send_procs[(conn.localaddress, conn.localport)] = multiprocessing.Process(
            target=self._process_dcc_send,
            kwargs={
                'connection': conn,
                'filename': file,
            }
        )

        send_proc.start()
        send_proc.join()

    @contextlib.contextmanager
    def event_queue(self, event_type: str) -> multiprocessing.Queue:
        q = self._pending_requests[event_type] = multiprocessing.Queue()
        try:
            yield q
        finally:
            q.close()
            self._pending_requests.pop(event_type, None)

    def start(self):
        self._dcc_processor = multiprocessing.Process(target=self._dcc_connect_processor)
        self._dcc_processor.start()

        for event_code in irc_event_codes.keys():
            handler = getattr(self, f'on_{event_code}', None)
            if not handler:
                self.reactor.add_global_handler(
                    event_code, lambda conn, evt: self._on_generic_event(conn, evt)
                )

        super().start()

    def stop(self, msg: Optional[str] = None):
        msg = msg or self.stop_message
        for addr, port in list(self._dcc_recv_procs.keys()) + list(self._dcc_send_procs.keys()):
            self._stop_dcc_connection(addr, port)

        if self._dcc_processor and self._dcc_processor.is_alive():
            self._dcc_processor.terminate()
        self._dcc_processor = None

        super().disconnect(msg=msg)
