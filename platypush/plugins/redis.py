import logging

from redis import Redis

from platypush.message.response import Response
from platypush.plugins import Plugin


class RedisPlugin(Plugin):
    def send_message(self, queue, msg, *args, **kwargs):
        redis = Redis(*args, **kwargs)
        redis.rpush(queue, msg)
        return Response(output={'state': 'ok'})


# vim:sw=4:ts=4:et:

