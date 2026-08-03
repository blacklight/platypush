import logging
import os
import platform
import random
import socket
import struct
import threading
import uuid as uuid_mod
from email.utils import formatdate
from typing import Optional

from platypush.plugins.media._chromecast_receiver._constants import (
    DIAL_SSDP_MCAST_ADDR,
    DIAL_SSDP_PORT,
    DIAL_ST_DIAL,
    DIAL_ELIGIBLE_ST,
    DIAL_SSDP_MX_MAX,
    DIAL_SSDP_RECV_BUF,
)

logger = logging.getLogger(__name__)


class SsdpResponder:
    """
    IPv4 UDP multicast SSDP responder.

    Listens on 239.255.255.250:1900 for M-SEARCH packets and replies
    with a unicast HTTP/1.1 200 OK when the search target matches DIAL.

    IPv4 only. IPv6 (MLD) is out of scope for the first release.
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config:
            ChromecastReceiverConfig with a populated .dial sub-config.
        """
        self._config = config
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._device_uuid = str(uuid_mod.UUID(hex=self._config.device_id))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Open the SSDP socket and start the listener thread."""
        try:
            self._sock = self._create_socket()
        except OSError as e:
            logger.warning(
                'Could not open SSDP socket on port %d: %s. '
                'DIAL discovery will be unavailable.',
                DIAL_SSDP_PORT,
                e,
            )
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._listen_loop,
            name='DialSsdpResponder',
            daemon=True,
        )
        self._thread.start()
        logger.info(
            'SSDP responder started on %s:%d',
            DIAL_SSDP_MCAST_ADDR,
            DIAL_SSDP_PORT,
        )

    def stop(self):
        """Signal the listener to stop and close the socket."""
        self._stop_event.set()
        if self._sock:
            try:
                self._send_byebye()
            except Exception as e:
                logger.debug('Could not send ssdp:byebye: %s', e)
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.debug('SSDP responder stopped')

    # ------------------------------------------------------------------
    # Socket setup
    # ------------------------------------------------------------------

    def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, 'SO_REUSEPORT'):
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass

        sock.bind(('', DIAL_SSDP_PORT))

        interfaces = self._config.dial.ssdp_interfaces or [self._config.host]
        joined_any = False
        for iface_ip in interfaces:
            try:
                socket.inet_aton(iface_ip)
            except OSError:
                try:
                    addrinfo = socket.getaddrinfo(
                        iface_ip, None, socket.AF_INET, socket.SOCK_DGRAM
                    )
                    resolved = (addrinfo[0][4][0]) if addrinfo else None
                    if not resolved:
                        logger.warning(
                            'Could not resolve SSDP interface %s, skipping', iface_ip
                        )
                        continue
                    iface_ip = resolved
                except Exception:
                    logger.warning(
                        'Could not resolve SSDP interface %s, skipping', iface_ip
                    )
                    continue

            try:
                mreq = struct.pack(
                    '4s4s',
                    socket.inet_aton(DIAL_SSDP_MCAST_ADDR),
                    socket.inet_aton(iface_ip),
                )
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                logger.debug('Joined SSDP multicast on interface %s', iface_ip)
                joined_any = True
            except OSError as e:
                logger.warning('Could not join SSDP multicast on %s: %s', iface_ip, e)

        if not joined_any:
            sock.close()
            raise OSError('No SSDP multicast interface joined')

        sock.settimeout(1.0)
        return sock

    # ------------------------------------------------------------------
    # Listener loop
    # ------------------------------------------------------------------

    def _listen_loop(self):
        while not self._stop_event.is_set():
            if not self._sock:
                break

            try:
                data, addr = self._sock.recvfrom(DIAL_SSDP_RECV_BUF)
            except socket.timeout:
                continue
            except OSError:
                break

            try:
                self._handle_packet(data, addr)
            except Exception as e:
                logger.debug('Error handling SSDP packet from %s: %s', addr, e)

    def _handle_packet(self, data: bytes, addr: tuple):
        src_ip, src_port = addr[0], addr[1]

        if not self._config.is_client_allowed(src_ip):
            logger.debug('SSDP: ignoring disallowed source %s', src_ip)
            return

        try:
            text = data.decode('utf-8', errors='replace')
        except Exception:
            return

        headers = self._parse_headers(text)

        first_line = text.split('\r\n', 1)[0].strip().upper()
        if not first_line.startswith('M-SEARCH'):
            return

        man = headers.get('man', '').strip('"').strip().lower()
        if man != 'ssdp:discover':
            return

        st = headers.get('st', '').strip().lower()
        if st not in DIAL_ELIGIBLE_ST:
            return

        if src_ip in (DIAL_SSDP_MCAST_ADDR, '255.255.255.255'):
            return

        try:
            mx = min(int(headers.get('mx', '1')), DIAL_SSDP_MX_MAX)
        except ValueError:
            mx = 1
        delay = random.uniform(0, max(0, mx))
        if self._stop_event.wait(delay):
            return

        self._send_response(src_ip, src_port)

    def _send_response(self, dst_ip: str, dst_port: int):
        from platypush.plugins.media._chromecast_receiver._config import (
            get_http_port,
            get_http_scheme,
        )

        http_port = get_http_port()
        host = self._config.dial_advertise_host
        max_age = self._config.dial.ssdp_max_age
        scheme = get_http_scheme()
        location = f'{scheme}://{host}:{http_port}/device.xml'

        try:
            u = os.uname()
            os_info = f'{u.sysname}/{u.release}'
        except AttributeError:
            os_info = f'{platform.system()}/{platform.release()}'

        response = (
            'HTTP/1.1 200 OK\r\n'
            f'CACHE-CONTROL: max-age={max_age}\r\n'
            f'DATE: {formatdate(usegmt=True)}\r\n'
            'EXT:\r\n'
            f'LOCATION: {location}\r\n'
            f'SERVER: {os_info} UPnP/1.0 Platypush/1.0\r\n'
            f'ST: {DIAL_ST_DIAL}\r\n'
            f'USN: uuid:{self._device_uuid}::{DIAL_ST_DIAL}\r\n'
            '\r\n'
        )

        try:
            if not self._sock:
                raise OSError('No SSDP socket')

            self._sock.sendto(response.encode('utf-8'), (dst_ip, dst_port))
            logger.debug('SSDP response sent to %s:%d', dst_ip, dst_port)
        except OSError as e:
            logger.warning(
                'Could not send SSDP response to %s:%d: %s',
                dst_ip,
                dst_port,
                e,
            )

    def _send_byebye(self):
        notify = (
            'NOTIFY * HTTP/1.1\r\n'
            f'HOST: {DIAL_SSDP_MCAST_ADDR}:{DIAL_SSDP_PORT}\r\n'
            'NTS: ssdp:byebye\r\n'
            f'NT: {DIAL_ST_DIAL}\r\n'
            f'USN: uuid:{self._device_uuid}::{DIAL_ST_DIAL}\r\n'
            '\r\n'
        )

        if not self._sock:
            raise OSError('No SSDP socket')

        self._sock.sendto(
            notify.encode('utf-8'),
            (DIAL_SSDP_MCAST_ADDR, DIAL_SSDP_PORT),
        )

    # ------------------------------------------------------------------
    # Header parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_headers(text: str) -> dict:
        """
        Parse HTTP-style headers from an SSDP packet.
        Keys are normalized to lowercase.
        """
        headers = {}
        lines = text.split('\r\n')
        for line in lines[1:]:
            if ':' in line:
                key, _, value = line.partition(':')
                headers[key.strip().lower()] = value.strip()
        return headers
