from typing import Optional, Union

from platypush.exceptions import PlatypushException


class UserException(PlatypushException):
    """
    Base class for all user exceptions.
    """
    def __init__(self, *args, user: Optional[Union[str, int]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user


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


class InvalidJWTTokenException(InvalidTokenException):
    """
    Exception raised in case of wrong/invalid JWT token.
    """
    def __init__(self, error='Invalid JWT token', *args, **kwargs):
        super().__init__(error, *args, **kwargs)
