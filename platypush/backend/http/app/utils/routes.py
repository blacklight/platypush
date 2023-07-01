import importlib
import inspect
import os
import pkgutil

from platypush.backend import Backend
from platypush.config import Config
from platypush.utils import get_ip_or_hostname

from .logger import logger


def get_http_port():
    from platypush.backend.http import HttpBackend

    http_conf = Config.get('backend.http') or {}
    return http_conf.get('port', HttpBackend._DEFAULT_HTTP_PORT)


def get_routes():
    base_pkg = '.'.join([Backend.__module__, 'http', 'app', 'routes'])
    base_dir = os.path.join(
        os.path.dirname(inspect.getfile(Backend)), 'http', 'app', 'routes'
    )
    routes = []

    for _, mod_name, _ in pkgutil.walk_packages([base_dir], prefix=base_pkg + '.'):
        try:
            module = importlib.import_module(mod_name)
            if hasattr(module, '__routes__'):
                routes.extend(module.__routes__)
        except Exception as e:
            logger().warning('Could not import module %s: %s', mod_name, str(e))
            continue

    return routes


def get_local_base_url():
    http_conf = Config.get('backend.http') or {}
    bind_address = http_conf.get('bind_address')
    if not bind_address or bind_address == '0.0.0.0':
        bind_address = 'localhost'

    return '{proto}://{host}:{port}'.format(
        proto=('https' if http_conf.get('ssl_cert') else 'http'),
        host=bind_address,
        port=get_http_port(),
    )


def get_remote_base_url():
    http_conf = Config.get('backend.http') or {}
    return '{proto}://{host}:{port}'.format(
        proto=('https' if http_conf.get('ssl_cert') else 'http'),
        host=get_ip_or_hostname(),
        port=get_http_port(),
    )
