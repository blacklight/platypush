from threading import RLock
from typing import Optional

from platypush.config import Config
from platypush.context import get_backend, get_plugin

_app_tunnel_lock = RLock()
_app_tunnel_url: Optional[str] = None


def _get_http_port() -> int:
    http = None
    if Config.get('backend.http'):
        http = get_backend('http')

    assert http, 'The http backend is required in order to subscribe to notifications'
    return http.port


def get_or_create_ngrok_tunnel() -> str:
    """
    This method creates an ngrok tunnel for the local web application,
    useful to register public HTTPS callback URLs on the fly from plugins
    and backends.
    """
    global _app_tunnel_url
    with _app_tunnel_lock:
        if _app_tunnel_url:
            return _app_tunnel_url

        local_port = _get_http_port()

        ngrok = None
        if Config.get('ngrok'):
            ngrok = get_plugin('ngrok')

        assert ngrok, 'The ngrok plugin is required in order to subscribe to notifications'
        tunnel_response = ngrok.create_tunnel(
            resource=local_port,
            protocol='http',
            bind_tls=True,
        ).output

        _app_tunnel_url = tunnel_response.get('url')
        assert _app_tunnel_url, 'Unable to create an ngrok tunnel'
        return _app_tunnel_url
