from .context import platypush, config_file, TestTimeoutException

import json
import logging
import requests
import sys
import time
import unittest

from threading import Thread

from platypush import Daemon
from platypush.config import Config
from platypush.message import Message
from platypush.message.response import Response
from platypush.utils import set_timeout, clear_timeout

class TestHttp(unittest.TestCase):
    """ Tests the full flow of a request/response on the HTTP backend.
        Runs a remote command over HTTP via shell.exec plugin and gets the output """

    timeout = 5

    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        backends = Config.get_backends()
        self.assertTrue('http' in backends)

    def test_request_exec_flow(self):
        self.start_daemon()
        time.sleep(2)
        self.send_request()

    def start_daemon(self):
        def _f():
            self.receiver = Daemon(config_file=config_file, requests_to_process=1)
            self.receiver.start()

        Thread(target=_f).start()

    def on_timeout(self, msg):
        def _f(): raise TestTimeoutException(msg)
        return _f

    def send_request(self):
        set_timeout(seconds=self.timeout,
                    on_timeout=self.on_timeout('Receiver response timed out'))

        response = requests.post(
            u'http://localhost:8123/execute',
            json  = {
                'type': 'request',
                'target': Config.get('device_id'),
                'action': 'shell.exec',
                'args': { 'cmd':'echo ping' }
            }
        )

        clear_timeout()

        response = Message.build(response.json())
        self.assertTrue(isinstance(response, Response))
        self.assertEqual(response.output.strip(), 'ping')
        self.receiver.stop_app()


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:

