import ipaddress
import os
import re
import socket
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Union

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
        )

    def is_client_allowed(self, ip: str) -> bool:
        """
        Check whether a client IP address is in the allowed networks.
        """
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return any(addr in network for network in self.allowed_networks)
