import warnings

from platypush.backend import Backend


class ZigbeeMqttBackend(Backend):
    """
    Listen for events on a zigbee2mqtt service.

    **WARNING**: This backend is **DEPRECATED** and it will be removed in a
    future version.

    It has been merged with
    :class:`platypush.plugins.zigbee.mqtt.ZigbeeMqttPlugin`.

    Now you can simply configure the `zigbee.mqtt` plugin in order to enable
    the Zigbee integration - no need to enable both the plugin and the backend.
    """

    def run(self):
        super().run()
        warnings.warn(
            '''
            The zigbee.mqtt backend has been merged into the zigbee.mqtt
            plugin. It is now deprecated and it will be removed in a future
            version.
            Please remove any references to it from your configuration.
            ''',
            DeprecationWarning,
        )

        self.wait_stop()


# vim:sw=4:ts=4:et:
