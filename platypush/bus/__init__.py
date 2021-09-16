import logging
import threading
import time

from queue import Queue, Empty
from typing import Callable, Type

from platypush.message.event import Event

logger = logging.getLogger('platypush:bus')


class Bus(object):
    """ Main local bus where the daemon will listen for new messages """

    _MSG_EXPIRY_TIMEOUT = 60.0  # Consider a message on the bus as expired after one minute without being picked up

    def __init__(self, on_message=None):
        self.bus = Queue()
        self.on_message = on_message
        self.thread_id = threading.get_ident()
        self.event_handlers = {}
        self._should_stop = threading.Event()

    def post(self, msg):
        """ Sends a message to the bus """
        self.bus.put(msg)

    def get(self):
        """ Reads one message from the bus """
        try:
            return self.bus.get(timeout=0.1)
        except Empty:
            return

    def stop(self):
        self._should_stop.set()

    def _msg_executor(self, msg):
        def event_handler(event: Event, handler: Callable[[Event], None]):
            logger.info('Triggering event handler {}'.format(handler.__name__))
            handler(event)

        def executor():
            if isinstance(msg, Event):
                if type(msg) in self.event_handlers:
                    handlers = self.event_handlers[type(msg)]
                else:
                    handlers = {*[hndl for event_type, hndl in self.event_handlers.items()
                                  if isinstance(msg, event_type)]}

                for hndl in handlers:
                    threading.Thread(target=event_handler, args=(msg, hndl))

            try:
                self.on_message(msg)
            except Exception as e:
                logger.error('Error on processing message {}'.format(msg))
                logger.exception(e)

        return executor

    def should_stop(self):
        return self._should_stop.is_set()

    def poll(self):
        """
        Reads messages from the bus until either stop event message or KeyboardInterrupt
        """
        if not self.on_message:
            logger.warning('No message handlers installed, cannot poll')
            return

        while not self.should_stop():
            msg = self.get()
            if msg is None:
                continue

            timestamp = msg.timestamp if hasattr(msg, 'timestamp') else msg.get('timestamp')
            if timestamp and time.time() - timestamp > self._MSG_EXPIRY_TIMEOUT:
                logger.debug('{} seconds old message on the bus expired, ignoring it: {}'.
                             format(int(time.time()-msg.timestamp), msg))
                continue

            threading.Thread(target=self._msg_executor(msg)).start()

        logger.info('Bus service stopped')

    def register_handler(self, event_type: Type[Event], handler: Callable[[Event], None]) -> Callable[[], None]:
        """
        Register an event handler to the bus.

        :param event_type: Event type to subscribe (event inheritance also works).
        :param handler: Event handler - a function that takes an Event object as parameter.
        :return: A function that can be called to remove the handler (no parameters required).
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = set()

        self.event_handlers[event_type].add(handler)

        def unregister():
            self.unregister_handler(event_type, handler)

        return unregister

    def unregister_handler(self, event_type: Type[Event], handler: Callable[[Event], None]) -> None:
        """
        Remove an event handler.

        :param event_type: Event type.
        :param handler: Existing event handler.
        """
        if event_type not in self.event_handlers:
            return

        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)

        if len(self.event_handlers[event_type]) == 0:
            del self.event_handlers[event_type]


# vim:sw=4:ts=4:et:
