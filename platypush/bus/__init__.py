import logging
import threading
import time

from queue import Queue

from platypush.config import Config
from platypush.message.event import StopEvent

logger = logging.getLogger('platypush:bus')


class Bus(object):
    """ Main local bus where the daemon will listen for new messages """

    _MSG_EXPIRY_TIMEOUT = 60.0  # Consider a message on the bus as expired after one minute without being picked up

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

        self.post(evt)

    def _msg_executor(self, msg):
        def executor():
            try:
                self.on_message(msg)
            except Exception as e:
                logger.error('Error on processing message {}'.format(msg))
                logger.exception(e)

        return executor

    def poll(self):
        """
        Reads messages from the bus until either stop event message or KeyboardInterrupt
        """

        if not self.on_message:
            logger.warning('No message handlers installed, cannot poll')
            return

        stop = False
        while not stop:
            msg = self.get()
            timestamp = msg.timestamp if hasattr(msg, 'timestamp') else msg.get('timestamp')
            if timestamp and time.time() - timestamp > self._MSG_EXPIRY_TIMEOUT:
                logger.debug('{} seconds old message on the bus expired, ignoring it: {}'.
                             format(int(time.time()-msg.timestamp), msg))
                continue

            threading.Thread(target=self._msg_executor(msg)).start()

            if isinstance(msg, StopEvent) and msg.targets_me():
                logger.info('Received STOP event on the bus')
                stop = True


# vim:sw=4:ts=4:et:
