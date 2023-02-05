import json
from typing import Optional, Union

from redis import Redis

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message import Message


class RedisBackend(Backend):
    """
    Backend that reads messages from a configured Redis queue (default:
    ``platypush_bus_mq``) and posts them to the application bus.  Very
    useful when you have plugin whose code is executed in another process
    and can't post events or requests to the application bus.
    """

    def __init__(self, *args, queue='platypush_bus_mq', redis_args=None, **kwargs):
        """
        :param queue: Queue name to listen on (default: ``platypush_bus_mq``)
        :type queue: str

        :param redis_args: Arguments that will be passed to the redis-py constructor (e.g. host, port, password), see
            https://redis-py.readthedocs.io/en/latest/
        :type redis_args: dict
        """

        super().__init__(*args, **kwargs)
        if redis_args is None:
            redis_args = {}

        self.queue = queue

        if not redis_args:
            redis_plugin = get_plugin('redis')
            if redis_plugin and redis_plugin.kwargs:
                redis_args = redis_plugin.kwargs

        self.redis_args = redis_args
        self.redis: Optional[Redis] = None

    def send_message(
        self, msg: Union[str, Message], queue_name: Optional[str] = None, **_
    ):
        """
        Send a message to a Redis queue.

        :param msg: Message to send, as a ``Message`` object or a string.
        :param queue_name: Queue name to send the message to (default: ``platypush_bus_mq``).
        """

        if not self.redis:
            self.logger.warning('The Redis backend is not yet running.')
            return

        self.redis.rpush(queue_name or self.queue, str(msg))

    def get_message(self, queue_name=None):
        queue = queue_name or self.queue
        data = self.redis.blpop(queue, timeout=1)
        if data is None:
            return

        msg = data[1].decode()
        try:
            msg = Message.build(msg)
        except Exception as e:
            self.logger.debug(str(e))
            try:
                import ast

                msg = Message.build(ast.literal_eval(msg))
            except Exception as ee:
                self.logger.debug(str(ee))
                try:
                    msg = json.loads(msg)
                except Exception as eee:
                    self.logger.exception(eee)

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
