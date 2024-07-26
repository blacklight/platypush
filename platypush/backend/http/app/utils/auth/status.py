from collections import namedtuple
from enum import Enum

from flask import jsonify

from platypush.user import AuthenticationStatus

StatusValue = namedtuple('StatusValue', ['code', 'error', 'message'])


class UserAuthStatus(Enum):
    """
    Models the status of the authentication.
    """

    OK = StatusValue(200, AuthenticationStatus.OK, 'OK')
    INVALID_AUTH_TYPE = StatusValue(
        400, AuthenticationStatus.INVALID_AUTH_TYPE, 'Invalid authentication type'
    )
    INVALID_CREDENTIALS = StatusValue(
        401, AuthenticationStatus.INVALID_CREDENTIALS, 'Invalid credentials'
    )
    INVALID_JWT_TOKEN = StatusValue(
        401, AuthenticationStatus.INVALID_JWT_TOKEN, 'Invalid JWT token'
    )
    INVALID_OTP_CODE = StatusValue(
        401, AuthenticationStatus.INVALID_OTP_CODE, 'Invalid OTP code'
    )
    INVALID_METHOD = StatusValue(
        405, AuthenticationStatus.INVALID_METHOD, 'Invalid method'
    )
    MISSING_OTP_CODE = StatusValue(
        401, AuthenticationStatus.MISSING_OTP_CODE, 'Missing OTP code'
    )
    MISSING_PASSWORD = StatusValue(
        400, AuthenticationStatus.MISSING_PASSWORD, 'Missing password'
    )
    INVALID_SESSION = StatusValue(
        401, AuthenticationStatus.INVALID_CREDENTIALS, 'Invalid session'
    )
    INVALID_TOKEN = StatusValue(
        400, AuthenticationStatus.INVALID_JWT_TOKEN, 'Invalid token'
    )
    MISSING_USERNAME = StatusValue(
        400, AuthenticationStatus.MISSING_USERNAME, 'Missing username'
    )
    PASSWORD_MISMATCH = StatusValue(
        400, AuthenticationStatus.PASSWORD_MISMATCH, 'Password mismatch'
    )
    REGISTRATION_DISABLED = StatusValue(
        401, AuthenticationStatus.REGISTRATION_DISABLED, 'Registrations are disabled'
    )
    REGISTRATION_REQUIRED = StatusValue(
        412, AuthenticationStatus.REGISTRATION_REQUIRED, 'Please create a user first'
    )
    UNKNOWN_ERROR = StatusValue(
        500, AuthenticationStatus.UNKNOWN_ERROR, 'Unknown error'
    )

    def to_dict(self):
        return {
            'code': self.value[0],
            'error': self.value[1].name,
            'message': self.value[2],
        }

    def to_response(self):
        return jsonify(self.to_dict()), self.value[0]

    @staticmethod
    def by_status(status: AuthenticationStatus):
        for auth_status in UserAuthStatus:
            if auth_status.value[1] == status:
                return auth_status

        return None
