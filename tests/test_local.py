from .context import platypush, config_file, TestTimeoutException

import logging
import os
import sys
import time
import unittest

from threading import Thread

from platypush import Daemon
from platypush.config import Config
from platypush.pusher import Pusher
from platypush.utils import set_timeout, clear_timeout

class TestLocal(unittest.TestCase):
    """ Tests the full flow on a local backend by executing a command through
        the shell.exec plugin and getting the output """

    timeout = 5

    def setUp(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        backends = Config.get_backends()
        self.assertTrue('local' in backends)

        try: os.remove(Config.get_backends()['local']['request_fifo'])
        except FileNotFoundError as e: pass

        try: os.remove(Config.get_backends()['local']['response_fifo'])
        except FileNotFoundError as e: pass


    def test_local_shell_exec_flow(self):
        self.start_sender()
        self.start_receiver()

    def on_response(self):
        def _f(response):
            logging.info("Received response: {}".format(response))
            clear_timeout()
            self.assertEqual(response.output.strip(), 'ping')
        return _f

    def on_timeout(self, msg):
        def _f(): raise TestTimeoutException(msg)
        return _f

    def start_sender(self):
        def _run_sender():
            pusher = Pusher(config_file=config_file, backend='local',
                            on_response=self.on_response())

            logging.info('Sending request')
            pusher.push(target=Config.get('device_id'), action='shell.exec',
                        cmd='echo ping', timeout=None)


        # Start the sender thread and wait for a response
        set_timeout(seconds=self.timeout,
                    on_timeout=self.on_timeout('Receiver response timed out'))

        self.sender = Thread(target=_run_sender)
        self.sender.start()

    def start_receiver(self):
        set_timeout(seconds=self.timeout,
                    on_timeout=self.on_timeout('Sender request timed out'))

        self.receiver = Daemon(config_file=config_file, requests_to_process=1)
        self.receiver.start()

        time.sleep(1)


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:

