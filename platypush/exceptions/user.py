from typing import Optional, Union

from platypush.exceptions import PlatypushException


class UserException(PlatypushException):
    """
    Base class for all user exceptions.
    """

    def __init__(self, *args, user: Optional[Union[str, int]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user


class NoUserException(UserException):
    """
    Exception raised when no user is found.
    """


class AuthenticationException(UserException):
    """
    Authentication error exception.
    """

    def __init__(self, error='Unauthorized', *args, **kwargs):
        super().__init__(error, *args, **kwargs)


class InvalidTokenException(AuthenticationException):
    """
    Exception raised in case of wrong user token.
    """

    def __init__(self, error='Invalid user token', *args, **kwargs):
        super().__init__(error, *args, **kwargs)


class InvalidCredentialsException(AuthenticationException):
    """
    Exception raised in case of wrong user token.
    """

    def __init__(self, error='Invalid credentials', *args, **kwargs):
        super().__init__(error, *args, **kwargs)


class InvalidTokenException(InvalidTokenException):
    """
    Exception raised in case of wrong/invalid API token.
    """

    def __init__(self, error='Invalid API token', *args, **kwargs):
        super().__init__(error, *args, **kwargs)


class InvalidJWTTokenException(InvalidTokenException):
    """
    Exception raised in case of wrong/invalid JWT token.
    """

    def __init__(self, error='Invalid JWT token', *args, **kwargs):
        super().__init__(error, *args, **kwargs)


class InvalidOtpCodeException(AuthenticationException):
    """
    Exception raised in case of wrong OTP code.
    """

    def __init__(self, error='Invalid OTP code', *args, **kwargs):
        super().__init__(error, *args, **kwargs)


class OtpRecordAlreadyExistsException(UserException):
    """
    Exception raised in case of an OTP record already existing for a user.
    """

    def __init__(
        self, *args, error='An OTP record already exists for this user', **kwargs
    ):
        super().__init__(*args, error, **kwargs)
