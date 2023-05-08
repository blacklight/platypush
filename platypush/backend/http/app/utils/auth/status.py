from collections import namedtuple
from enum import Enum


StatusValue = namedtuple('StatusValue', ['code', 'message'])


class AuthStatus(Enum):
    """
    Models the status of the authentication.
    """

    OK = StatusValue(200, 'OK')
    UNAUTHORIZED = StatusValue(401, 'Unauthorized')
    NO_USERS = StatusValue(412, 'Please create a user first')

    def to_dict(self):
        return {
            'code': self.value[0],
            'message': self.value[1],
        }
