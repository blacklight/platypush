"""
Routes that emulate the Chromecast setup/eureka_info API.

Android cast selectors and pychromecast query ``/setup/eureka_info`` over HTTP
(port 8008) or HTTPS (port 8443) after mDNS discovery to determine the device
type and manufacturer.  Without this endpoint the device will not appear in the
cast selector.
"""

import ipaddress
import json
import logging
import socket
import uuid as uuid_mod

from flask import Blueprint, Response, request

from platypush.config import Config
from platypush.plugins.media._chromecast_receiver._config import (
    ChromecastReceiverConfig,
    _load_or_generate_device_id,
)
from platypush.plugins.media._chromecast_receiver._constants import (
    DEFAULT_CAPABILITIES_AUDIO,
    DEFAULT_CAPABILITIES_AV,
    DEFAULT_MANUFACTURER,
    DEFAULT_MODEL_NAME,
    DEFAULT_PORT,
    DEFAULT_STATUS_INTERVAL,
    PRIVATE_NETWORKS,
)
from platypush.utils import get_ip_or_hostname

setup = Blueprint('chromecast_setup', __name__)

__routes__ = [
    setup,
]

logger = logging.getLogger(__name__)


def _get_receiver_config():
    """
    Read the Chromecast receiver configuration directly from the Platypush
    config (no plugin instantiation required).

    This avoids calling ``get_plugin()`` which would hang in forked HTTP
    worker processes (plugins are registered after the HTTP backend forks).
    """
    plugins = Config.get_plugins()

    # Look for any media plugin with chromecast_receiver enabled
    for name, plugin_conf in plugins.items():
        if not name.startswith('media'):
            continue

        if not isinstance(plugin_conf, dict):
            continue

        receiver_conf = plugin_conf.get('chromecast_receiver')
        if not receiver_conf or not receiver_conf.get('enabled'):
            continue

        # Build config without needing a plugin instance — we just need
        # the plugin name for the default device_name fallback
        return _build_config_from_raw(name, receiver_conf)

    return None


def _build_config_from_raw(plugin_name: str, raw: dict) -> ChromecastReceiverConfig:
    """
    Build a ChromecastReceiverConfig from the raw config dict without
    requiring a plugin instance.
    """
    workdir = Config.get_workdir()

    device_name = raw.get('device_name') or f'{plugin_name} on {socket.gethostname()}'
    host = raw.get('host') or get_ip_or_hostname()
    port = int(raw.get('port', DEFAULT_PORT))
    device_id = _load_or_generate_device_id(workdir, raw.get('device_id'))

    allowed_networks = raw.get('allowed_networks')
    if allowed_networks:
        networks = [ipaddress.ip_network(n) for n in allowed_networks]
    else:
        networks = [ipaddress.ip_network(n) for n in PRIVATE_NETWORKS]

    audio_only = bool(raw.get('audio_only', False))
    default_capabilities = (
        DEFAULT_CAPABILITIES_AUDIO if audio_only else DEFAULT_CAPABILITIES_AV
    )
    capabilities = int(raw.get('capabilities', raw.get('ca', default_capabilities)))

    return ChromecastReceiverConfig(
        enabled=True,
        device_name=device_name,
        host=host,
        port=port,
        device_id=device_id,
        model_name=raw.get('model_name', DEFAULT_MODEL_NAME),
        manufacturer=raw.get('manufacturer', DEFAULT_MANUFACTURER),
        allowed_networks=networks,
        media_base_url=raw.get('media_base_url', ''),
        status_interval=float(raw.get('status_interval', DEFAULT_STATUS_INTERVAL)),
        capabilities=capabilities,
        audio_only=audio_only,
    )


@setup.route('/setup/eureka_info', methods=['GET'])
def eureka_info():
    """
    Emulate the Chromecast eureka_info endpoint.

    Query parameters:
        params: comma-separated list of sections to include
                (e.g. ``device_info,name``)
    """
    config = _get_receiver_config()
    if config is None:
        return Response(
            json.dumps({'error': 'Chromecast receiver not active'}),
            status=404,
            mimetype='application/json',
        )

    params = request.args.get('params', '')
    requested = {p.strip() for p in params.split(',') if p.strip()} if params else set()

    # Build the full response object
    device_uuid = uuid_mod.UUID(hex=config.device_id)
    ssdp_udn = str(device_uuid)

    full_response = {
        'name': config.device_name,
        'device_info': {
            'name': config.device_name,
            'model_name': config.model_name,
            'manufacturer': config.manufacturer,
            'ssdp_udn': ssdp_udn,
            'capabilities': {
                'display_supported': not config.audio_only,
                'multizone_supported': False,
            },
        },
    }

    # If specific params were requested, filter the response
    if requested:
        response = {}
        for key in requested:
            if key in full_response:
                response[key] = full_response[key]
        # Always include 'name' at top-level if device_info is requested
        if 'device_info' in requested and 'name' not in response:
            response['name'] = config.device_name
    else:
        response = full_response

    return Response(
        json.dumps(response),
        status=200,
        mimetype='application/json',
    )
