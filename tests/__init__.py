import abc
import logging
import os
import requests
import sys
import time
import unittest
from threading import Thread
from typing import Optional

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
test_dir = os.path.abspath(os.path.dirname(__file__))
conf_dir = os.path.join(test_dir, 'etc')
sys.path.insert(0, os.path.abspath(os.path.join(test_dir, '..')))

from platypush import Daemon, Config, Response
from platypush.message import Message
from platypush.utils import set_timeout, clear_timeout


class TimeoutException(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


class BaseTest(unittest.TestCase, abc.ABC):
    """
    Base class for Platypush tests.
    """

    app_start_timeout = 5
    request_timeout = 10
    config_file = None
    db_file = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app: Optional[Daemon] = None

    def setUp(self) -> None:
        self.start_daemon()

    def tearDown(self):
        try:
            self.stop_daemon()
        finally:
            if self.db_file and os.path.isfile(self.db_file):
                logging.info('Removing temporary db file {}'.format(self.db_file))
                os.unlink(self.db_file)

    def start_daemon(self):
        logging.info('Starting platypush service')
        self.app = Daemon(config_file=self.config_file)
        Thread(target=lambda: self.app.run()).start()
        logging.info('Sleeping {} seconds while waiting for the daemon to start up'.format(self.app_start_timeout))
        time.sleep(self.app_start_timeout)

    def stop_daemon(self):
        if self.app:
            logging.info('Stopping platypush service')
            self.app.stop_app()

    @staticmethod
    def parse_response(response):
        response = Message.build(response.json())
        assert isinstance(response, Response), 'Expected Response type, got {}'.format(response.__class__.__name__)
        return response

    @staticmethod
    def on_timeout(msg):
        def _f(): raise TimeoutException(msg)
        return _f


class BaseHttpTest(BaseTest, abc.ABC):
    """
    Base class for Platypush HTTP tests.
    """

    base_url = None
    test_user = 'platypush'
    test_pass = 'test'

    def setUp(self) -> None:
        Config.init(self.config_file)
        backends = Config.get_backends()
        self.assertTrue('http' in backends, 'Missing HTTP server configuration')
        self.base_url = 'http://localhost:{port}'.format(port=backends['http']['port'])
        self.db_file = Config.get('main.db')['engine'][len('sqlite:///'):]
        super().setUp()

    def register_user(self, username: Optional[str] = None, password: Optional[str] = None):
        if not username:
            username = self.test_user
            password = self.test_pass

        set_timeout(seconds=self.request_timeout, on_timeout=self.on_timeout('User registration response timed out'))
        response = requests.post('{base_url}/register?redirect={base_url}/'.format(base_url=self.base_url), data={
            'username': username,
            'password': password,
            'confirm_password': password,
        })

        clear_timeout()
        return response

    def send_request(self, action: str, timeout: Optional[float] = None, args: Optional[dict] = None,
                     parse_response: bool = True, authenticate: bool = True, **kwargs):
        if not timeout:
            timeout = self.request_timeout
        if not args:
            args = {}

        auth = (self.test_user, self.test_pass) if authenticate else kwargs.pop('auth', ())
        set_timeout(seconds=timeout, on_timeout=self.on_timeout('Receiver response timed out'))
        response = requests.post(
            '{}/execute'.format(self.base_url),
            auth=auth,
            json={
                'type': 'request',
                'action': action,
                'args': args,
            }, **kwargs
        )

        clear_timeout()

        if parse_response:
            response = self.parse_response(response)
        return response

    def assertEqual(self, first, second, msg=..., expected=None, actual=None) -> None:
        if expected is not None and actual is not None:
            if not msg:
                msg = ''
            msg += '\n\tExpected: {expected}\n\tActual: {actual}'.format(expected=expected, actual=actual)

        super().assertEqual(first, second, msg)
