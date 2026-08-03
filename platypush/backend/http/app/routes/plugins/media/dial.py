"""
DIAL REST API and device description routes.

Exposes:
    GET  /device.xml          UPnP device description + Application-URL header
    GET  /apps/<app_id>       DIAL app status XML
    POST /apps/<app_id>       DIAL app launch
    DELETE /apps/<app_id>/run DIAL app stop
"""

import ipaddress
import json
import logging
import math
import os
import socket
from typing import Optional
import urllib.parse
import uuid as uuid_mod
from email.utils import formatdate
from xml.etree.ElementTree import Element, SubElement, tostring

from flask import Blueprint, Response, request

from platypush.config import Config
from platypush.context import get_bus
from platypush.message import Message
from platypush.plugins.media._chromecast_receiver._config import (
    ChromecastReceiverConfig,
    DialConfig,
    _load_or_generate_device_id,
    get_dial_state_path,
    get_http_port,
    get_http_scheme,
)
from platypush.plugins.media._chromecast_receiver._constants import (
    DEFAULT_CAPABILITIES_AUDIO,
    DEFAULT_CAPABILITIES_AV,
    DEFAULT_MANUFACTURER,
    DEFAULT_MODEL_NAME,
    DEFAULT_PORT,
    DEFAULT_STATUS_INTERVAL,
    DIAL_LAUNCH_TIMEOUT,
    PRIVATE_NETWORKS,
)
from platypush.plugins.media._chromecast_receiver._dial._messages import (
    DialLaunchReply,
    DialLaunchRequest,
    DialStopReply,
    DialStopRequest,
)

from platypush.utils import get_ip_or_hostname, get_redis

logger = logging.getLogger(__name__)

dial = Blueprint('dial', __name__)

__routes__ = [dial]

# Worker-process cache for the parsed DIAL configuration.
# Invalidated when the main configuration file mtime or workdir changes.
_cached_cfg = None
_cached_cfg_key = None


def _get_config():
    """
    Return (ChromecastReceiverConfig, DialConfig) from static platypush config,
    or (None, None) if DIAL is not enabled.
    No plugin instantiation.
    """
    global _cached_cfg, _cached_cfg_key

    config_file = Config.get_file()
    try:
        mtime = (
            os.path.getmtime(config_file)
            if config_file and os.path.exists(config_file)
            else 0
        )
    except OSError:
        mtime = 0

    workdir = Config.get_workdir()

    plugins = Config.get_plugins() or {}
    for name, plugin_conf in plugins.items():
        if not name.startswith('media') or not isinstance(plugin_conf, dict):
            continue

        receiver_raw = plugin_conf.get('chromecast_receiver')
        if not receiver_raw or not receiver_raw.get('enabled'):
            continue

        dial_raw = receiver_raw.get('dial') or {}
        if not dial_raw.get('enabled'):
            continue

        cache_key = (
            mtime,
            workdir,
            name,
            json.dumps(receiver_raw, sort_keys=True, default=str),
        )
        if cache_key == _cached_cfg_key and _cached_cfg is not None:
            return _cached_cfg
        device_name = (
            receiver_raw.get('device_name') or f'{name} on {socket.gethostname()}'
        )
        host = receiver_raw.get('host') or get_ip_or_hostname()
        port = int(receiver_raw.get('port', DEFAULT_PORT))
        device_id = _load_or_generate_device_id(workdir, receiver_raw.get('device_id'))

        allowed_networks_raw = receiver_raw.get('allowed_networks')
        networks = (
            [ipaddress.ip_network(n) for n in allowed_networks_raw]
            if allowed_networks_raw
            else [ipaddress.ip_network(n) for n in PRIVATE_NETWORKS]
        )

        audio_only = bool(receiver_raw.get('audio_only', False))
        default_cap = (
            DEFAULT_CAPABILITIES_AUDIO if audio_only else DEFAULT_CAPABILITIES_AV
        )
        capabilities = int(
            receiver_raw.get('capabilities', receiver_raw.get('ca', default_cap))
        )

        receiver_cfg = ChromecastReceiverConfig(
            enabled=True,
            device_name=device_name,
            host=host,
            port=port,
            device_id=device_id,
            model_name=receiver_raw.get('model_name', DEFAULT_MODEL_NAME),
            manufacturer=receiver_raw.get('manufacturer', DEFAULT_MANUFACTURER),
            allowed_networks=networks,
            media_base_url=receiver_raw.get('media_base_url', ''),
            status_interval=float(
                receiver_raw.get('status_interval', DEFAULT_STATUS_INTERVAL)
            ),
            capabilities=capabilities,
            audio_only=audio_only,
            dial=DialConfig.build(dial_raw),
        )
        _cached_cfg = (receiver_cfg, receiver_cfg.dial)
        _cached_cfg_key = cache_key
        return _cached_cfg

    _cached_cfg = (None, None)
    _cached_cfg_key = (mtime, workdir, None, '')
    return _cached_cfg


def _authorized(receiver_cfg) -> bool:
    return receiver_cfg.is_client_allowed(request.remote_addr or '')


def _json_err(msg: str, status: int) -> Response:
    return Response(
        json.dumps({'error': msg}), status=status, mimetype='application/json'
    )


def _xml_response(
    xml_bytes: bytes, status: int = 200, extra_headers: Optional[dict] = None
) -> Response:
    headers = {
        'Content-Type': 'application/xml; charset=utf-8',
        'Date': formatdate(usegmt=True),
    }
    if extra_headers:
        headers.update(extra_headers)
    return Response(xml_bytes, status=status, headers=headers)


def _read_dial_state() -> dict:
    """
    Read the DIAL state JSON file written by DialService.
    Returns {'active_app': str|None, 'run_id': str|None}.
    """
    path = get_dial_state_path()
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {'active_app': None, 'run_id': None}


def _get_app_state(app_id: str) -> str:
    """Return 'running' or 'stopped' for *app_id*."""
    state = _read_dial_state()
    return 'running' if state.get('active_app') == app_id else 'stopped'


def _build_device_xml(cfg) -> bytes:
    device_uuid = str(uuid_mod.UUID(hex=cfg.device_id))
    root = Element('root', xmlns='urn:schemas-upnp-org:device-1-0')
    spec = SubElement(root, 'specVersion')
    SubElement(spec, 'major').text = '1'
    SubElement(spec, 'minor').text = '0'
    dev = SubElement(root, 'device')
    SubElement(dev, 'deviceType').text = 'urn:dial-multiscreen-org:device:dial:1'
    SubElement(dev, 'friendlyName').text = cfg.device_name
    SubElement(dev, 'manufacturer').text = cfg.manufacturer
    SubElement(dev, 'modelName').text = cfg.model_name
    SubElement(dev, 'UDN').text = f'uuid:{device_uuid}'
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root, encoding='unicode'
    ).encode('utf-8')


def _build_app_xml(app_id: str, state: str) -> bytes:
    svc = Element(
        'service',
        {
            'xmlns': 'urn:dial-multiscreen-org:schemas:dial',
            'dialVer': '2.1',
        },
    )
    SubElement(svc, 'name').text = app_id
    SubElement(svc, 'options', allowStop='true')
    SubElement(svc, 'state').text = state
    if state == 'running':
        SubElement(svc, 'link', rel='run', href='run')
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        svc, encoding='unicode'
    ).encode('utf-8')


def _dispatch_and_wait(request_cls, reply_cls, *, timeout: float = 5.0, **kwargs):
    """
    Post a DIAL request on the bus and wait for the matching reply.

    The reply is expected to be pushed onto a private Redis queue whose name
    is carried as ``reply_topic`` in the request.
    """
    timeout = timeout or DIAL_LAUNCH_TIMEOUT
    reply_topic = f'platypush/dial/reply/{uuid_mod.uuid4().hex}'
    request = request_cls(reply_topic=reply_topic, **kwargs)

    get_bus().post(request)

    try:
        redis = get_redis()
        response = redis.blpop(reply_topic, timeout=math.ceil(timeout) + 1)
    except Exception as e:
        logger.error('DIAL reply transport error: %s', e)
        raise RuntimeError(
            f'DIAL reply transport error for {reply_cls.__name__}'
        ) from e

    if not response:
        raise RuntimeError(f'Timeout ({timeout}s) waiting for {reply_cls.__name__}')

    try:
        reply = Message.build(response[1])
    except Exception as e:
        raise RuntimeError(f'Invalid DIAL reply: {e}') from e

    if not isinstance(reply, reply_cls):
        raise RuntimeError(f'Unexpected reply type: {type(reply)}')

    return reply


@dial.route('/device.xml', methods=['GET'])
def device_description():
    receiver_cfg, dial_cfg = _get_config()
    if not dial_cfg:
        return _json_err('DIAL not enabled', 404)
    if not (receiver_cfg and _authorized(receiver_cfg)):
        return _json_err('Forbidden', 403)

    http_port = get_http_port()
    host = receiver_cfg.dial_advertise_host
    scheme = get_http_scheme()
    app_url = f'{scheme}://{host}:{http_port}/apps/'

    xml_bytes = _build_device_xml(receiver_cfg)
    return _xml_response(xml_bytes, extra_headers={'Application-URL': app_url})


@dial.route('/apps/<app_id>', methods=['GET'])
def app_status(app_id: str):
    receiver_cfg, dial_cfg = _get_config()
    if not dial_cfg:
        return _json_err('DIAL not enabled', 404)
    if not _authorized(receiver_cfg):
        return _json_err('Forbidden', 403)
    if app_id not in dial_cfg.supported_apps:
        return _json_err(f'Unsupported app: {app_id}', 404)

    state = _get_app_state(app_id)
    return _xml_response(_build_app_xml(app_id, state))


@dial.route('/apps/<app_id>', methods=['POST'])
def app_launch(app_id: str):
    receiver_cfg, dial_cfg = _get_config()
    if not dial_cfg:
        return _json_err('DIAL not enabled', 404)
    if not _authorized(receiver_cfg):
        return _json_err('Forbidden', 403)
    if app_id not in dial_cfg.supported_apps:
        return _json_err(f'Unknown app: {app_id}', 404)

    content_type = request.content_type or ''
    if 'application/x-www-form-urlencoded' not in content_type:
        return _json_err('Unsupported Media Type', 415)

    raw_payload = request.get_data(as_text=True) or ''

    try:
        reply: DialLaunchReply = _dispatch_and_wait(  # type: ignore
            DialLaunchRequest,
            DialLaunchReply,
            app_id=app_id,
            raw_payload=raw_payload,
        )
    except RuntimeError as e:
        logger.error('DIAL launch dispatch error: %s', e)
        return _json_err('Internal server error', 500)

    if not reply.success:
        status = 400 if getattr(reply, 'client_error', False) else 500
        return _json_err(reply.error, status)

    http_port = get_http_port()
    host = receiver_cfg.dial_advertise_host
    scheme = get_http_scheme()
    safe_id = urllib.parse.quote(app_id, safe='')
    location = f'{scheme}://{host}:{http_port}/apps/{safe_id}/run'
    return Response('', status=201, headers={'Location': location})


@dial.route('/apps/<app_id>/run', methods=['DELETE'])
def app_stop(app_id: str):
    receiver_cfg, dial_cfg = _get_config()
    if not dial_cfg:
        return _json_err('DIAL not enabled', 404)
    if not _authorized(receiver_cfg):
        return _json_err('Forbidden', 403)
    if app_id not in dial_cfg.supported_apps:
        return _json_err(f'Unknown app: {app_id}', 404)

    if _get_app_state(app_id) != 'running':
        return _json_err(f'App {app_id} is not running', 404)

    try:
        reply: DialStopReply = _dispatch_and_wait(  # type: ignore
            DialStopRequest,
            DialStopReply,
            app_id=app_id,
        )
    except RuntimeError as e:
        logger.error('DIAL stop dispatch error: %s', e)
        return _json_err('Internal server error', 500)

    if not reply.success:
        status = 400 if getattr(reply, 'client_error', False) else 500
        return _json_err(reply.error, status)
    return Response('', status=200)
