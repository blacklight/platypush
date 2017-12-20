import os
import sys
import signal
import logging

from enum import Enum
from queue import Queue

from platypush.message.event import Event, StopEvent

class Bus(object):
    """ Main local bus where the daemon will listen for new messages """

    def __init__(self, on_message=None):
        self.bus = Queue()
        self.on_message = on_message

    def post(self, msg):
        """ Sends a message to the bus """
        self.bus.put(msg)

    def get(self):
        """ Reads one message from the bus """
        return self.bus.get()

    def poll(self):
        """
        Reads messages from the bus until either stop event message or KeyboardInterrupt
        """

        if not self.on_message:
            logging.warning('No message handlers installed, cannot poll')
            return

        stop=False
        while not stop:
            msg = self.get()
            self.on_message(msg)

            if isinstance(msg, StopEvent) and msg.targets_me():
                logging.info('Received STOP event')
                stop=True


# vim:sw=4:ts=4:et:

