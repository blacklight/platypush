from redis import Redis

from platypush.bus.redis import RedisBus
from platypush.config import Config
from platypush.context import get_backend
from platypush.message import Message
from platypush.message.request import Request
from platypush.utils import get_redis_conf, get_redis_queue_name_by_message

from .logger import logger

_bus = None


def bus():
    """
    Lazy getter/initializer for the bus object.
    """
    global _bus  # pylint: disable=global-statement
    if _bus is None:
        redis_queue = get_backend('http').bus.redis_queue  # type: ignore
        _bus = RedisBus(**get_redis_conf(), redis_queue=redis_queue)
    return _bus


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

    return send_message(msg, wait_for_response=wait_for_response)


def get_message_response(msg):
    """
    Get the response to the given message.

    :param msg: The message to get the response for.
    :return: The response to the given message.
    """
    redis = Redis(**bus().redis_args)
    redis_queue = get_redis_queue_name_by_message(msg)
    if not redis_queue:
        return None

    response = redis.blpop(redis_queue, timeout=60)
    if response and len(response) > 1:
        response = Message.build(response[1])
    else:
        response = None

    return response
