from multiprocessing import Lock

from platypush.bus.redis import RedisBus
from platypush.context import get_bus
from platypush.config import Config
from platypush.message import Message
from platypush.message.request import Request
from platypush.utils import get_message_response

from .logger import logger


class BusWrapper:  # pylint: disable=too-few-public-methods
    """
    Lazy singleton wrapper for the bus object.
    """

    def __init__(self):
        self._redis_queue = None
        self._bus = None
        self._bus_lock = Lock()

    @property
    def bus(self) -> RedisBus:
        """
        Lazy getter/initializer for the bus object.
        """
        with self._bus_lock:
            if not self._bus:
                self._bus = get_bus()

        bus_: RedisBus = self._bus  # type: ignore
        return bus_

    def post(self, msg):
        """
        Send a message to the bus.

        :param msg: The message to send.
        """
        try:
            self.bus.post(msg)
        except Exception as e:
            logger().exception(e)


_bus = BusWrapper()


def bus():
    """
    Lazy getter/initializer for the bus object.
    """
    return _bus.bus


def send_message(msg, wait_for_response=True):
    """
    Send a message to the bus.

    :param msg: The message to send.
    :param wait_for_response: If ``True``, wait for the response to be received
        before returning, otherwise return immediately.
    """
    msg = Message.build(msg)
    if msg is None:
        return None

    if isinstance(msg, Request):
        msg.origin = 'http'

    if Config.get('token'):
        msg.token = Config.get('token')

    bus().post(msg)

    if isinstance(msg, Request) and wait_for_response:
        response = get_message_response(msg)
        logger().debug('Processing response on the HTTP backend: %s', response)

        return response

    return None


def send_request(action, wait_for_response=True, **kwargs):
    """
    Send a request to the bus.

    :param action: The action to send.
    :param wait_for_response: If ``True``, wait for the response to be received
        before returning, otherwise return immediately.
    :param kwargs: Additional arguments to pass to the action.
    """
    msg = {'type': 'request', 'action': action}

    if kwargs:
        msg['args'] = kwargs

    rs = send_message(msg, wait_for_response=wait_for_response)
    assert rs, 'Got an empty response from the server'
    if rs:
        assert not rs.errors, '\n'.join(rs.errors)

    return rs.output
