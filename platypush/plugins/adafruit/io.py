import ast
import statistics
import json
import time

from threading import Thread, Lock

from platypush.context import get_backend
from platypush.plugins import Plugin, action

data_throttler_lock = None


class AdafruitIoPlugin(Plugin):
    """
    This plugin allows you to interact with the Adafruit IO
    <https://io.adafruit.com>, a cloud-based message queue and storage.
    You can send values to feeds on your Adafruit IO account and read the
    values of those feeds as well through any device.

    Requires:

        * **adafruit-io** (``pip install adafruit-io``)
        * Redis server running and Redis backend configured if you want to enable throttling

    Some example usages::

        # Send the temperature value for a connected sensor to the "temperature" feed
        {
            "type": "request",
            "action": "adafruit.io.send",
            "args": {
                "feed": "temperature",
                "value": 25.0
            }
        }

        # Receive the most recent temperature value
        {
            "type": "request",
            "action": "adafruit.io.receive",
            "args": {
                "feed": "temperature"
            }
        }
    """

    _DATA_THROTTLER_QUEUE = 'platypush/adafruit.io'

    def __init__(self, username, key, throttle_seconds=None, **kwargs):
        """
        :param username: Your Adafruit username
        :type username: str

        :param key: Your Adafruit IO key
        :type key: str

        :param throttle_seconds: If set, then instead of sending the values directly over ``send`` the plugin will
            first collect all the samples within the specified period and then dispatch them to Adafruit IO.
            You may want to set it if you have data sources providing a lot of data points and you don't want to hit
            the throttling limitations of Adafruit.
        :type throttle_seconds: float
        """

        from Adafruit_IO import Client
        global data_throttler_lock
        super().__init__(**kwargs)

        self._username = username
        self._key = key
        self.aio = Client(username=username, key=key)
        self.throttle_seconds = throttle_seconds

        if not data_throttler_lock:
            data_throttler_lock = Lock()

        if self.throttle_seconds and not data_throttler_lock.locked():
            self._get_redis()
            self.logger.info('Starting Adafruit IO throttler thread')
            data_throttler_lock.acquire(False)
            self.data_throttler = Thread(target=self._data_throttler())
            self.data_throttler.start()

    @staticmethod
    def _get_redis():
        from redis import Redis

        redis_args = get_backend('redis').redis_args
        redis_args['socket_timeout'] = 1
        return Redis(**redis_args)

    def _data_throttler(self):
        from redis.exceptions import TimeoutError as QueueTimeoutError

        def run():
            redis = self._get_redis()
            last_processed_batch_timestamp = None
            data = {}

            try:
                while True:
                    try:
                        new_data = ast.literal_eval(
                            redis.blpop(self._DATA_THROTTLER_QUEUE)[1].decode('utf-8'))

                        for (key, value) in new_data.items():
                            data.setdefault(key, []).append(value)
                    except QueueTimeoutError:
                        pass

                    if data and (last_processed_batch_timestamp is None or
                                 time.time() - last_processed_batch_timestamp >= self.throttle_seconds):
                        last_processed_batch_timestamp = time.time()
                        self.logger.info('Processing feeds batch for Adafruit IO')

                        for (feed, values) in data.items():
                            if values:
                                value = statistics.mean(values)

                                try:
                                    self.send(feed, value, enqueue=False)
                                except ThrottlingError:
                                    self.logger.warning('Adafruit IO throttling threshold hit, taking a nap ' +
                                                        'before retrying')
                                    time.sleep(self.throttle_seconds)

                        data = {}
            except Exception as e:
                self.logger.exception(e)

        return run

    @action
    def send(self, feed, value, enqueue=True):
        """
        Send a value to an Adafruit IO feed

        :param feed: Feed name
        :type feed: str

        :param value: Value to send
        :type value: Numeric or string

        :param enqueue: If throttle_seconds is set, this method by default will append values to the throttling queue
            to be periodically flushed instead of sending the message directly. In such case, pass enqueue=False to
            override the behaviour and send the message directly instead.
        :type enqueue: bool
        """

        if not self.throttle_seconds or not enqueue:
            # If no throttling is configured, or enqueue is false then send the value directly to Adafruit
            self.aio.send(feed, value)
        else:
            # Otherwise send it to the Redis queue to be picked up by the throttler thread
            redis = self._get_redis()
            redis.rpush(self._DATA_THROTTLER_QUEUE, json.dumps({feed: value}))

    @action
    def send_location_data(self, feed, lat, lon, ele, value):
        """
        Send location data to an Adafruit IO feed

        :param feed: Feed name
        :type feed: str

        :param lat: Latitude
        :type lat: float

        :param lon: Longitude
        :type lon: float

        :param ele: Elevation
        :type ele: float

        :param value: Value to send
        :type value: Numeric or string
        """

        self.aio.send_data(feed=feed, value=value, metadata={
            'lat': lat,
            'lon': lon,
            'ele': ele,
        })

    @classmethod
    def _cast_value(cls, value):
        try:
            value = float(value)
        except ValueError:
            pass

        return value

    def _convert_data_to_dict(self, *data):
        from Adafruit_IO.model import DATA_FIELDS

        return [
            {
                attr: self._cast_value(getattr(i, attr))
                if attr == 'value' else getattr(i, attr)
                for attr in DATA_FIELDS if getattr(i, attr) is not None
            } for i in data
        ]

    @action
    def receive(self, feed, limit=1):
        """
        Receive data from the specified Adafruit IO feed

        :param feed: Feed name
        :type feed: str

        :param limit: Maximum number of data points to be returned. If None,
            all the values in the feed will be returned. Default: 1 (return most
            recent value)
        :type limit: int
        """

        if limit == 1:
            values = self._convert_data_to_dict(self.aio.receive(feed))
            return values[0] if values else None

        values = self._convert_data_to_dict(*self.aio.data(feed))
        return values[:limit] if limit else values

    @action
    def receive_next(self, feed):
        """
        Receive the next unprocessed data point from a feed

        :param feed: Feed name
        :type feed: str
        """

        values = self._convert_data_to_dict(self.aio.receive_next(feed))
        return values[0] if values else None

    @action
    def receive_previous(self, feed):
        """
        Receive the last processed data point from a feed

        :param feed: Feed name
        :type feed: str
        """

        values = self._convert_data_to_dict(self.aio.receive_previous(feed))
        return values[0] if values else None

    @action
    def delete(self, feed, data_id):
        """
        Delete a data point from a feed

        :param feed: Feed name
        :type feed: str

        :param data_id: Data point ID to remove
        :type data_id: str
        """

        self.aio.delete(feed, data_id)


# vim:sw=4:ts=4:et:
