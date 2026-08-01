import logging
import re
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
        bs = self.config.device_id[:16]

        return {
            b'id': self.config.device_id.encode('utf-8'),
            b'fn': self.config.device_name.encode('utf-8'),
            b'md': self.config.model_name.encode('utf-8'),
            b've': b'05',
            b'ic': b'/setup/icon.png',
            b'ca': str(self.config.capabilities).encode('utf-8'),
            b'st': st.encode('utf-8'),
            b'rs': rs.encode('utf-8'),
            b'bs': bs.encode('utf-8'),
            b'nf': b'1',
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

        safe_name = re.sub(r'[^a-zA-Z0-9-]', '-', self.config.device_name).strip('-')
        return ServiceInfo(
            type_='_googlecast._tcp.local.',
            name=f'{self.config.device_name}._googlecast._tcp.local.',
            addresses=addresses,
            port=self.config.port,
            properties=self._build_txt(state),
            server=f'{safe_name}.local.',
        )

    def start(self, state):
        try:
            self._info = self._build_info(state)
            self._zeroconf = Zeroconf()
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
