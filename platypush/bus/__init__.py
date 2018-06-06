import os
import sys
import signal
import logging
import threading

from enum import Enum
from queue import Queue

from platypush.config import Config
from platypush.message.event import Event, StopEvent

logger = logging.getLogger(__name__)


class Bus(object):
    """ Main local bus where the daemon will listen for new messages """

    def __init__(self, on_message=None):
        self.bus = Queue()
        self.on_message = on_message
        self.thread_id = threading.get_ident()

    def post(self, msg):
        """ Sends a message to the bus """
        self.bus.put(msg)

    def get(self):
        """ Reads one message from the bus """
        return self.bus.get()

    def stop(self):
        """ Stops the bus by sending a STOP event """
        evt = StopEvent(target=Config.get('device_id'),
                        origin=Config.get('device_id'),
                        thread_id=self.thread_id)

        self.bus.put(evt)

    def poll(self):
        """
        Reads messages from the bus until either stop event message or KeyboardInterrupt
        """

        if not self.on_message:
            logger.warning('No message handlers installed, cannot poll')
            return

        stop=False
        while not stop:
            msg = self.get()
            self.on_message(msg)

            if isinstance(msg, StopEvent) and msg.targets_me():
                logger.info('Received STOP event on the bus')
                stop=True


# vim:sw=4:ts=4:et:

