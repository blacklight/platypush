import statistics
import time

from queue import Empty, Queue
from threading import Thread
from typing import Iterable, Optional, Union

from platypush.message.event.adafruit import (
    AdafruitConnectedEvent,
    AdafruitDisconnectedEvent,
    AdafruitFeedUpdateEvent,
)
from platypush.plugins import RunnablePlugin, action


class AdafruitIoPlugin(RunnablePlugin):
    """
    This plugin allows you to interact with `Adafruit IO
    <https://io.adafruit.com>`_, a cloud-based message queue and storage. You
    can use this plugin to send and receive data to topics connected to your
    Adafruit IO account.

    Some example usages:

      .. code-block:: javascript

        // Send the temperature value for a connected sensor to the "temperature" feed
        {
            "type": "request",
            "action": "adafruit.io.send",
            "args": {
                "feed": "temperature",
                "value": 25.0
            }
        }

        // Receive the most recent temperature value
        {
            "type": "request",
            "action": "adafruit.io.receive",
            "args": {
                "feed": "temperature"
            }
        }

    """

    def __init__(
        self,
        username: str,
        key: str,
        feeds: Iterable[str] = (),
        throttle_interval: Optional[float] = None,
        **kwargs
    ):
        """
        :param username: Your Adafruit username
        :param key: Your Adafruit IO key
        :param feeds: List of feeds to subscribe to. If not set, then the plugin
            will not subscribe to any feed unless instructed to do so, neither
            it will emit any event.
        :param throttle_interval: If set, then instead of sending the values
            directly over ``send`` the plugin will first collect all the
            samples within the specified period and then dispatch them to
            Adafruit IO. You may want to set it if you have data sources
            providing a lot of data points and you don't want to hit the
            throttling limitations of Adafruit.
        """

        from Adafruit_IO import Client, MQTTClient

        super().__init__(**kwargs)

        self._username = username
        self._key = key
        self.feeds = feeds
        self.aio = Client(username=username, key=key)
        self._mqtt_client: Optional[MQTTClient] = None
        self.throttle_interval = throttle_interval
        self._data_throttler_thread: Optional[Thread] = None
        self._data_throttler_queue = Queue()

    @property
    def _mqtt(self):
        if not self._mqtt_client:
            from Adafruit_IO import MQTTClient

            self._mqtt_client = MQTTClient(self._username, self._key)
            self._mqtt_client.on_connect = self._on_connect  # type: ignore
            self._mqtt_client.on_disconnect = self._on_disconnect  # type: ignore
            self._mqtt_client.on_message = self._on_message  # type: ignore

        return self._mqtt_client

    def _on_connect(self, *_, **__):
        assert self._mqtt_client, 'MQTT client not initialized'
        for feed in self.feeds:
            self._mqtt_client.subscribe(feed)
        self._bus.post(AdafruitConnectedEvent())

    def _on_disconnect(self, *_, **__):
        self._bus.post(AdafruitDisconnectedEvent())

    def _on_message(self, _, feed, data, *__):
        try:
            data = float(data)
        except (TypeError, ValueError):
            pass

        self._bus.post(AdafruitFeedUpdateEvent(feed=feed, data=data))

    def _subscribe(self, feed: str):
        assert self._mqtt_client, 'MQTT client not initialized'
        self._mqtt_client.subscribe(feed)

    def _unsubscribe(self, feed: str):
        assert self._mqtt_client, 'MQTT client not initialized'
        self._mqtt_client.unsubscribe(feed)

    def _data_throttler(self):
        from Adafruit_IO import ThrottlingError

        if not self.throttle_interval:
            return

        last_processed_batch_timestamp = None
        data = {}

        try:
            while not self.should_stop():
                try:
                    new_data = self._data_throttler_queue.get(timeout=1)
                    for key, value in new_data.items():
                        data.setdefault(key, []).append(value)
                except Empty:
                    continue

                should_process = data and (
                    last_processed_batch_timestamp is None
                    or time.time() - last_processed_batch_timestamp
                    >= self.throttle_interval
                )

                if not should_process:
                    continue

                last_processed_batch_timestamp = time.time()
                self.logger.info('Processing feeds batch for Adafruit IO')

                for feed, values in data.items():
                    if values:
                        value = statistics.mean(values)

                        try:
                            self.send(feed, value, enqueue=False)
                        except ThrottlingError:
                            self.logger.warning(
                                'Adafruit IO throttling threshold hit, taking a nap '
                                + 'before retrying'
                            )
                            self.wait_stop(self.throttle_interval)

                data = {}
        except Exception as e:
            self.logger.exception(e)

    @action
    def send(self, feed: str, value: Union[int, float, str], enqueue: bool = True):
        """
        Send a value to an Adafruit IO feed.

        :param feed: Feed name.
        :param value: Value to send.
        :param enqueue: If throttle_interval is set, this method by default will append values to the throttling queue
            to be periodically flushed instead of sending the message directly. In such case, pass enqueue=False to
            override the behaviour and send the message directly instead.
        """

        if not self.throttle_interval or not enqueue:
            # If no throttling is configured, or enqueue is false then send the value directly to Adafruit
            self.aio.send(feed, value)
        else:
            # Otherwise send it to the queue to be picked up by the throttler thread
            self._data_throttler_queue.put({feed: value})

    @action
    def send_location_data(
        self,
        feed: str,
        latitude: float,
        longitude: float,
        elevation: float,
        value: Optional[Union[int, float, str]] = None,
    ):
        """
        Send location data to an Adafruit IO feed

        :param feed: Feed name
        :param lat: Latitude
        :param lon: Longitude
        :param ele: Elevation
        :param value: Extra value to attach to the record
        """

        self.aio.send_data(
            feed=feed,
            value=value,
            metadata={
                'lat': latitude,
                'lon': longitude,
                'ele': elevation,
            },
        )

    @action
    def subscribe(self, feed: str):
        """
        Subscribe to a feed.

        :param feed: Feed name
        """
        self._subscribe(feed)

    @action
    def unsubscribe(self, feed: str):
        """
        Unsubscribe from a feed.

        :param feed: Feed name
        """
        self._unsubscribe(feed)

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
                if attr == 'value'
                else getattr(i, attr)
                for attr in DATA_FIELDS
                if getattr(i, attr) is not None
            }
            for i in data
        ]

    @action
    def receive(self, feed: str, limit: int = 1):
        """
        Receive data from the specified Adafruit IO feed

        :param feed: Feed name
        :param limit: Maximum number of data points to be returned. If None,
            all the values in the feed will be returned. Default: 1 (return most
            recent value)
        """

        if limit == 1:
            values = self._convert_data_to_dict(self.aio.receive(feed))
            return values[0] if values else None

        values = self._convert_data_to_dict(*self.aio.data(feed))
        return values[:limit] if limit else values

    @action
    def receive_next(self, feed: str):
        """
        Receive the next unprocessed data point from a feed

        :param feed: Feed name
        """

        values = self._convert_data_to_dict(self.aio.receive_next(feed))
        return values[0] if values else None

    @action
    def receive_previous(self, feed: str):
        """
        Receive the last processed data point from a feed

        :param feed: Feed name
        """

        values = self._convert_data_to_dict(self.aio.receive_previous(feed))
        return values[0] if values else None

    @action
    def delete(self, feed: str, data_id: str):
        """
        Delete a data point from a feed

        :param feed: Feed name
        :param data_id: Data point ID to remove
        """

        self.aio.delete(feed, data_id)

    def main(self):
        if self.throttle_interval:
            self._data_throttler_thread = Thread(target=self._data_throttler)
            self._data_throttler_thread.start()

        try:
            while not self.should_stop():
                cur_wait = 1
                max_wait = 60

                try:
                    self._mqtt.connect()
                    cur_wait = 1
                    self._mqtt.loop_blocking()
                except Exception as e:
                    self.logger.warning(
                        'Adafruit IO connection error: %s, retrying in %d seconds',
                        e,
                        cur_wait,
                    )

                    self.logger.exception(e)
                    self.wait_stop(cur_wait)
                    cur_wait = min(cur_wait * 2, max_wait)
                finally:
                    self._stop_mqtt()
        finally:
            self._stop_data_throttler()

    def _stop_mqtt(self):
        if self._mqtt_client:
            self._mqtt_client.disconnect()
            self._mqtt_client = None

    def _stop_data_throttler(self):
        if self._data_throttler_thread:
            self._data_throttler_thread.join()
            self._data_throttler_thread = None

    def _stop(self):
        self._stop_mqtt()
        self._stop_data_throttler()

    def stop(self):
        self._stop()
        super().stop()


# vim:sw=4:ts=4:et:
