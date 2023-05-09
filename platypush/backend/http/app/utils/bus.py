from redis import Redis

from platypush.bus.redis import RedisBus
from platypush.config import Config
from platypush.context import get_backend
from platypush.message import Message
from platypush.message.request import Request
from platypush.utils import get_redis_queue_name_by_message

from .logger import logger

_bus = None


def bus():
    global _bus
    if _bus is None:
        redis_queue = get_backend('http').bus.redis_queue  # type: ignore
        _bus = RedisBus(redis_queue=redis_queue)
    return _bus


def send_message(msg, wait_for_response=True):
    msg = Message.build(msg)
    if msg is None:
        return

    if isinstance(msg, Request):
        msg.origin = 'http'

    if Config.get('token'):
        msg.token = Config.get('token')

    bus().post(msg)

    if isinstance(msg, Request) and wait_for_response:
        response = get_message_response(msg)
        logger().debug('Processing response on the HTTP backend: {}'.format(response))

        return response


def send_request(action, wait_for_response=True, **kwargs):
    msg = {'type': 'request', 'action': action}

    if kwargs:
        msg['args'] = kwargs

    return send_message(msg, wait_for_response=wait_for_response)


def get_message_response(msg):
    redis = Redis(**bus().redis_args)
    redis_queue = get_redis_queue_name_by_message(msg)
    if not redis_queue:
        return

    response = redis.blpop(redis_queue, timeout=60)
    if response and len(response) > 1:
        response = Message.build(response[1])
    else:
        response = None

    return response
