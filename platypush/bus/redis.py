import logging
import random
import threading
import time
from typing import Callable

from platypush.bus import Bus
from platypush.message import Message

logger = logging.getLogger('platypush:bus:redis')


class RedisBus(Bus):
    """
    Overrides the in-process in-memory local bus with a Redis bus
    """

    DEFAULT_REDIS_QUEUE: str = 'platypush/bus'
    _PUBSUB_POLL_TIMEOUT: float = 1.0

    def __init__(self, *_, on_message=None, redis_queue=None, **kwargs):
        super().__init__(on_message=on_message)
        self.redis_args = kwargs
        self._redis = None
        self.redis_queue = redis_queue or self.DEFAULT_REDIS_QUEUE
        self.on_message = on_message
        self.thread_id = threading.get_ident()
        self._pubsub = None
        self._pubsub_lock = threading.RLock()

    @property
    def redis(self):
        from platypush.utils import get_redis

        if self._redis is None:
            self._redis = get_redis(**self.redis_args)
        return self._redis

    @property
    def pubsub(self):
        with self._pubsub_lock:
            if self._pubsub is None:
                self._pubsub = self.redis.pubsub()
            return self._pubsub

    def _close_pubsub(self):
        with self._pubsub_lock:
            if self._pubsub is not None:
                self._pubsub.close()
                self._pubsub = None

    def poll(self):
        """
        Polls the Redis queue for new messages
        """
        from redis.exceptions import (
            ConnectionError as RedisConnectionError,
            TimeoutError as RedisTimeoutError,
        )

        from platypush.message.event.application import ApplicationStartedEvent
        from platypush.utils import redis_pools

        has_error = False

        while not self.should_stop():
            try:
                pubsub = self.pubsub
                pubsub.subscribe(self.redis_queue)
                self.post(ApplicationStartedEvent())

                while not self.should_stop():
                    msg = pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=self._PUBSUB_POLL_TIMEOUT,
                    )

                    if has_error:
                        logger.info('Redis connection restored')

                    has_error = False
                    if not msg:
                        continue

                    try:
                        data = msg.get('data', b'').decode('utf-8')
                        logger.debug('Received message on the Redis bus: %r', data)
                        parsed_msg = Message.build(data)
                        if parsed_msg:
                            self._on_message(parsed_msg)
                    except Exception as e:
                        logger.exception(e)
            except (RedisTimeoutError, RedisConnectionError) as e:
                if not (self.should_stop() or has_error):
                    logger.warning('Redis connection error: %s', e)

                has_error = True
                self._close_pubsub()
                redis_pools.clear()  # Clear the connection pool
                self._redis = None
                time.sleep(1)
            finally:
                if self._pubsub is not None:
                    try:
                        self._pubsub.unsubscribe(self.redis_queue)
                    except (RedisConnectionError, RedisTimeoutError) as e:
                        logger.warning(
                            'Could not unsubscribe from Redis queue %s: %s',
                            self.redis_queue,
                            e,
                        )

    def _on_message(self, msg: Message):
        if self.on_message:
            self.on_message(msg)

        def msg_handler(event: Message, handler: Callable[[Message], None]):
            logger.debug(
                'Triggering event handler <%s.%s> from event %s',
                handler.__module__,
                handler.__name__,
                type(event),
            )
            handler(event)

        for hndl in self._get_matching_handlers(msg):
            threading.Thread(
                target=msg_handler,
                args=(msg, hndl),
                name=f'handler-{hndl.__name__}-{random.randint(0, 10000)}',
                daemon=True,
            ).start()

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
        self._close_pubsub()
        if self._redis is not None:
            self._redis.close()


# vim:sw=4:ts=4:et:
