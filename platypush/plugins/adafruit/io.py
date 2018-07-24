from Adafruit_IO import Client

from platypush.message import Message
from platypush.plugins import Plugin, action

class AdafruitIoPlugin(Plugin):
    """
    This plugin allows you to interact with the Adafruit IO
    <https://io.adafruit.com>, a cloud-based message queue and storage.
    You can send values to feeds on your Adafruit IO account and read the
    values of those feeds as well through any device.

    Requires:

        * **adafruit-io** (``pip install adafruit-io``)

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

    def __init__(self, username, key, *args, **kwargs):
        """
        :param username: Your Adafruit username
        :type username: str

        :param key: Your Adafruit IO key
        :type key: str
        """

        super().__init__(*args, **kwargs)
        self.aio = Client(username=username, key=key)


    @action
    def send(self, feed, value):
        """
        Send a value to an Adafruit IO feed

        :param feed: Feed name
        :type feed: str

        :param value: Value to send
        :type value: Numeric or string
        """

        self.aio.send(feed, value)


    @action
    def receive(self, feed):
        """
        Receive the most recent value from an Adafruit IO feed and returns it
        as a scalar (string or number)

        :param feed: Feed name
        :type feed: str
        """

        value = self.aio.receive(feed).value

        try:
            value = float(value)
        except ValueError:
            pass

        return value


# vim:sw=4:ts=4:et:

