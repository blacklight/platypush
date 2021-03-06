import os
import requests
from typing import Optional

from platypush.message import Message
from platypush.message.response import Response
from platypush.utils import set_timeout, clear_timeout

from . import test_dir

# Default configuration folder for tests
conf_dir = os.path.join(test_dir, 'etc')

# Default configuration file for tests
config_file = os.path.join(conf_dir, 'config_test.yaml')

# Default request timeout in seconds
request_timeout = 10

# Default test user
test_user = 'platypush'

# Default test password
test_pass = 'test'

# Base URL
base_url = None


def set_base_url(url: str):
    global base_url
    base_url = url


class TimeoutException(RuntimeError):
    """
    Exception raised in case of timeout.
    """
    def __init__(self, msg: str = 'Timeout'):
        self.msg = msg


def send_request(action: str, timeout: Optional[float] = None, args: Optional[dict] = None,
                 parse_json: bool = True, authenticate: bool = True, **kwargs):
    if not timeout:
        timeout = request_timeout
    if not args:
        args = {}

    auth = (test_user, test_pass) if authenticate else kwargs.pop('auth', ())
    set_timeout(seconds=timeout, on_timeout=on_timeout('Receiver response timed out'))
    response = requests.post(
        '{}/execute'.format(base_url),
        auth=auth,
        json={
            'type': 'request',
            'action': action,
            'args': args,
        }, **kwargs
    )

    clear_timeout()

    if parse_json:
        response = parse_response(response)
    return response


def register_user(username: Optional[str] = None, password: Optional[str] = None):
    if not username:
        username = test_user
        password = test_pass

    set_timeout(seconds=request_timeout, on_timeout=on_timeout('User registration response timed out'))
    response = requests.post('{base_url}/register?redirect={base_url}/'.format(base_url=base_url), data={
        'username': username,
        'password': password,
        'confirm_password': password,
    })

    clear_timeout()
    return response


def on_timeout(msg):
    def _f(): raise TimeoutException(msg)
    return _f


def parse_response(response):
    response = Message.build(response.json())
    assert isinstance(response, Response), 'Expected Response type, got {}'.format(response.__class__.__name__)
    return response
