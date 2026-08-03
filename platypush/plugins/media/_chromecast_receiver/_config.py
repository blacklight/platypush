import ipaddress
import logging
import os
import re
import socket
import uuid
from dataclasses import dataclass, field
from typing import ClassVar, List, Optional, Union

from platypush.config import Config
from platypush.utils import get_ip_or_hostname

from ._constants import (
    DEFAULT_CAPABILITIES_AUDIO,
    DEFAULT_CAPABILITIES_AV,
    DEFAULT_DEVICE_NAME,
    DEFAULT_MANUFACTURER,
    DEFAULT_MODEL_NAME,
    DEFAULT_PORT,
    DEFAULT_STATUS_INTERVAL,
    PRIVATE_NETWORKS,
)

logger = logging.getLogger(__name__)


def _normalize_device_id(device_id: Optional[str]) -> str:
    """
    Normalize a device ID to a 32-character lowercase hexadecimal string.
    """
    if not device_id:
        return uuid.uuid4().hex

    # Remove dashes and convert to lowercase
    device_id = device_id.replace('-', '').lower()

    # If it's a valid UUID, return its hex form
    try:
        return uuid.UUID(device_id).hex
    except ValueError:
        pass

    if not re.fullmatch(r'[0-9a-f]+', device_id):
        raise ValueError(f'Invalid device_id; must be hexadecimal: {device_id}')

    if len(device_id) != 32:
        raise ValueError(f'Invalid device_id; must be 32 hex chars: {device_id}')

    return device_id


def _load_or_generate_device_id(workdir: str, device_id: Optional[str]) -> str:
    """
    Load a persisted device ID or generate and persist a new one.
    """
    device_id_file = os.path.join(workdir, 'chromecast_receiver', 'device_id')
    os.makedirs(os.path.dirname(device_id_file), exist_ok=True)

    if device_id:
        device_id = _normalize_device_id(device_id)
        with open(device_id_file, 'w') as f:
            f.write(device_id)
        return device_id

    if os.path.isfile(device_id_file):
        with open(device_id_file) as f:
            device_id = f.read().strip()
        if device_id:
            return _normalize_device_id(device_id)

    device_id = _normalize_device_id(None)
    with open(device_id_file, 'w') as f:
        f.write(device_id)
    return device_id


def get_http_port() -> int:
    """
    Return the configured HTTP backend port, defaulting to 8008.
    """
    http_conf = (Config.get_backends() or {}).get('http') or {}
    return int(http_conf.get('port', 8008))


def get_http_scheme() -> str:
    """
    Return ``"https"`` if the HTTP backend is configured with an SSL
    certificate, ``"http"`` otherwise. Used to build DIAL/SSDP URLs that
    correctly reflect whether the HTTP backend is served over TLS.
    """
    http_conf = (Config.get_backends() or {}).get('http') or {}
    return 'https' if http_conf.get('ssl_cert') else 'http'


def get_dial_state_path() -> str:
    """
    Return the path to the DIAL state JSON file written by DialService.
    """
    return os.path.join(Config.get_workdir(), 'chromecast_receiver', 'dial_state.json')


@dataclass
class DialConfig:
    """
    Parsed and normalized DIAL sub-configuration.

    Attributes
    ----------
    enabled:
        Whether the DIAL layer is active. Defaults to False (opt-in).
    ssdp_max_age:
        SSDP CACHE-CONTROL max-age in seconds.
    ssdp_interfaces:
        IP addresses (or resolvable hostnames) of interfaces to bind the
        SSDP multicast socket. Empty list means fall back to
        ChromecastReceiverConfig.host.
    advertise_host:
        Explicit host/IP to embed in SSDP LOCATION and Application-URL.
        If empty, falls back to ChromecastReceiverConfig.host.
    supported_apps:
        List of DIAL app IDs this device supports.
        Valid values: ``"Media"``, ``"YouTube"``.
        ``Media`` is the supported default for direct URL playback.
        ``YouTube`` is **experimental** — it has not been validated against
        a real YouTube DIAL sender and may not handle all sender payload
        variants.  Enable it only for testing.
        An empty list is replaced with ``["Media"]``; set ``enabled: false``
        to disable DIAL entirely.
    """

    enabled: bool = False
    ssdp_max_age: int = 1800
    ssdp_interfaces: List[str] = field(default_factory=list)
    advertise_host: str = ''
    supported_apps: List[str] = field(default_factory=lambda: ['Media'])

    _VALID_APPS: ClassVar[frozenset] = frozenset({'Media', 'YouTube'})
    # Note: YouTube is experimental — it has not been validated against a real
    # DIAL sender.  Only enable it for testing.  See 01-PLAN.md for details.

    @classmethod
    def build(cls, raw: dict) -> 'DialConfig':
        if not raw:
            return cls()
        apps = [a for a in raw.get('supported_apps', ['Media']) if a in cls._VALID_APPS]
        return cls(
            enabled=bool(raw.get('enabled', False)),
            ssdp_max_age=int(raw.get('ssdp_max_age', 1800)),
            ssdp_interfaces=list(raw.get('ssdp_interfaces') or []),
            advertise_host=str(raw.get('advertise_host') or ''),
            supported_apps=apps or ['Media'],
        )


@dataclass
class ChromecastReceiverConfig:
    """
    Parsed and normalized Chromecast receiver configuration.
    """

    enabled: bool = False
    device_name: str = DEFAULT_DEVICE_NAME
    host: str = ''
    port: int = DEFAULT_PORT
    device_id: str = ''
    model_name: str = DEFAULT_MODEL_NAME
    manufacturer: str = DEFAULT_MANUFACTURER
    allowed_networks: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = field(
        default_factory=list
    )
    media_base_url: str = ''
    status_interval: float = DEFAULT_STATUS_INTERVAL
    capabilities: int = DEFAULT_CAPABILITIES_AV
    audio_only: bool = False
    dial: DialConfig = field(default_factory=DialConfig)

    @classmethod
    def build(
        cls,
        plugin,
        config: Optional[dict] = None,
    ) -> 'ChromecastReceiverConfig':
        """
        Build a :class:`ChromecastReceiverConfig` from a raw configuration
        dictionary and a :class:`MediaPlugin` instance.
        """
        config = config or {}
        from platypush.utils import get_plugin_name_by_class

        plugin_name = get_plugin_name_by_class(plugin.__class__)
        workdir = Config.get_workdir()

        device_name = (
            config.get('device_name') or f'{plugin_name} on {socket.gethostname()}'
        )
        host = config.get('host') or get_ip_or_hostname()
        port = int(config.get('port', DEFAULT_PORT))

        if port != DEFAULT_PORT:
            import logging

            logging.getLogger(__name__).warning(
                'Chromecast receiver port is set to %d; some sender apps may '
                'ignore mDNS and assume port 8009',
                port,
            )

        device_id = _load_or_generate_device_id(workdir, config.get('device_id'))

        allowed_networks = config.get('allowed_networks')
        if allowed_networks:
            networks = [ipaddress.ip_network(n) for n in allowed_networks]
        else:
            networks = [ipaddress.ip_network(n) for n in PRIVATE_NETWORKS]

        media_base_url = config.get('media_base_url') or ''

        audio_only = bool(config.get('audio_only', False))
        default_capabilities = (
            DEFAULT_CAPABILITIES_AUDIO if audio_only else DEFAULT_CAPABILITIES_AV
        )
        capabilities = int(
            config.get(
                'capabilities',
                config.get('ca', default_capabilities),
            )
        )

        dial = DialConfig.build(config.get('dial') or {})

        return cls(
            enabled=bool(config.get('enabled', False)),
            device_name=device_name,
            host=host,
            port=port,
            device_id=device_id,
            model_name=config.get('model_name', DEFAULT_MODEL_NAME),
            manufacturer=config.get('manufacturer', DEFAULT_MANUFACTURER),
            allowed_networks=networks,
            media_base_url=media_base_url,
            status_interval=float(
                config.get('status_interval', DEFAULT_STATUS_INTERVAL)
            ),
            capabilities=capabilities,
            audio_only=audio_only,
            dial=dial,
        )

    @property
    def dial_advertise_host(self) -> str:
        """
        Host/IP to embed in SSDP LOCATION and Application-URL headers.
        Priority: dial.advertise_host > self.host > get_ip_or_hostname().
        """
        if self.dial.advertise_host:
            return self.dial.advertise_host
        if self.host:
            return self.host
        fallback = get_ip_or_hostname()
        logger.warning(
            'dial.advertise_host falling back to %s; '
            'consider setting an explicit host or dial.advertise_host',
            fallback,
        )
        return fallback

    def is_client_allowed(self, ip: str) -> bool:
        """
        Check whether a client IP address is in the allowed networks.
        """
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return any(addr in network for network in self.allowed_networks)
