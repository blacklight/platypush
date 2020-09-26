import ast
import json
import logging
import threading

from redis import Redis

from platypush.bus import Bus
from platypush.config import Config
from platypush.message import Message

logger = logging.getLogger('platypush:bus:redis')


class RedisBus(Bus):
    """ Overrides the in-process in-memory local bus with a Redis bus """
    _DEFAULT_REDIS_QUEUE = 'platypush/bus'

    def __init__(self, on_message=None, redis_queue=_DEFAULT_REDIS_QUEUE,
                 *args, **kwargs):
        super().__init__(on_message=on_message)

        if not args and not kwargs:
            kwargs = (Config.get('backend.redis') or {}).get('redis_args', {})

        self.redis = Redis(*args, **kwargs)
        self.redis_args = kwargs
        self.redis_queue = redis_queue
        self.on_message = on_message
        self.thread_id = threading.get_ident()

    def get(self):
        """ Reads one message from the Redis queue """
        msg = None

        try:
            msg = self.redis.blpop(self.redis_queue)
            if not msg or msg[1] is None:
                return

            msg = msg[1].decode('utf-8')
            try:
                msg = json.loads(msg)
            except json.decoder.JSONDecodeError:
                msg = ast.literal_eval(msg)

            msg = Message.build(msg)
        except Exception as e:
            logger.exception(e)

        return msg

    def post(self, msg):
        """ Sends a message to the Redis queue """
        return self.redis.rpush(self.redis_queue, str(msg))


# vim:sw=4:ts=4:et:
