import threading

from typing import Optional, List, Any, Dict

from platypush.plugins.mqtt import MqttPlugin, action


class ZigbeeMqttPlugin(MqttPlugin):
    """
    This plugin allows you to interact with Zigbee devices over MQTT through any Zigbee sniffer and
    `zigbee2mqtt <https://www.zigbee2mqtt.io/>`_.

    In order to get started you'll need:

        - A Zigbee USB adapter/sniffer (in this example I'll use the `CC2531 <https://hackaday.io/project/163487-zigbee-cc2531-smart-home-usb-adapter>`_.
        - A Zigbee debugger/emulator + downloader cable (only to flash the firmware).

    Instructions:

        - Install `cc-tool <https://github.com/dashesy/cc-tool>`_ either from sources or from a package manager.
        - Connect the Zigbee to your PC/RaspberryPi in this way: USB -> CC debugger -> downloader cable -> CC2531 -> USB.
          The debugger and the adapter should be connected *at the same time*. If the later ``cc-tool`` command throws up
          an error, put the device in sync while connected by pressing the _Reset_ button on the debugger.
        - Check where the device is mapped. On Linux it will usually be ``/dev/ttyACM0``.
        - Download the latest `Z-Stack firmware <https://github.com/Koenkk/Z-Stack-firmware/tree/master/coordinator>`_ to your device.
          Instructions for a CC2531 device:

          .. code-block:: shell

              wget https://github.com/Koenkk/Z-Stack-firmware/raw/master/coordinator/Z-Stack_Home_1.2/bin/default/CC2531_DEFAULT_20190608.zip
              unzip CC2531_DEFAULT_20190608.zip
              [sudo] cc-tool -e -w CC2531ZNP-Prod.hex

        - You can disconnect your debugger and downloader cable once the firmware is flashed.

        - Install ``zigbee2mqtt``. First install a node/npm environment, then either install ``zigbee2mqtt`` manually or through your
          package manager. Manual instructions:

          .. code-block:: shell

              # Clone zigbee2mqtt repository
              [sudo] git clone https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt
              [sudo] chown -R pi:pi /opt/zigbee2mqtt  # Or whichever is your user

              # Install dependencies (as user "pi")
              cd /opt/zigbee2mqtt
              npm install

        - You need to have an MQTT broker running somewhere. If not, you can install
            `Mosquitto <https://mosquitto.org/>`_ through your package manager on any device in your network.

        - Edit the ``/opt/zigbee2mqtt/data/configuration.yaml`` file to match the configuration of your MQTT broker:

          .. code-block:: yaml

              # MQTT settings
              mqtt:
                  # MQTT base topic for zigbee2mqtt MQTT messages
                  base_topic: zigbee2mqtt
                  # MQTT server URL
                  server: 'mqtt://localhost'
                  # MQTT server authentication, uncomment if required:
                  # user: my_user
                  # password: my_password

        - Also make sure that ``permit_join`` is set to ``True``, in order to allow Zigbee devices to join the network
          while you're configuring it. It's equally important to set ``permit_join`` to ``False`` once you have
          configured your network, to prevent accidental/malignant joins from outer Zigbee devices.

        - Start the ``zigbee2mqtt`` daemon on your device (the
          `official documentation <https://www.zigbee2mqtt.io/getting_started/running_zigbee2mqtt.html#5-optional-running-as-a-daemon-with-systemctl>`_
          also contains instructions on how to configure it as a ``systemd`` service:

          .. code-block:: shell

              cd /opt/zigbee2mqtt
              npm start

        - If you have Zigbee devices that are paired to other bridges, unlink them or do a factory reset to pair them
          to your new bridge.

        - If it all goes fine, once the daemon is running and a new device is found you should see traces like this in
          the output of ``zigbee2mqtt``::

            zigbee2mqtt:info  2019-11-09T12:19:56: Successfully interviewed '0x00158d0001dc126a', device has successfully been paired

        - You are now ready to use this integration.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)

    """

    def __init__(self, host: str = 'localhost', port: int = 1883, base_topic: str = 'zigbee2mqtt', timeout: int = 60,
                 tls_certfile: Optional[str] = None, tls_keyfile: Optional[str] = None,
                 tls_version: Optional[str] = None, tls_ciphers: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None, **kwargs):
        """
        :param host: Default MQTT broker where ``zigbee2mqtt`` publishes its messages (default: ``localhost``).
        :param port: Broker listen port (default: 1883).
        :param base_topic: Topic prefix, as specified in ``/opt/zigbee2mqtt/data/configuration.yaml``
            (default: '``base_topic``').
        :param timeout: If the command expects from a response, then this timeout value will be used
            (default: 60 seconds).
        :param tls_cafile: If the connection requires TLS/SSL, specify the certificate authority file
            (default: None)
        :param tls_certfile: If the connection requires TLS/SSL, specify the certificate file (default: None)
        :param tls_keyfile: If the connection requires TLS/SSL, specify the key file (default: None)
        :param tls_version: If the connection requires TLS/SSL, specify the minimum TLS supported version
            (default: None)
        :param tls_ciphers: If the connection requires TLS/SSL, specify the supported ciphers (default: None)
        :param username: If the connection requires user authentication, specify the username (default: None)
        :param password: If the connection requires user authentication, specify the password (default: None)
        """

        super().__init__(host=host, port=port, tls_certfile=tls_certfile, tls_keyfile=tls_keyfile,
                         tls_version=tls_version, tls_ciphers=tls_ciphers, username=username,
                         password=password, **kwargs)

        self.base_topic = base_topic
        self.timeout = timeout

    def _mqtt_args(self, host: Optional[str] = None, **kwargs):
        if not host:
            return {
                'host': self.host,
                'port': self.port,
                'timeout': self.timeout,
                'tls_certfile': self.tls_certfile,
                'tls_keyfile': self.tls_keyfile,
                'tls_version': self.tls_version,
                'tls_ciphers': self.tls_ciphers,
                'username': self.username,
                'password': self.password,
            }

        return kwargs

    def _topic(self, topic):
        return self.base_topic + '/' + topic

    @action
    def devices(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get the list of devices registered to the service.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).

        :return: List of paired devices. Example output:

        .. code-block:: json

            [
                {
                    "dateCode": "20190608",
                    "friendly_name": "Coordinator",
                    "ieeeAddr": "0x00123456789abcde",
                    "lastSeen": 1579640601215,
                    "networkAddress": 0,
                    "softwareBuildID": "zStack12",
                    "type": "Coordinator"
                },
                {
                    "dateCode": "20160906",
                    "friendly_name": "My Lightbulb",
                    "hardwareVersion": 1,
                    "ieeeAddr": "0x00123456789abcdf",
                    "lastSeen": 1579595191623,
                    "manufacturerID": 4107,
                    "manufacturerName": "Philips",
                    "model": "8718696598283",
                    "modelID": "LTW013",
                    "networkAddress": 52715,
                    "powerSource": "Mains (single phase)",
                    "softwareBuildID": "1.15.2_r19181",
                    "type": "Router"
                }
            ]

        """
        return self.publish(
            topic=self._topic('bridge/config/devices/get'), msg='',
            reply_topic=self._topic('bridge/config/devices'),
            **self._mqtt_args(**kwargs))

    def _permit_join_timeout_callback(self, permit: bool, **kwargs):
        def callback():
            self.logger.info('Restoring permit_join state to {}'.format(permit))
            self.permit_join(permit, **kwargs)
        return callback

    @action
    def permit_join(self, permit: bool = True, timeout: Optional[float] = None, **kwargs):
        """
        Enable/disable devices from joining the network. This is not persistent (will not be saved to
        ``configuration.yaml``).

        :param permit: Set to True to allow joins, False otherwise.
        :param timeout: Allow/disallow joins only for this amount of time.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/permit_join'), msg=permit, **self._mqtt_args(**kwargs))
        if timeout:
            threading.Timer(timeout, self._permit_join_timeout_callback(not permit, **kwargs)).start()

    @action
    def reset(self, **kwargs):
        """
        Reset the adapter.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/reset'), msg='', **self._mqtt_args(**kwargs))

    @action
    def factory_reset(self, **kwargs):
        """
        Perform a factory reset of the device. Of course, you should only do it if you know what you're doing,
        as you will lose all the paired devices and may also lose the Z-Stack firmware.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/factory_reset'), msg='', **self._mqtt_args(**kwargs))

    @action
    def log_level(self, level: str, **kwargs):
        """
        Change the log level at runtime. This change will not be persistent.

        :param level: Possible values: 'debug', 'info', 'warn', 'error'.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/log_level'), msg=level, **self._mqtt_args(**kwargs))

    @action
    def device_set_option(self, device: str, option: str, value: Any, **kwargs):
        """
        Change the options of a device. Options can only be changed, not added or deleted.

        :param device: Display name of the device.
        :param option: Option name.
        :param value: New value.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/device_options'), msg={
            'friendly_name': device,
            'options': {
                option: value,
            }
        }, **self._mqtt_args(**kwargs))

    @action
    def device_remove(self, device: str, force: bool = False, **kwargs):
        """
        Remove a device from the network.

        :param device: Display name of the device.
        :param force: Force the remove also if the removal wasn't acknowledged by the device. Note: a forced remove
            only removes the entry from the internal database, but the device is likely to connect again when
            restarted unless it's factory reset (default: False).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        topic = self._topic('bridge/config/{}remove'.format('force_' if force else ''))
        self.publish(topic=topic, msg=device, **self._mqtt_args(**kwargs))

    @action
    def device_ban(self, device: str, **kwargs):
        """
        Ban a device from the network.

        :param device: Display name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/ban'), msg=device, **self._mqtt_args(**kwargs))

    @action
    def device_whitelist(self, device: str, **kwargs):
        """
        Whitelist a device on the network. Note: once at least a device is whitelisted, all the other non-whitelisted
        devices will be removed from the network.

        :param device: Display name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/whitelist'), msg=device, **self._mqtt_args(**kwargs))

    @action
    def device_rename(self, name: str, device: Optional[str] = None, **kwargs):
        """
        Rename a device on the network.

        :param name: New name.
        :param device: Current name of the device to rename. If no name is specified then the rename will
            affect the last device that joined the network.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if name == device:
            self.logger.info('Old and new name are the same: nothing to do')
            return

        # noinspection PyUnresolvedReferences
        devices = self.devices().output
        assert not [dev for dev in devices if dev.get('friendly_name') == name], \
            'A device named {} already exists on the network'.format(name)

        self.publish(
            topic=self._topic('bridge/config/rename{}'.format('_last' if not device else '')),
            msg={'old': device, 'new': name} if device else name,
            **self._mqtt_args(**kwargs))

    # noinspection PyShadowingBuiltins
    @action
    def device_get(self, device: str, property: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get the properties of a device. The returned keys vary depending on the device. For example, a light bulb
        may have the "``state``" and "``brightness``" properties, while an environment sensor may have the
        "``temperature``" and "``humidity``" properties, and so on.

        :param device: Display name of the device.
        :param property: Name of the property that should be retrieved (default: all).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        :return: Key->value map of the device properties.
        """
        properties = self.publish(topic=self._topic(device + '/get'),
                                  reply_topic=self._topic(device), msg='', **self._mqtt_args(**kwargs)).output

        if property:
            assert property in properties, 'No such property: ' + property
            return {property: properties[property]}

        return properties

    # noinspection PyShadowingBuiltins,DuplicatedCode
    @action
    def device_set(self, device: str, property: str, value: Any, **kwargs):
        """
        Set a properties on a device. The compatible properties vary depending on the device. For example, a light bulb
        may have the "``state``" and "``brightness``" properties, while an environment sensor may have the
        "``temperature``" and "``humidity``" properties, and so on.

        :param device: Display name of the device.
        :param property: Name of the property that should be set.
        :param value: New value of the property.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        properties = self.publish(topic=self._topic(device + '/set'),
                                  reply_topic=self._topic(device),
                                  msg={property: value}, **self._mqtt_args(**kwargs)).output

        if property:
            assert property in properties, 'No such property: ' + property
            return {property: properties[property]}

        return properties

    @action
    def device_groups(self, device: str, **kwargs) -> List[int]:
        """
        List the groups a given device belongs to.

        :param device: Display name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        :return: List of group IDs the device is linked to.
        """

        return self.publish(topic=self._topic('bridge/device/{}/get_group_membership'.format(device)),
                            reply_topic=self._topic(device), msg=device, **self._mqtt_args(**kwargs)).\
            output.get('group_list', [])

    @action
    def groups(self, **kwargs):
        """
        Get the groups registered on the device.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        groups = self.publish(topic=self._topic('bridge/config/groups'), msg={},
                              reply_topic=self._topic('bridge/log'),
                              **self._mqtt_args(**kwargs)).output.get('message', [])

        # noinspection PyUnresolvedReferences
        devices = {
            device['ieeeAddr']: device
            for device in self.devices(**kwargs).output
        }

        return [
            {
                'id': group['ID'],
                'friendly_name': group['friendly_name'],
                'optimistic': group.get('optimistic', False),
                'devices': [
                    devices[device.split('/')[0]]
                    for device in group.get('devices', [])
                ]
            }
            for group in groups
        ]

    @action
    def group_add(self, name: str, id: Optional[int] = None, **kwargs):
        """
        Add a new group.

        :param name: Display name of the group.
        :param id: Optional numeric ID (default: auto-generated).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        args = {'friendly_name': name}
        if id is not None:
            args['id'] = id

        self.publish(topic=self._topic('bridge/config/add_group'), msg=args, **self._mqtt_args(**kwargs))

    # noinspection PyShadowingBuiltins,DuplicatedCode
    @action
    def group_set(self, group: str, property: str, value: Any, **kwargs):
        """
        Set a properties on a group. The compatible properties vary depending on the devices on the group.
        For example, a light bulb may have the "``state``" (with values ``"ON"`` and ``"OFF"``) and "``brightness``"
        properties, while an environment sensor may have the "``temperature``" and "``humidity``" properties, and so on.

        :param group: Display name of the group.
        :param property: Name of the property that should be set.
        :param value: New value of the property.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        properties = self.publish(topic=self._topic(group + '/set'),
                                  reply_topic=self._topic(group),
                                  msg={property: value}, **self._mqtt_args(**kwargs)).output

        if property:
            assert property in properties, 'No such property: ' + property
            return {property: properties[property]}

        return properties

    @action
    def group_rename(self, name: str, group: str, **kwargs):
        """
        Rename a group.

        :param name: New name.
        :param group: Current name of the group to rename.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        if name == group:
            self.logger.info('Old and new name are the same: nothing to do')
            return

        # noinspection PyUnresolvedReferences
        groups = {group.get('friendly_name'): group for group in self.groups().output}
        assert name not in groups, 'A group named {} already exists on the network'.format(name)

        self.publish(
            topic=self._topic('bridge/config/rename'),
            msg={'old': group, 'new': name} if group else name,
            **self._mqtt_args(**kwargs))

    @action
    def group_remove(self, name: str, **kwargs):
        """
        Remove a group.

        :param name: Display name of the group.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/config/remove_group'), msg=name,
                     **self._mqtt_args(**kwargs))

    @action
    def group_add_device(self, group: str, device: str, **kwargs):
        """
        Add a device to a group.

        :param group: Display name of the group.
        :param device: Display name of the device to be added.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/group/{}/add'.format(group)),
                     msg=device, **self._mqtt_args(**kwargs))

    @action
    def group_remove_device(self, group: str, device: Optional[str] = None, **kwargs):
        """
        Remove a device from a group.

        :param group: Display name of the group.
        :param device: Display name of the device to be removed. If none is specified then all the devices registered
            to the specified group will be removed.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/group/{}/remove{}'.format(group, '_all' if not device else '')),
                     msg=device, **self._mqtt_args(**kwargs))

    @action
    def bind_devices(self, source: str, target: str, endpoint: Optional[str] = None, **kwargs):
        """
        Bind two devices. Binding makes it possible that devices can directly control each other without the
        intervention of zigbee2mqtt or any home automation software. You may want to use this feature to bind
        for example an IKEA/Philips Hue dimmer switch to a light bulb, or a Zigbee remote to a thermostat.
        Read more on the `zigbee2mqtt binding page <https://www.zigbee2mqtt.io/information/binding.html>`_.

        :param source: Name of the source device. It can also be a group name, although the support is
            `still experimental <https://www.zigbee2mqtt.io/information/binding.html#binding-a-group>`_.
        :param target: Name of the target device.
        :param endpoint: The target may support multiple endpoints (e.g. 'left', 'down', 'up' etc.). If so,
            you can bind the source to a specific endpoint on the target device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/bind/' + source + ('/' + endpoint if endpoint else '')),
                     msg=target, **self._mqtt_args(**kwargs))

    @action
    def unbind_devices(self, source: str, target: str, **kwargs):
        """
        Un-bind two devices.

        :param source: Name of the source device.
        :param target: Name of the target device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/unbind/' + source),
                     msg=target, **self._mqtt_args(**kwargs))


# vim:sw=4:ts=4:et:
