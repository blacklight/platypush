import logging
import threading
from typing import Optional

from platypush.bus import Bus
from platypush.message import Message

logger = logging.getLogger('platypush:bus:redis')


class RedisBus(Bus):
    """
    Overrides the in-process in-memory local bus with a Redis bus
    """

    _DEFAULT_REDIS_QUEUE = 'platypush/bus'

    def __init__(self, *args, on_message=None, redis_queue=None, **kwargs):
        from platypush.utils import get_redis

        super().__init__(on_message=on_message)
        self.redis = get_redis(*args, **kwargs)
        self.redis_args = kwargs
        self.redis_queue = redis_queue or self._DEFAULT_REDIS_QUEUE
        self.on_message = on_message
        self.thread_id = threading.get_ident()

    def get(self) -> Optional[Message]:
        """
        Reads one message from the Redis queue
        """

        try:
            if self.should_stop():
                return None

            msg = self.redis.blpop(self.redis_queue, timeout=1)
            if not msg or msg[1] is None:
                return None

            msg = msg[1].decode('utf-8')
            return Message.build(msg)
        except Exception as e:
            logger.exception(e)

        return None

    def post(self, msg):
        """
        Sends a message to the Redis queue
        """

        return self.redis.rpush(self.redis_queue, str(msg))

    def stop(self):
        super().stop()
        self.redis.close()


# vim:sw=4:ts=4:et:
