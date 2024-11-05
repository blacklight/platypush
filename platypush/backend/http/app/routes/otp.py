from typing import List, Optional

from flask import Blueprint, jsonify, request

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import UserAuthStatus, authenticate
from platypush.backend.http.utils import HttpUtils
from platypush.exceptions.user import (
    InvalidCredentialsException,
    InvalidOtpCodeException,
    UserException,
)
from platypush.config import Config
from platypush.context import get_plugin
from platypush.user import UserManager

otp = Blueprint('otp', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    otp,
]


def _get_otp_and_qrcode():
    otp = get_plugin('otp')  # pylint: disable=redefined-outer-name
    qrcode = get_plugin('qrcode')
    assert (
        otp and qrcode
    ), 'The otp and/or qrcode plugins are not available in your installation'

    return otp, qrcode


def _get_username():
    user = HttpUtils.current_user()
    if not user:
        raise InvalidCredentialsException('Invalid user session')

    return str(user.username)


def _get_otp_uri_and_qrcode(username: str, otp_secret: Optional[str] = None):
    if not otp_secret:
        return None, None

    otp, qrcode = _get_otp_and_qrcode()  # pylint: disable=redefined-outer-name
    otp_uri = (
        otp.provision_time_otp(
            name=username,
            secret=otp_secret,
            issuer=f'platypush@{Config.get_device_id()}',
        ).output
        if otp_secret
        else None
    )

    otp_qrcode = (
        qrcode.generate(content=otp_uri, format='png').output.get('data')
        if otp_uri
        else None
    )

    return otp_uri, otp_qrcode


def _verify_code(code: str, otp_secret: str) -> bool:
    otp, _ = _get_otp_and_qrcode()  # pylint: disable=redefined-outer-name
    return otp.verify_time_otp(otp=code, secret=otp_secret).output


def _dump_response(
    username: str,
    otp_secret: Optional[str] = None,
    backup_codes: Optional[List[str]] = None,
):
    otp_uri, otp_qrcode = _get_otp_uri_and_qrcode(username, otp_secret)
    return jsonify(
        {
            'username': username,
            'otp_secret': otp_secret,
            'otp_uri': otp_uri,
            'qrcode': otp_qrcode,
            'backup_codes': backup_codes or [],
        }
    )


def _get_otp():
    username = _get_username()
    user_manager = UserManager()
    otp_secret = user_manager.get_otp_secret(username)
    return _dump_response(
        username=username,
        otp_secret=otp_secret,
    )


def _authenticate_user(username: str, password: Optional[str]):
    assert password, 'The password field is required when setting up OTP'
    user, auth_status = UserManager().authenticate_user(  # type: ignore
        username, password, skip_2fa=True, with_status=True
    )

    if not user:
        raise InvalidCredentialsException(auth_status.value[2])


def _post_otp():
    body = request.json
    assert body, 'Invalid request body'

    username = _get_username()
    dry_run = body.get('dry_run', False)
    otp_secret = body.get('otp_secret')

    if not dry_run:
        _authenticate_user(username, body.get('password'))

        if otp_secret:
            code = body.get('code')
            assert code, 'The code field is required when setting up OTP'

            if not _verify_code(code, otp_secret):
                raise InvalidOtpCodeException()

    user_manager = UserManager()
    user_otp, backup_codes = user_manager.enable_otp(
        username=username,
        otp_secret=otp_secret,
        dry_run=dry_run,
    )

    return _dump_response(
        username=username,
        otp_secret=str(user_otp.otp_secret),
        backup_codes=backup_codes,
    )


def _delete_otp():
    body = request.json
    assert body, 'Invalid request body'

    username = _get_username()
    _authenticate_user(username, body.get('password'))

    user_manager = UserManager()
    user_manager.disable_otp(username)
    return jsonify({'status': 'ok'})


@otp.route('/otp/config', methods=['GET', 'POST', 'DELETE'])
@authenticate()
def otp_route():
    """
    :return: The user's current MFA/OTP configuration:

        .. code-block:: json

            {
                "username": "testuser",
                "otp_secret": "JBSA6ZUZ5DPEK7YV",
                "otp_uri": "otpauth://totp/testuser?secret=JBSA6ZUZ5DPEK7YV&issuer=platypush@localhost",
                "qrcode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAABwklEQVR4nO3dMW7CQBAF0",
                "backup_codes": [
                    "1A2B3C4D5E",
                    "6F7G8H9I0J",
                    "KLMNOPQRST",
                    "UVWXYZ1234",
                    "567890ABCD",
                    "EFGHIJKLMN",
                    "OPQRSTUVWX",
                    "YZ12345678",
                    "90ABCDEF12",
                    "34567890AB"
                ]
            }

    """
    try:
        if request.method.lower() == 'get':
            return _get_otp()

        if request.method.lower() == 'post':
            return _post_otp()

        if request.method.lower() == 'delete':
            return _delete_otp()

        return jsonify({'error': 'Method not allowed'}), 405
    except AssertionError as e:
        return jsonify({'error': str(e)}), 400
    except InvalidCredentialsException:
        return UserAuthStatus.INVALID_CREDENTIALS.to_response()
    except InvalidOtpCodeException:
        return UserAuthStatus.INVALID_OTP_CODE.to_response()
    except UserException as e:
        return jsonify({'error': e.__class__.__name__, 'message': str(e)}), 401
    except Exception as e:
        HttpUtils.log.error(f'Error while processing OTP request: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@otp.route('/otp/refresh-codes', methods=['POST'])
def refresh_codes():
    """
    :return: A new set of backup codes for the user.
    """
    username = _get_username()
    user_manager = UserManager()
    otp_secret = user_manager.get_otp_secret(username)
    if not otp_secret:
        return jsonify({'error': 'OTP not configured for the user'}), 400

    backup_codes = user_manager.refresh_user_backup_codes(username)
    return jsonify({'backup_codes': backup_codes})


# vim:sw=4:ts=4:et:
