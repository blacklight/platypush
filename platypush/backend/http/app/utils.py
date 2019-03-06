import importlib
import json
import logging
import os
import sys

from functools import wraps
from flask import request, Response
from redis import Redis

# NOTE: The HTTP service will *only* work on top of a Redis bus. The default
# internal bus service won't work as the web server will run in a different process.
from platypush.bus.redis import RedisBus

from platypush.config import Config
from platypush.message import Message
from platypush.message.request import Request
from platypush.utils import get_redis_queue_name_by_message, get_ip_or_hostname

_bus = None
_logger = None


def bus():
    global _bus
    if _bus is None:
        _bus = RedisBus()
    return _bus

def logger():
    global _logger
    if not _logger:
        log_args = {
            'level': logging.INFO,
            'format': '%(asctime)-15s|%(levelname)5s|%(name)s|%(message)s',
        }

        level = (Config.get('backend.http') or {}).get('logging') or \
            (Config.get('logging') or {}).get('level')
        filename = (Config.get('backend.http') or {}).get('filename')

        if level:
            log_args['level'] = getattr(logging, level.upper()) \
                if isinstance(level, str) else level
        if filename:
            log_args['filename'] = filename

        logging.basicConfig(**log_args)
        _logger = logging.getLogger('platyweb')

    return _logger

def get_message_response(msg):
    redis = Redis(**bus().redis_args)
    response = redis.blpop(get_redis_queue_name_by_message(msg), timeout=60)
    if response and len(response) > 1:
        response = Message.build(response[1])
    else:
        response = None

    return response

def get_http_port():
    from platypush.backend.http import HttpBackend
    http_conf = Config.get('backend.http')
    return http_conf.get('port', HttpBackend._DEFAULT_HTTP_PORT)

def get_websocket_port():
    from platypush.backend.http import HttpBackend
    http_conf = Config.get('backend.http')
    return http_conf.get('websocket_port', HttpBackend._DEFAULT_WEBSOCKET_PORT)

def send_message(msg):
    msg = Message.build(msg)

    if isinstance(msg, Request):
        msg.origin = 'http'

    if Config.get('token'):
        msg.token = Config.get('token')

    bus().post(msg)

    if isinstance(msg, Request):
        response = get_message_response(msg)
        logger().debug('Processing response on the HTTP backend: {}'.
                       format(response))

        return response

def send_request(action, **kwargs):
    msg = {
        'type': 'request',
        'action': action
    }

    if kwargs:
        msg['args'] = kwargs

    return send_message(msg)

def authenticate():
    return Response('Authentication required', 401,
                    {'WWW-Authenticate': 'Basic realm="Login required"'})

def authentication_ok(req):
    token = Config.get('token')
    if not token:
        return True

    user_token = None

    # Check if
    if 'X-Token' in req.headers:
        user_token = req.headers['X-Token']
    elif req.authorization:
        # TODO support for user check
        user_token = req.authorization.password
    elif 'token' in req.args:
        user_token = req.args.get('token')
    else:
        try:
            args = json.loads(req.data.decode('utf-8'))
            user_token = args.get('token')
        except:
            pass

    if user_token == token:
        return True

    return False

def get_routes():
    routes_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'routes')
    routes = []
    base_module = '.'.join(__name__.split('.')[:-1])

    for path, dirs, files in os.walk(routes_dir):
        for f in files:
            if f.endswith('.py'):
                mod_name = '.'.join(
                    (base_module + '.' + os.path.join(path, f).replace(
                        os.path.dirname(__file__), '')[1:] \
                        .replace(os.sep, '.')).split('.') \
                    [:(-2 if f == '__init__.py' else -1)])

                try:
                    mod = importlib.import_module(mod_name)
                    if hasattr(mod, '__routes__'):
                        routes.extend(mod.__routes__)
                except Exception as e:
                    logger().warning('Could not import routes from {}/{}: {}: {}'.
                                     format(path, f, type(e), str(e)))

    return routes


def get_local_base_url():
    http_conf = Config.get('backend.http') or {}
    return '{proto}://localhost:{port}'.format(
        proto=('https' if http_conf.get('ssl_cert') else 'http'),
        port=get_http_port())

def get_remote_base_url():
    http_conf = Config.get('backend.http') or {}
    return '{proto}://{host}:{port}'.format(
        proto=('https' if http_conf.get('ssl_cert') else 'http'),
        host=get_ip_or_hostname(), port=get_http_port())


def authenticate_user(route):
    @wraps(route)
    def authenticated_route(*args, **kwargs):
        if not authentication_ok(request): return authenticate()
        return route(*args, **kwargs)
    return authenticated_route


# vim:sw=4:ts=4:et:
