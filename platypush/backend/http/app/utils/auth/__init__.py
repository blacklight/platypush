import base64
from functools import wraps
from typing import Optional, Union

from flask import request, redirect
from flask.wrappers import Response

from platypush.config import Config
from platypush.user import User, UserManager

from ..logger import logger
from .status import UserAuthStatus

user_manager = UserManager()


def get_arg(req, name: str) -> Optional[str]:
    # The Flask way
    if hasattr(req, 'args'):
        return req.args.get(name)

    # The Tornado way
    if hasattr(req, 'arguments'):
        arg = req.arguments.get(name)
        if arg:
            return arg[0].decode()

    return None


def get_cookie(req, name: str) -> Optional[str]:
    cookie = req.cookies.get(name)
    if not cookie:
        return None

    # The Flask way
    if isinstance(cookie, str):
        return cookie

    # The Tornado way
    return cookie.value


def authenticate_token(req) -> Optional[User]:
    global_token = Config.get('user.global_token')
    user_token = None

    if 'X-Token' in req.headers:
        user_token = req.headers['X-Token']
    elif 'Authorization' in req.headers and req.headers['Authorization'].startswith(
        'Bearer '
    ):
        user_token = req.headers['Authorization'][7:]
    else:
        user_token = get_arg(req, 'token')

    if not user_token:
        return None

    try:
        # Stantard API token authentication
        return user_manager.validate_api_token(user_token)
    except Exception as e:
        try:
            # Legacy JWT token authentication
            return user_manager.validate_jwt_token(user_token)
        except Exception as ee:
            logger().debug(
                'Invalid token. API token error: %s, JWT token error: %s', e, ee
            )

            # Legacy global token authentication.
            # The global token should be specified in the configuration file,
            # as a root parameter named `token`.
            if bool(global_token and user_token == global_token):
                return User(username='__token__', user_id=1)

            logger().info(e)


def authenticate_user_pass(req):
    # Flask populates request.authorization
    if hasattr(req, 'authorization'):
        if not req.authorization:
            return False

        username = req.authorization.username
        password = req.authorization.password

    # Otherwise, check the Authorization header
    elif 'Authorization' in req.headers and req.headers['Authorization'].startswith(
        'Basic '
    ):
        auth = req.headers['Authorization'][6:]
        try:
            auth = base64.b64decode(auth)
        except ValueError:
            pass

        username, password = auth.decode().split(':', maxsplit=1)
    else:
        return False

    return user_manager.authenticate_user(username, password)


def authenticate_session(req) -> Optional[User]:
    user = None

    # Check the X-Session-Token header
    user_session_token = req.headers.get('X-Session-Token')

    # Check the `session_token` query/body parameter
    if not user_session_token:
        user_session_token = get_arg(req, 'session_token')

    # Check the `session_token` cookie
    if not user_session_token:
        user_session_token = get_cookie(req, 'session_token')

    if user_session_token:
        user, _ = user_manager.authenticate_user_session(user_session_token)[:2]

    return user


def authenticate(
    redirect_page='',
    skip_auth_methods=None,
    json=False,
):
    """
    Authentication decorator for Flask routes.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_status = get_auth_status(
                request,
                skip_auth_methods=skip_auth_methods,
            )

            if auth_status == UserAuthStatus.OK:
                return f(*args, **kwargs)

            if json:
                return auth_status.to_response()

            if auth_status == UserAuthStatus.REGISTRATION_REQUIRED:
                return redirect(
                    f'/register?redirect={redirect_page or request.url}', 307
                )

            if auth_status == UserAuthStatus.INVALID_CREDENTIALS:
                return redirect(f'/login?redirect={redirect_page or request.url}', 307)

            return Response(
                'Authentication required',
                401,
                {'WWW-Authenticate': 'Basic realm="Login required"'},
            )

        return wrapper

    return decorator


# pylint: disable=too-many-return-statements
def get_current_user_or_auth_status(
    req, skip_auth_methods=None
) -> Union[User, UserAuthStatus]:
    """
    Returns the current user if authenticated, and the authentication status if
    ``with_status`` is True.
    """
    n_users = user_manager.get_user_count()
    skip_methods = skip_auth_methods or []

    # User/pass HTTP authentication
    http_auth_ok = True
    if n_users > 0 and 'http' not in skip_methods:
        response = authenticate_user_pass(req)
        if response:
            user = response[0] if isinstance(response, tuple) else response
            if user:
                return user

    # Token-based authentication
    token_auth_ok = True
    if 'token' not in skip_methods:
        user = authenticate_token(req)
        if user:
            return user

    # Session token based authentication
    session_auth_ok = True
    if n_users > 0 and 'session' not in skip_methods:
        user = authenticate_session(req)
        if user:
            return user

        return UserAuthStatus.INVALID_CREDENTIALS

    # At least a user should be created before accessing an authenticated resource
    if n_users == 0 and 'session' not in skip_methods:
        return UserAuthStatus.REGISTRATION_REQUIRED

    if (  # pylint: disable=too-many-boolean-expressions
        ('http' not in skip_methods and http_auth_ok)
        or ('token' not in skip_methods and token_auth_ok)
        or ('session' not in skip_methods and session_auth_ok)
    ):
        return UserAuthStatus.OK

    return UserAuthStatus.INVALID_CREDENTIALS


def get_auth_status(req, skip_auth_methods=None) -> UserAuthStatus:
    """
    Check against the available authentication methods (except those listed in
    ``skip_auth_methods``) if the user is properly authenticated.
    """
    ret = get_current_user_or_auth_status(req, skip_auth_methods=skip_auth_methods)
    return UserAuthStatus.OK if isinstance(ret, User) else ret


def current_user() -> Optional[User]:
    """
    Returns the current user if authenticated.
    """
    ret = get_current_user_or_auth_status(request)
    return ret if isinstance(ret, User) else None
