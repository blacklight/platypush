import importlib
import logging
import os

from functools import wraps
from flask import abort, request, redirect, Response
from redis import Redis

# NOTE: The HTTP service will *only* work on top of a Redis bus. The default
# internal bus service won't work as the web server will run in a different process.
from platypush.bus.redis import RedisBus

from platypush.config import Config
from platypush.message import Message
from platypush.message.request import Request
from platypush.user import UserManager
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
        _logger = logging.getLogger('platypush:web')

    return _logger


def get_message_response(msg):
    redis = Redis(**bus().redis_args)
    response = redis.blpop(get_redis_queue_name_by_message(msg), timeout=60)
    if response and len(response) > 1:
        response = Message.build(response[1])
    else:
        response = None

    return response


# noinspection PyProtectedMember
def get_http_port():
    from platypush.backend.http import HttpBackend
    http_conf = Config.get('backend.http')
    return http_conf.get('port', HttpBackend._DEFAULT_HTTP_PORT)


# noinspection PyProtectedMember
def get_websocket_port():
    from platypush.backend.http import HttpBackend
    http_conf = Config.get('backend.http')
    return http_conf.get('websocket_port', HttpBackend._DEFAULT_WEBSOCKET_PORT)


def send_message(msg, wait_for_response=True):
    msg = Message.build(msg)

    if isinstance(msg, Request):
        msg.origin = 'http'

    if Config.get('token'):
        msg.token = Config.get('token')

    bus().post(msg)

    if isinstance(msg, Request) and wait_for_response:
        response = get_message_response(msg)
        logger().debug('Processing response on the HTTP backend: {}'.
                       format(response))

        return response


def send_request(action, wait_for_response=True, **kwargs):
    msg = {
        'type': 'request',
        'action': action
    }

    if kwargs:
        msg['args'] = kwargs

    return send_message(msg, wait_for_response=wait_for_response)


def _authenticate_token():
    token = Config.get('token')

    if 'X-Token' in request.headers:
        user_token = request.headers['X-Token']
    elif 'token' in request.args:
        user_token = request.args.get('token')
    else:
        return False

    return token and user_token == token


def _authenticate_http():
    user_manager = UserManager()

    if not request.authorization:
        return False

    username = request.authorization.username
    password = request.authorization.password
    return user_manager.authenticate_user(username, password)


def _authenticate_session():
    user_manager = UserManager()
    user_session_token = None
    user = None

    if 'X-Session-Token' in request.headers:
        user_session_token = request.headers['X-Session-Token']
    elif 'session_token' in request.args:
        user_session_token = request.args.get('session_token')
    elif 'session_token' in request.cookies:
        user_session_token = request.cookies.get('session_token')

    if user_session_token:
        user, session = user_manager.authenticate_user_session(user_session_token)

    return user is not None


def _authenticate_csrf_token():
    user_manager = UserManager()
    user_session_token = None

    if 'X-Session-Token' in request.headers:
        user_session_token = request.headers['X-Session-Token']
    elif 'session_token' in request.args:
        user_session_token = request.args.get('session_token')
    elif 'session_token' in request.cookies:
        user_session_token = request.cookies.get('session_token')

    if user_session_token:
        user, session = user_manager.authenticate_user_session(user_session_token)
    else:
        return False

    if user is None:
        return False

    return session.csrf_token is None or request.form.get('csrf_token') == session.csrf_token


def authenticate(redirect_page='', skip_auth_methods=None, check_csrf_token=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_manager = UserManager()
            n_users = user_manager.get_user_count()
            token = Config.get('token')
            skip_methods = skip_auth_methods or []

            # User/pass HTTP authentication
            http_auth_ok = True
            if n_users > 0 and 'http' not in skip_methods:
                http_auth_ok = _authenticate_http()
                if http_auth_ok:
                    return f(*args, **kwargs)

            # Token-based authentication
            token_auth_ok = True
            if token and 'token' not in skip_methods:
                token_auth_ok = _authenticate_token()
                if token_auth_ok:
                    return f(*args, **kwargs)

            # Session token based authentication
            session_auth_ok = True
            if n_users > 0 and 'session' not in skip_methods:
                session_auth_ok = _authenticate_session()
                if session_auth_ok:
                    return f(*args, **kwargs)

                return redirect('/login?redirect=' + (redirect_page or request.url), 307)

            # CSRF token check
            if check_csrf_token:
                csrf_check_ok = _authenticate_csrf_token()
                if not csrf_check_ok:
                    return abort(403, 'Invalid or missing csrf_token')

            if n_users == 0 and 'session' not in skip_methods:
                return redirect('/register?redirect=' + redirect_page, 307)

            if ('http' not in skip_methods and http_auth_ok) or \
                    ('token' not in skip_methods and token_auth_ok) or \
                    ('session' not in skip_methods and session_auth_ok):
                return f(*args, **kwargs)

            return Response('Authentication required', 401,
                            {'WWW-Authenticate': 'Basic realm="Login required"'})

        return wrapper

    return decorator


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
                        os.path.dirname(__file__), '')[1:].replace(os.sep, '.')).split('.')
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


# vim:sw=4:ts=4:et:
