import json

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

    Requires:

        * **redis** (``pip install redis``)
    """

    def __init__(self, queue='platypush_bus_mq', redis_args=None, *args, **kwargs):
        """
        :param queue: Queue name to listen on (default: ``platypush_bus_mq``)
        :type queue: str

        :param redis_args: Arguments that will be passed to the redis-py constructor (e.g. host, port, password), see
            http://redis-py.readthedocs.io/en/latest/
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
        self.redis = Redis(**self.redis_args)

    def send_message(self, msg, queue_name=None, **kwargs):
        msg = str(msg)
        if queue_name:
            self.redis.rpush(queue_name, msg)
        else:
            self.redis.rpush(self.queue, msg)

    # noinspection PyBroadException
    def get_message(self, queue_name=None):
        queue = queue_name or self.queue
        msg = self.redis.blpop(queue)[1].decode('utf-8')

        try:
            msg = Message.build(json.loads(msg))
        except:
            try:
                import ast
                msg = Message.build(ast.literal_eval(msg))
            except:
                try:
                    msg = json.loads(msg)
                except Exception as e:
                    self.logger.exception(e)

        return msg

    def run(self):
        super().run()

        self.logger.info('Initialized Redis backend on queue {} with arguments {}'.
                         format(self.queue, self.redis_args))

        while not self.should_stop():
            try:
                msg = self.get_message()
                self.logger.info('Received message on the Redis backend: {}'.
                                 format(msg))
                self.on_message(msg)
            except Exception as e:
                self.logger.exception(e)


# vim:sw=4:ts=4:et:
