import json
from typing import Any, Dict, Optional, Union

from redis import Redis

from platypush.backend import Backend
from platypush.message import Message
from platypush.utils import get_redis_conf


class RedisBackend(Backend):
    """
    Backend that reads messages from a configured Redis queue (default:
    ``platypush/backend/redis``) and forwards them to the application bus.

    Useful when you have plugin whose code is executed in another process
    and can't post events or requests to the application bus.
    """

    def __init__(
        self,
        *args,
        queue: str = 'platypush/backend/redis',
        redis_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        :param queue: Name of the Redis queue to listen to (default:
            ``platypush/backend/redis``).

        :param redis_args: Arguments that will be passed to the redis-py
            constructor (e.g. host, port, password). See
            https://redis-py.readthedocs.io/en/latest/connections.html#redis.Redis
            for supported parameters.
        """
        super().__init__(*args, **kwargs)
        self.redis_args = redis_args or get_redis_conf()
        self.queue = queue
        self.redis: Optional[Redis] = None

    def send_message(
        self, msg: Union[str, Message], queue_name: Optional[str] = None, **_
    ):
        """
        Send a message to a Redis queue.

        :param msg: Message to send, as a ``Message`` object or a string.
        :param queue_name: Queue name to send the message to (default:
            configured ``queue`` value).
        """
        if not self.redis:
            self.logger.warning('The Redis backend is not yet running.')
            return

        self.redis.rpush(queue_name or self.queue, str(msg))

    def get_message(self, queue_name: Optional[str] = None) -> Optional[Message]:
        queue = queue_name or self.queue
        assert self.redis, 'The Redis backend is not yet running.'
        data = self.redis.blpop(queue, timeout=1)
        if data is None:
            return None

        msg = data[1].decode()
        try:
            msg = Message.build(msg)
        except Exception as e:
            self.logger.debug(str(e))
            try:
                msg = json.loads(msg)
            except Exception as ee:
                self.logger.exception(ee)

        return msg

    def run(self):
        super().run()
        self.logger.info(
            'Initialized Redis backend on queue %s with arguments %s',
            self.queue,
            self.redis_args,
        )

        with Redis(**self.redis_args) as self.redis:
            while not self.should_stop():
                try:
                    msg = self.get_message()
                    if not msg:
                        continue

                    self.logger.info('Received message on the Redis backend: %s', msg)
                    self.on_message(msg)
                except Exception as e:
                    self.logger.exception(e)

        self.logger.info('Redis backend terminated')


# vim:sw=4:ts=4:et:
