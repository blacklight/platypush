import datetime
import json
import logging

from flask import Blueprint, request, abort, jsonify

from platypush.backend.http.app.utils import authenticate
from platypush.backend.http.app.utils.auth import (
    UserAuthStatus,
    authenticate_session_with_csrf,
    current_user,
    get_current_user_or_auth_status,
)
from platypush.exceptions.user import (
    InvalidCredentialsException,
    InvalidOtpCodeException,
    MissingOtpCodeException,
    TokenNameExistsException,
    UserException,
)
from platypush.user import User, UserManager
from platypush.utils import utcnow

auth = Blueprint('auth', __name__)
log = logging.getLogger(__name__)

# Declare routes list
__routes__ = [
    auth,
]


def _dump_session(session, redirect_page='/'):
    return jsonify(
        {
            'status': 'ok',
            'user_id': session.user_id,
            'session_token': session.session_token,
            'csrf_token': session.csrf_token,
            'expires_at': session.expires_at,
            'redirect': redirect_page,
        }
    )


def _jwt_auth():
    try:
        payload = json.loads(request.get_data(as_text=True))
        username, password = payload['username'], payload['password']
    except Exception:
        log.warning('Invalid payload passed to the auth endpoint')
        abort(400)

    expiry_days = payload.get('expiry_days')
    expires_at = None
    if expiry_days:
        expires_at = datetime.datetime.now() + datetime.timedelta(days=expiry_days)

    code = payload.get('code')
    user_manager = UserManager()

    try:
        return jsonify(
            {
                'token': user_manager.generate_jwt_token(
                    username=username,
                    password=password,
                    expires_at=expires_at,
                    code=code,
                ),
            }
        )
    except MissingOtpCodeException:
        return UserAuthStatus.MISSING_OTP_CODE.to_response()
    except InvalidOtpCodeException:
        return UserAuthStatus.INVALID_OTP_CODE.to_response()
    except InvalidCredentialsException:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()
    except UserException as e:
        abort(401, str(e))


def _session_auth():
    user_manager = UserManager()
    session_token = request.cookies.get('session_token')
    redirect_page = request.args.get('redirect') or '/'

    if session_token:
        user, session = user_manager.authenticate_user_session(session_token)[:2]
        if user and session:
            return _dump_session(session, redirect_page)

    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        code = request.form.get('code')
        remember = request.form.get('remember')
        expires = utcnow() + datetime.timedelta(days=365) if remember else None
        session, status = user_manager.create_user_session(  # type: ignore
            username=username,
            password=password,
            code=code,
            expires_at=expires,
            with_status=True,
        )

        if session:
            return _dump_session(session, redirect_page)

        if status:
            auth_status = UserAuthStatus.by_status(status)
            if not (auth_status):
                raise AssertionError
            return auth_status.to_response()

    return UserAuthStatus.INVALID_CREDENTIALS.to_response()


def _create_token():
    payload = {}
    try:
        payload = json.loads(request.get_data(as_text=True))
    except json.JSONDecodeError:
        pass

    username = payload.get('username')
    password = payload.get('password')
    code = payload.get('code')
    name = payload.get('name')
    expiry_days = payload.get('expiry_days')
    user_manager = UserManager()

    # Credential mode: authenticate with the username/password/OTP supplied
    # in the JSON payload. Two-factor authentication is enforced when enabled.
    if username and password:
        user, status = user_manager.authenticate_user(
            username, password, code=code, with_status=True
        )
        if not isinstance(user, User):
            auth_status = UserAuthStatus.by_status(status)
            if auth_status:
                return auth_status.to_response()
            return UserAuthStatus.INVALID_CREDENTIALS.to_response()
    elif not username and not password:
        # Session mode: the browser's session cookie authenticates the user and
        # the X-CSRF-Token header proves the request came from the Platypush UI.
        response = authenticate_session_with_csrf(request)
        if not isinstance(response, User):
            return response.to_response()

        user = response
    else:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()

    expires_at = None
    if expiry_days:
        expires_at = datetime.datetime.now() + datetime.timedelta(days=expiry_days)

    try:
        token = user_manager.generate_api_token(
            username=str(user.username), name=name, expires_at=expires_at
        )
        return jsonify({'token': token})
    except TokenNameExistsException:
        return UserAuthStatus.TOKEN_NAME_EXISTS.to_response()
    except UserException:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()


def _delete_token():
    try:
        payload = json.loads(request.get_data(as_text=True))
        token = payload.get('token')
        if not (token):
            raise AssertionError
    except (AssertionError, json.JSONDecodeError):
        return UserAuthStatus.INVALID_TOKEN.to_response()

    user_manager = UserManager()

    try:
        token = payload.get('token')
        if not token:
            return UserAuthStatus.INVALID_TOKEN.to_response()

        ret = user_manager.delete_api_token(token)
        if not ret:
            return UserAuthStatus.INVALID_TOKEN.to_response()

        return jsonify({'status': 'ok'})
    except UserException:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()


def _register_route():
    """Registration endpoint"""
    user_manager = UserManager()
    session_token = request.cookies.get('session_token')
    redirect_page = request.args.get('redirect') or '/'

    if session_token:
        user, session = user_manager.authenticate_user_session(session_token)[:2]
        if user and session:
            return _dump_session(session, redirect_page)

    if user_manager.get_user_count() > 0:
        return UserAuthStatus.REGISTRATION_DISABLED.to_response()

    if not request.form:
        return UserAuthStatus.MISSING_USERNAME.to_response()

    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    remember = request.form.get('remember')

    if not username:
        return UserAuthStatus.MISSING_USERNAME.to_response()
    if not password:
        return UserAuthStatus.MISSING_PASSWORD.to_response()
    if password != confirm_password:
        return UserAuthStatus.PASSWORD_MISMATCH.to_response()

    user_manager.create_user(username=username, password=password)
    session, status = user_manager.create_user_session(  # type: ignore
        username=username,
        password=password,
        expires_at=(utcnow() + datetime.timedelta(days=365) if remember else None),
        with_status=True,
    )

    if session:
        return _dump_session(session, redirect_page)

    if status:
        return status.to_response()  # type: ignore

    return UserAuthStatus.INVALID_CREDENTIALS.to_response()


def _auth_get():
    """
    Get the current authentication status of the user session.
    """
    user_manager = UserManager()
    session_token = request.cookies.get('session_token')
    redirect_page = request.args.get('redirect') or '/'
    user, session, status = user_manager.authenticate_user_session(  # type: ignore
        session_token, with_status=True
    )

    if user and session:
        return _dump_session(session, redirect_page)

    response = get_current_user_or_auth_status(request)
    if isinstance(response, User):
        user = response
        return jsonify(
            {'status': 'ok', 'user_id': user.user_id, 'username': user.username}
        )

    if response:
        status = response

    if status:
        if not isinstance(status, UserAuthStatus):
            status = UserAuthStatus.by_status(status)
        if not status:
            status = UserAuthStatus.INVALID_CREDENTIALS
        return status.to_response()

    return UserAuthStatus.INVALID_CREDENTIALS.to_response()


def _auth_post():
    """
    Authenticate the user session.
    """
    auth_type = request.args.get('type') or 'token'

    if auth_type == 'token':
        return _create_token()

    if auth_type == 'jwt':
        return _jwt_auth()

    if auth_type == 'register':
        return _register_route()

    if auth_type == 'login':
        return _session_auth()

    return UserAuthStatus.INVALID_AUTH_TYPE.to_response()


def _auth_delete():
    """
    Logout/invalidate a token or the current user session.
    """
    # Delete the specified API token if it's passed on the JSON payload
    token = None
    try:
        payload = json.loads(request.get_data(as_text=True))
        token = payload.get('token')
    except json.JSONDecodeError:
        pass

    if token:
        return _delete_token()

    user_manager = UserManager()
    session_token = request.cookies.get('session_token')
    redirect_page = request.args.get('redirect') or '/'

    if session_token:
        user, session = user_manager.authenticate_user_session(session_token)[:2]
        if user and session:
            user_manager.delete_user_session(session_token)
            return jsonify({'status': 'ok', 'redirect': redirect_page})

    return UserAuthStatus.INVALID_SESSION.to_response()


def _tokens_get():
    user = current_user()
    if not user:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()

    tokens = UserManager().get_api_tokens(username=str(user.username))
    return jsonify(
        {
            'tokens': [
                {
                    'id': t.id,
                    'name': t.name,
                    'created_at': t.created_at,
                    'expires_at': t.expires_at,
                }
                for t in tokens
            ]
        }
    )


def _tokens_delete():
    args = {}

    try:
        payload = json.loads(request.get_data(as_text=True))
        token = payload.get('token')
        if token:
            args['token'] = token
        else:
            token_id = payload.get('token_id')
            if token_id:
                args['token_id'] = token_id

        if not (args):
            raise AssertionError('No token or token_id specified')
    except (AssertionError, json.JSONDecodeError):
        return UserAuthStatus.INVALID_TOKEN.to_response()

    user_manager = UserManager()
    user = current_user()
    if not user:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()

    args['username'] = str(user.username)

    try:
        user_manager.delete_api_token(**args)
        return jsonify({'status': 'ok'})
    except AssertionError as e:
        return (
            jsonify({'status': 'error', 'error': 'bad_request', 'message': str(e)}),
            400,
        )
    except UserException:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()
    except Exception as e:
        log.error('Token deletion error', exc_info=e)

    return UserAuthStatus.UNKNOWN_ERROR.to_response()


@auth.route('/auth', methods=['GET', 'POST', 'DELETE'])
def auth_endpoint():
    """
    Authentication endpoint.

    ``POST /auth?type=token`` can generate a new API token in two modes:

    * **Credential mode:** the caller provides the following JSON fields:

        .. code-block:: json

            {
                "username": "USERNAME",
                "password": "PASSWORD",
                "code": "2FA_CODE (required if the account has OTP/2FA enabled)",
                "name": "Token name",
                "expiry_days": "The generated token should be valid for these many days"
            }

      Two-factor authentication is enforced when enabled.

    * **Session mode:** the request is authenticated by the browser's
      ``session_token`` cookie and the JSON body only contains token metadata:

        .. code-block:: json

            {
                "name": "Token name",
                "expiry_days": "The generated token should be valid for these many days"
            }

      The ``X-CSRF-Token`` header must be set to the per-session CSRF token
      returned when the session was created or queried via ``GET /auth``.

    ``expiry_days`` is optional, and if omitted or set to zero the token will
    be valid indefinitely.

    The token can then be used to authenticate API calls to ``/execute`` by
    setting the ``Authorization: Bearer <TOKEN_HERE>`` header upon HTTP calls.

    :return: Return structure:

        .. code-block:: json

            {
                "token": "<generated token here>"
            }
    """
    if request.method == 'GET':
        return _auth_get()

    if request.method == 'POST':
        return _auth_post()

    if request.method == 'DELETE':
        return _auth_delete()

    return UserAuthStatus.INVALID_METHOD.to_response()


@auth.route('/tokens', methods=['GET', 'DELETE'])
@authenticate()
def tokens_route():
    """
    :return: The list of API tokens created by the logged in user.
        Note that this endpoint is only accessible by authenticated users
        and it won't return the clear-text token values, as those aren't
        stored in the database anyway.
    """
    if request.method == 'GET':
        return _tokens_get()

    if request.method == 'DELETE':
        return _tokens_delete()

    return UserAuthStatus.INVALID_METHOD.to_response()


# vim:sw=4:ts=4:et:
