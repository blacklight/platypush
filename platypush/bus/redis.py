import logging
import threading

from platypush.bus import Bus
from platypush.message import Message

logger = logging.getLogger('platypush:bus:redis')


class RedisBus(Bus):
    """
    Overrides the in-process in-memory local bus with a Redis bus
    """

    DEFAULT_REDIS_QUEUE: str = 'platypush/bus'

    def __init__(self, *args, on_message=None, redis_queue=None, **kwargs):
        from platypush.utils import get_redis

        super().__init__(on_message=on_message)
        self.redis = get_redis(*args, **kwargs)
        self.redis_args = kwargs
        self.redis_queue = redis_queue or self.DEFAULT_REDIS_QUEUE
        self.on_message = on_message
        self.thread_id = threading.get_ident()
        self._pubsub = None
        self._pubsub_lock = threading.RLock()

    @property
    def pubsub(self):
        with self._pubsub_lock:
            if not self._pubsub:
                self._pubsub = self.redis.pubsub()
            return self._pubsub

    def poll(self):
        """
        Polls the Redis queue for new messages
        """
        from platypush.message.event.application import ApplicationStartedEvent

        with self.pubsub as pubsub:
            pubsub.subscribe(self.redis_queue)
            self.post(ApplicationStartedEvent())

            try:
                for msg in pubsub.listen():
                    if msg.get('type') != 'message':
                        continue

                    if self.should_stop():
                        break

                    try:
                        data = msg.get('data', b'').decode('utf-8')
                        parsed_msg = Message.build(data)
                        if parsed_msg and self.on_message:
                            self.on_message(parsed_msg)
                    except Exception as e:
                        logger.exception(e)
            finally:
                pubsub.unsubscribe(self.redis_queue)

    def post(self, msg):
        """
        Sends a message to the Redis queue
        """
        from redis import exceptions

        try:
            self.redis.publish(self.redis_queue, str(msg))
        except exceptions.ConnectionError as e:
            if not self.should_stop():
                # Raise the exception only if the bus it not supposed to be
                # stopped
                raise e

    def stop(self):
        super().stop()
        self.redis.close()


# vim:sw=4:ts=4:et:
