import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from queue import Empty, Queue
from typing import Callable, Dict, Iterable, Optional, Type

from platypush.message import Message
from platypush.utils.executor import get_bus_executor

logger = logging.getLogger('platypush:bus')


@dataclass
class MessageHandler:
    """
    Wrapper for a message callback handler.
    """

    msg_type: Type[Message]
    callback: Callable[[Message], None]
    kwargs: dict = field(default_factory=dict)

    def match(self, msg: Message) -> bool:
        return isinstance(msg, self.msg_type) and all(
            getattr(msg, k, None) == v for k, v in self.kwargs.items()
        )


class Bus:
    """
    Main local bus where the daemon will listen for new messages.
    """

    _MSG_EXPIRY_TIMEOUT = 60.0  # Consider a message on the bus as expired after one minute without being picked up

    def __init__(self, on_message=None):
        self.bus = Queue()
        self.on_message = on_message
        self.thread_id = threading.get_ident()
        self.handlers: Dict[
            Type[Message], Dict[Callable[[Message], None], MessageHandler]
        ] = defaultdict(dict)

        self._should_stop = threading.Event()
        self._executor = get_bus_executor()

    def post(self, msg):
        """Sends a message to the bus"""
        self.bus.put(msg)

    def get(self, timeout: Optional[float] = 0.1) -> Optional[Message]:
        """Reads one message from the bus"""
        try:
            return self.bus.get(timeout=timeout)
        except Empty:
            return None

    def stop(self):
        self._should_stop.set()

    def _get_matching_handlers(
        self, msg: Message
    ) -> Iterable[Callable[[Message], None]]:
        return [
            callback
            for cls in type(msg).__mro__
            for callback, hndl in self.handlers.get(cls, {}).items()
            if hndl.match(msg)
        ]

    def _run_handler(self, msg: Message, handler: Callable[[Message], None]):
        logger.info('Triggering event handler %s', handler.__name__)
        try:
            handler(msg)
        except Exception as e:
            logger.error(
                'Error in event handler %s for message %s', handler.__name__, msg
            )
            logger.exception(e)

    def _run_on_message(self, msg: Message):
        try:
            if self.on_message:
                self.on_message(msg)
        except Exception as e:
            logger.error('Error on processing message %s', msg)
            logger.exception(e)

    def _msg_executor(self, msg):
        for hndl in self._get_matching_handlers(msg):
            self._executor.submit(self._run_handler, msg, hndl)

        self._run_on_message(msg)

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

            timestamp = getattr(msg, 'timestamp', None)
            if timestamp and time.time() - timestamp > self._MSG_EXPIRY_TIMEOUT:
                logger.debug(
                    '%f seconds old message on the bus expired, ignoring it: %s',
                    time.time() - msg.timestamp,
                    msg,
                )
                continue

            self._executor.submit(self._msg_executor, msg)

        logger.info('Bus service stopped')

    def register_handler(
        self, type: Type[Message], handler: Callable[[Message], None], **kwargs
    ) -> Callable[[], None]:
        """
        Register a generic handler to the bus.

        :param type: Type of the message to subscribe to (event inheritance also works).
        :param handler: Event handler - a function that takes a Message object as parameter.
        :param kwargs: Extra filter on the message values.
        :return: A function that can be called to remove the handler (no parameters required).
        """
        self.handlers[type][handler] = MessageHandler(type, handler, kwargs)

        def unregister():
            self.unregister_handler(type, handler)

        return unregister

    def unregister_handler(
        self, type: Type[Message], handler: Callable[[Message], None]
    ) -> None:
        """
        Remove an event handler.

        :param event_type: Event type.
        :param handler: Existing event handler.
        """
        if type not in self.handlers:
            return

        self.handlers[type].pop(handler, None)
        if len(self.handlers[type]) == 0:
            del self.handlers[type]


# vim:sw=4:ts=4:et:
