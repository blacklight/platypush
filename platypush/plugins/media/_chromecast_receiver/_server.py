import logging
import socket
import ssl
import threading
from typing import Optional

from ._certificate import load_or_create_certificate
from ._session import CastSession

logger = logging.getLogger(__name__)


class ChromecastReceiverServer(threading.Thread):
    """
    TLS socket server for the Cast channel.
    """

    def __init__(self, service):
        super().__init__(name='ChromecastReceiverServer', daemon=True)
        self.service = service
        self.config = service.config
        self.state = service.state
        self.plugin = service.plugin
        self.should_stop = service.should_stop
        self._sock: Optional[socket.socket] = None
        self._ssl_context: Optional[ssl.SSLContext] = None

    def _init_ssl(self) -> ssl.SSLContext:
        cert_path, key_path = load_or_create_certificate(self.config.device_name)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.load_cert_chain(cert_path, key_path)
        return ctx

    def _create_socket(self) -> socket.socket:
        addr_info = socket.getaddrinfo(
            self.config.host, self.config.port, type=socket.SOCK_STREAM
        )
        if not addr_info:
            raise RuntimeError(
                f'Could not resolve {self.config.host}:{self.config.port}'
            )

        family = addr_info[0][0]
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def run(self):
        try:
            self._ssl_context = self._init_ssl()
            self._sock = self._create_socket()
            self._sock.bind((self.config.host, self.config.port))
            self._sock.listen(5)
        except Exception as e:
            logger.exception('Could not start Chromecast receiver server: %s', e)
            return

        logger.info(
            'Chromecast receiver listening on %s:%d',
            self.config.host,
            self.config.port,
        )

        while not self.should_stop.is_set():
            try:
                self._sock.settimeout(1.0)
                client_sock, address = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            client_ip = address[0]
            if not self.config.is_client_allowed(client_ip):
                logger.warning('Rejected Chromecast connection from %s', client_ip)
                try:
                    client_sock.close()
                except Exception:
                    pass
                continue

            try:
                secure_sock = self._ssl_context.wrap_socket(
                    client_sock, server_side=True
                )
            except ssl.SSLError as e:
                # Chromecast devices routinely probe the receiver with a
                # TCP connect followed by an immediate disconnect (no TLS
                # ClientHello).  These result in UNEXPECTED_EOF_WHILE_READING
                # and are harmless — log at DEBUG to reduce noise.
                logger.debug('TLS handshake failed for %s: %s', client_ip, e)
                try:
                    client_sock.close()
                except Exception:
                    pass
                continue
            except Exception as e:
                logger.warning('TLS handshake failed for %s: %s', client_ip, e)
                try:
                    client_sock.close()
                except Exception:
                    pass
                continue

            session = CastSession(self.service, secure_sock, address)
            self.service.sessions.append(session)
            session.start()

        self._close_socket()

    def _close_socket(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception as e:
                logger.debug('Error closing server socket: %s', e)
            finally:
                self._sock = None

    def stop(self):
        self._close_socket()
