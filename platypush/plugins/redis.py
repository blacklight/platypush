from redis import Redis

from platypush.context import get_backend
from platypush.plugins import Plugin, action


class RedisPlugin(Plugin):
    """
    Plugin to send messages on Redis queues.

    Requires:

        * **redis** (``pip install redis``)
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

        if not kwargs:
            # noinspection PyBroadException
            try:
                redis_backend = get_backend('redis')
                if redis_backend and redis_backend.redis_args:
                    self.kwargs = redis_backend.redis_args
            except:
                pass

    def _get_redis(self):
        return Redis(*self.args, **self.kwargs)

    @action
    def send_message(self, queue, msg, *args, **kwargs):
        """
        Send a message to a Redis queue.

        :param queue: Queue name
        :type queue: str

        :param msg: Message to be sent
        :type msg: str, bytes, list, dict, Message object

        :param args: Args passed to the Redis constructor (see https://redis-py.readthedocs.io/en/latest/#redis.Redis)
        :type args: list

        :param kwargs: Kwargs passed to the Redis constructor (see
            https://redis-py.readthedocs.io/en/latest/#redis.Redis)
        :type kwargs: dict
        """

        if args or kwargs:
            redis = Redis(*args, **kwargs)
        else:
            redis = self._get_redis()

        return redis.rpush(queue, str(msg))

    @action
    def mget(self, keys, *args):
        """
        :returns: The values specified in keys as a key/value dict (wraps MGET)
        """

        return {
            keys[i]: value.decode() if value else value
            for (i, value) in enumerate(self._get_redis().mget(keys, *args))
        }

    @action
    def mset(self, **kwargs):
        """
        Set key/values based on mapping (wraps MSET)
        """

        try:
            return self._get_redis().mset(**kwargs)
        except TypeError:
            # XXX commit https://github.com/andymccurdy/redis-py/commit/90a52dd5de111f0053bb3ebaa7c78f73a82a1e3e
            # broke back-compatibility with the previous way of passing
            # key-value pairs to mset directly on kwargs. This try-catch block
            # is to support things on all the redis-py versions
            return self._get_redis().mset(mapping=kwargs)

    @action
    def expire(self, key, expiration):
        """
        Set an expiration time in seconds for the specified key

        :param key: Key to set to expire
        :type key: str

        :param expiration: Expiration timeout (in seconds)
        :type expiration: int
        """

        return self._get_redis().expire(key, expiration)

    @action
    def delete(self, *args):
        """
        Delete one or multiple keys

        :param args: Keys to delete
        """

        return self._get_redis().delete(*args)


# vim:sw=4:ts=4:et:
