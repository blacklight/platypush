from redis import Redis

from platypush.plugins import Plugin, action
from platypush.utils import get_redis_conf


class RedisPlugin(Plugin):
    """
    Plugin to send messages on Redis queues.

    See https://redis-py.readthedocs.io/en/latest/connections.html#redis.Redis
    for supported parameters.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs or get_redis_conf()

    def _get_redis(self):
        return Redis(*self.args, **self.kwargs)

    @action
    def send_message(self, queue: str, msg, *args, **kwargs):
        """
        Send a message to a Redis queue.

        :param queue: Queue name
        :param msg: Message to be sent
        :type msg: str, bytes, list, dict, :class:`platypush.message.Message`

        :param args: Args passed to the Redis constructor (see
            https://redis-py.readthedocs.io/en/latest/connections.html#redis.Redis)
        :param kwargs: Kwargs passed to the Redis constructor (see
            https://redis-py.readthedocs.io/en/latest/connections.html#redis.Redis)
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
            keys[i]: value.decode() if isinstance(value, bytes) else value
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
            # Commit https://github.com/andymccurdy/redis-py/commit/90a52dd5de111f0053bb3ebaa7c78f73a82a1e3e
            # broke back-compatibility with the previous way of passing
            # key-value pairs to mset directly on kwargs. This try-catch block
            # is to support things on all the redis-py versions
            return self._get_redis().mset(mapping=kwargs)  # type: ignore

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
