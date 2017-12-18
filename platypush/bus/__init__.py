import os
import sys
import signal
import logging

from queue import Queue

class Bus(object):
    """ Main local bus where the daemon will listen for new messages """

    """ Number of seconds to wait for any pending threads
    before the process returns to the OS """
    _kill_sec_timeout = 5

    def __init__(self, on_msg=None):
        self.bus = Queue()
        self.on_msg = on_msg

    def post(self, msg):
        """ Sends a message to the bus """
        self.bus.put(msg)

    def get(self):
        """ Reads one message from the bus """
        return self.bus.get()

    def loop_forever(self):
        """ Reads messages from the bus until KeyboardInterrupt """
        def _on_stop_timeout(signum, frame):
            logging.warn('Stopping all the active threads after waiting for ' +
                        '{} seconds'.format(self._kill_sec_timeout))
            os._exit(1)

        if not self.on_msg: return

        while True:
            try:
                self.on_msg(self.get())
            except KeyboardInterrupt:
                logging.info('Received keyboard interrupt ' +
                             '- terminating application')

                signal.signal(signal.SIGALRM, _on_stop_timeout)
                signal.alarm(self._kill_sec_timeout)
                sys.exit(0)

# vim:sw=4:ts=4:et:

