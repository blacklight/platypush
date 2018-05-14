import logging
import json

from redis import Redis

from platypush.backend import Backend
from platypush.message import Message


class RedisBackend(Backend):
    """
    Backend that reads messages from a configured Redis queue
    (default: `platypush_bus_mq`) and posts them to the application bus.
    Very useful when you have plugin whose code is executed in another process
    and can't post events or requests to the application bus.
    """

    def __init__(self, queue='platypush_bus_mq', redis_args={}, *args, **kwargs):
        """
        Params:
            queue -- Queue to poll for new messages
            redis_args -- Arguments that will be passed to the redis-py
                constructor (e.g. host, port, password),
                see http://redis-py.readthedocs.io/en/latest/
        """
        super().__init__(*args, **kwargs)

        self.queue = queue
        self.redis_args = redis_args
        self.redis = Redis(**self.redis_args)


    def send_message(self, msg):
        self.redis.rpush(self.queue, msg)


    def run(self):
        super().run()

        logging.info('Initialized Redis backend on queue {} with arguments {}'.
                     format(self.queue, self.redis_args))

        while not self.should_stop():
            try:
                msg = self.redis.blpop(self.queue)
                msg = Message.build(json.loads(msg[1].decode('utf-8')))
                self.bus.post(msg)
            except Exception as e:
                logging.exception(e)


# vim:sw=4:ts=4:et:

