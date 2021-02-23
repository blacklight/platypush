import os

from .context import config_file, TimeoutException

import logging
import requests
import sys
import time
import unittest

from threading import Thread, Event

from platypush import Daemon
from platypush.config import Config
from platypush.message import Message
from platypush.message.response import Response
from platypush.utils import set_timeout, clear_timeout


class TestHttp(unittest.TestCase):
    """ Tests the full flow of a request/response on the HTTP backend.
        Runs a remote command over HTTP via shell.exec plugin and gets the output """

    timeout = 10
    sleep_secs = 5
    db_file = '/tmp/platypush-tests.db'
    test_user = 'platypush'
    test_pass = 'test'
    base_url = 'http://localhost:8123'
    expected_registration_redirect = '{base_url}/register?redirect={base_url}/execute'.format(base_url=base_url)
    expected_login_redirect = '{base_url}/login?redirect={base_url}/execute'.format(base_url=base_url)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = None
        self._app_started = Event()

    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        backends = Config.get_backends()
        self.assertTrue('http' in backends, 'Missing HTTP server configuration')

        self.start_daemon()
        logging.info('Sleeping {} seconds while waiting for the daemon to start up'.format(self.sleep_secs))
        time.sleep(self.sleep_secs)

    def test_http_flow(self):
        # An /execute request performed before any user is registered should redirect to the registration page.
        response = self.send_request()
        self.assertEqual(self.expected_registration_redirect, response.url,
                         'No users registered, but the application did not redirect us to the registration page')

        # Emulate a first user registration through form and get the session_token.
        response = self.register_user()
        self.assertGreater(len(response.history), 0, 'Redirect missing from the history')
        self.assertTrue('session_token' in response.history[0].cookies, 'No session_token returned upon registration')
        self.assertEqual('{base_url}/'.format(base_url=self.base_url), response.url,
                         'The registration form did not redirect to the main panel')

        # After a first user has been registered any unauthenticated call to /execute should redirect to /login.
        response = self.send_request()
        self.assertEqual(self.expected_login_redirect, response.url,
                         'An unauthenticated request after user registration should result in a login redirect')

        # A request authenticated with user/pass should succeed.
        response = self.parse_response(self.send_request(auth=(self.test_user, self.test_pass)))
        self.assertEqual(response.__class__, Response, 'The request did not return a proper Response object')
        self.assertEqual(response.output.strip(), 'ping', 'The request did not return the expected output')

        # A request with the wrong user/pass should fail.
        response = self.send_request(auth=('wrong', 'wrong'))
        self.assertEqual(self.expected_login_redirect, response.url, 'A request with wrong credentials should fail')

    def start_daemon(self):
        self.app = Daemon(config_file=config_file)
        Thread(target=lambda: self.app.run()).start()

    def stop_daemon(self):
        if self.app:
            self.app.stop_app()

    @staticmethod
    def on_timeout(msg):
        def _f(): raise TimeoutException(msg)

        return _f

    def send_request(self, **kwargs):
        set_timeout(seconds=self.timeout, on_timeout=self.on_timeout('Receiver response timed out'))
        response = requests.post(
            '{}/execute'.format(self.base_url),
            json={
                'type': 'request',
                'target': Config.get('device_id'),
                'action': 'shell.exec',
                'args': {'cmd': 'echo ping'}
            }, **kwargs
        )

        clear_timeout()
        return response

    def register_user(self):
        set_timeout(seconds=self.timeout, on_timeout=self.on_timeout('User registration response timed out'))
        response = requests.post('{base_url}/register?redirect={base_url}/'.format(base_url=self.base_url), data={
            'username': self.test_user,
            'password': self.test_pass,
            'confirm_password': self.test_pass,
        })

        clear_timeout()
        return response

    @staticmethod
    def parse_response(response):
        return Message.build(response.json())

    def tearDown(self):
        try:
            self.stop_daemon()
        finally:
            if os.path.isfile(self.db_file):
                os.unlink(self.db_file)


if __name__ == '__main__':
    unittest.main()


# vim:sw=4:ts=4:et:
