from redis import Redis

from platypush.plugins import Plugin, action


class RedisPlugin(Plugin):
    """
    Plugin to send messages on Redis queues.

    Requires:

        * **redis** (``pip install redis``)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def send_message(self, queue, msg, *args, **kwargs):
        """
        Send a message to a Redis queu.

        :param queue: Queue name
        :type queue: str

        :param msg: Message to be sent
        :type msg: str, bytes, list, dict, Message object

        :param args: Args passed to the Redis constructor (see https://redis-py.readthedocs.io/en/latest/#redis.Redis)
        :type args: list

        :param kwargs: Kwargs passed to the Redis constructor (see https://redis-py.readthedocs.io/en/latest/#redis.Redis)
        :type kwargs: dict
        """

        redis = Redis(*args, **kwargs)
        redis.rpush(queue, msg)


# vim:sw=4:ts=4:et:

