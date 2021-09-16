from typing import Optional

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.adafruit import ConnectedEvent, DisconnectedEvent, \
    FeedUpdateEvent


class AdafruitIoBackend(Backend):
    """
    Backend that listens to messages received over the Adafruit IO message queue

    Triggers:

        * :class:`platypush.message.event.adafruit.ConnectedEvent` when the
            backend connects to the Adafruit queue
        * :class:`platypush.message.event.adafruit.DisconnectedEvent` when the
            backend disconnects from the Adafruit queue
        * :class:`platypush.message.event.adafruit.FeedUpdateEvent` when an
            update event is received on a monitored feed

    Requires:

        * The :class:`platypush.plugins.adafruit.io.AdafruitIoPlugin` plugin to
            be active and configured.
    """

    def __init__(self, feeds, *args, **kwargs):
        """
        :param feeds: List of feed IDs to monitor
        :type feeds: list[str]
        """

        super().__init__(*args, **kwargs)
        from Adafruit_IO import MQTTClient
        self.feeds = feeds
        self._client: Optional[MQTTClient] = None

    def _init_client(self):
        if self._client:
            return

        from Adafruit_IO import MQTTClient
        plugin = get_plugin('adafruit.io')
        if not plugin:
            raise RuntimeError('Adafruit IO plugin not configured')

        # noinspection PyProtectedMember
        self._client = MQTTClient(plugin._username, plugin._key)
        self._client.on_connect = self.on_connect()
        self._client.on_disconnect = self.on_disconnect()
        self._client.on_message = self.on_message()

    def on_connect(self):
        def _handler(client):
            for feed in self.feeds:
                client.subscribe(feed)
            self.bus.post(ConnectedEvent())

        return _handler

    def on_disconnect(self):
        def _handler(*_, **__):
            self.bus.post(DisconnectedEvent())

        return _handler

    def on_message(self, *_, **__):
        # noinspection PyUnusedLocal
        def _handler(client, feed, data):
            try:
                data = float(data)
            except Exception as e:
                self.logger.debug('Not a number: {}: {}'.format(data, e))

            self.bus.post(FeedUpdateEvent(feed=feed, data=data))

        return _handler

    def run(self):
        super().run()

        self.logger.info(('Initialized Adafruit IO backend, listening on ' +
                          'feeds {}').format(self.feeds))

        while not self.should_stop():
            try:
                self._init_client()
                # noinspection PyUnresolvedReferences
                self._client.connect()
                # noinspection PyUnresolvedReferences
                self._client.loop_blocking()
            except Exception as e:
                self.logger.exception(e)
                self._client = None

# vim:sw=4:ts=4:et:
