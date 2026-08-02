import hashlib
import logging
import socket
from ipaddress import ip_address
from typing import Dict, Optional

from zeroconf import ServiceInfo, Zeroconf

logger = logging.getLogger(__name__)


class ChromecastReceiverAdvertiser:
    """
    mDNS/Zeroconf advertiser for the Cast receiver service.
    """

    def __init__(self, config):
        self.config = config
        self._zeroconf: Optional[Zeroconf] = None
        self._info: Optional[ServiceInfo] = None

    def _build_txt(self, state) -> Dict[bytes, bytes]:
        st = '1' if state.is_active else '0'
        rs = state.status_text or 'Ready To Cast'
        # Cast mDNS 'bs' is a 12-character lowercase hex token (Bluetooth-MAC
        # style). Truncate to 12 chars as required by the Cast protocol.
        bs = self.config.device_id[:12]

        # 'cd' (CloudDeviceID) is a 32-character uppercase hex string that
        # Cast SDK senders use for device identity/pairing. Real Chromecasts
        # derive this from cloud registration; we derive it deterministically
        # from the device_id so it's stable across restarts.
        cd = hashlib.md5(self.config.device_id.encode('utf-8')).hexdigest().upper()

        return {
            b'id': self.config.device_id.encode('utf-8'),
            b'cd': cd.encode('utf-8'),
            b'fn': self.config.device_name.encode('utf-8'),
            b'md': self.config.model_name.encode('utf-8'),
            b've': b'05',
            b'ic': b'/setup/icon.png',
            b'ca': str(self.config.capabilities).encode('utf-8'),
            b'st': st.encode('utf-8'),
            b'rs': rs.encode('utf-8'),
            b'bs': bs.encode('utf-8'),
            b'nf': b'1',
            b'rm': b'',
        }

    def _build_info(self, state) -> ServiceInfo:
        try:
            addr = socket.getaddrinfo(self.config.host, None, type=socket.SOCK_STREAM)[
                0
            ][4][0]
            ip_addr = addr
        except Exception:
            ip_addr = self.config.host

        try:
            ip = ip_address(ip_addr)
            if ip.version == 4:
                addresses = [socket.inet_aton(str(ip))]
            else:
                addresses = [socket.inet_pton(socket.AF_INET6, str(ip))]
        except Exception:
            addresses = [socket.inet_aton('0.0.0.0')]

        # The mDNS service instance name MUST be based on the device ID, not
        # the friendly name.  Using the friendly name (which may contain spaces
        # or non-ASCII characters) causes Android's Cast SDK to silently skip
        # the record during discovery.
        # Real Chromecasts use "<ModelPrefix>-<device_id>._googlecast._tcp.local."
        # The friendly name is conveyed exclusively via the "fn" TXT record.
        instance_name = f'Platypush-{self.config.device_id}._googlecast._tcp.local.'
        server_name = f'platypush-{self.config.device_id[:8]}.local.'
        return ServiceInfo(
            type_='_googlecast._tcp.local.',
            name=instance_name,
            addresses=addresses,
            port=self.config.port,
            properties=self._build_txt(state),
            server=server_name,
        )

    def _get_interfaces(self) -> list:
        """
        Return the list of network interfaces to advertise on — restricted to
        the interface(s) that own the configured host address so that Zeroconf
        does not try to multicast over VPN/WireGuard interfaces (which raise
        ENOTAVAIL / errno 126).
        """
        try:
            target = ip_address(
                socket.getaddrinfo(self.config.host, None, type=socket.SOCK_STREAM)[0][
                    4
                ][0]
            )
            return [str(target)]
        except Exception:
            return []

    def start(self, state):
        try:
            self._info = self._build_info(state)
            interfaces = self._get_interfaces()
            self._zeroconf = (
                Zeroconf(interfaces=interfaces) if interfaces else Zeroconf()
            )
            self._zeroconf.register_service(self._info)
            logger.info(
                'Chromecast receiver advertised as %s on port %d',
                self._info.name,
                self.config.port,
            )
        except Exception as e:
            logger.exception('Could not register Chromecast mDNS service: %s', e)

    def update(self, state):
        if not self._zeroconf or not self._info:
            return

        try:
            self._info = self._build_info(state)
            self._zeroconf.update_service(self._info)
        except Exception as e:
            logger.warning('Could not update Chromecast mDNS service: %s', e)

    def stop(self):
        if self._zeroconf and self._info:
            try:
                self._zeroconf.unregister_service(self._info)
            except Exception as e:
                logger.debug('Error unregistering mDNS service: %s', e)

        if self._zeroconf:
            try:
                self._zeroconf.close()
            except Exception as e:
                logger.debug('Error closing zeroconf: %s', e)

        self._zeroconf = None
        self._info = None
