import json
import threading

from queue import Queue
from typing import Optional, List, Any, Dict, Union

from platypush.message.response import Response
from platypush.plugins.mqtt import MqttPlugin, action
from platypush.plugins.switch import SwitchPlugin


class ZigbeeMqttPlugin(MqttPlugin, SwitchPlugin):
    """
    This plugin allows you to interact with Zigbee devices over MQTT through any Zigbee sniffer and
    `zigbee2mqtt <https://www.zigbee2mqtt.io/>`_.

    In order to get started you'll need:

        - A Zigbee USB adapter/sniffer (in this example I'll use the
          `CC2531 <https://hackaday.io/project/163487-zigbee-cc2531-smart-home-usb-adapter>`_.
        - A Zigbee debugger/emulator + downloader cable (only to flash the firmware).

    Instructions:

        - Install `cc-tool <https://github.com/dashesy/cc-tool>`_ either from sources or from a package manager.
        - Connect the Zigbee to your PC/RaspberryPi in this way:
            USB -> CC debugger -> downloader cable -> CC2531 -> USB
          The debugger and the adapter should be connected *at the same time*. If the later ``cc-tool`` command throws
          up an error, put the device in sync while connected by pressing the _Reset_ button on the debugger.
        - Check where the device is mapped. On Linux it will usually be ``/dev/ttyACM0``.
        - Download the latest `Z-Stack firmware <https://github.com/Koenkk/Z-Stack-firmware/tree/master/coordinator>`_
          to your device. Instructions for a CC2531 device:

          .. code-block:: shell

              wget https://github.com/Koenkk/Z-Stack-firmware/raw/master/coordinator/Z-Stack_Home_1.2/bin/default/CC2531_DEFAULT_20201127.zip
              unzip CC2531_DEFAULT_20201127.zip
              [sudo] cc-tool -e -w CC2531ZNP-Prod.hex

        - You can disconnect your debugger and downloader cable once the firmware is flashed.

        - Install ``zigbee2mqtt``. First install a node/npm environment, then either install ``zigbee2mqtt`` manually or
          through your package manager. **NOTE**: many API breaking changes have occurred on Zigbee2MQTT 1.17.0,
          therefore this integration will only be compatible with the version 1.17.0 of the service or higher versions.
          Manual instructions:

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

            zigbee2mqtt:info  2019-11-09T12:19:56: Successfully interviewed '0x00158d0001dc126a', device has
            successfully been paired

        - You are now ready to use this integration.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)

    """

    def __init__(self, host: str = 'localhost', port: int = 1883, base_topic: str = 'zigbee2mqtt', timeout: int = 10,
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
        self._info = {
            'devices': {},
            'groups': {},
        }

    def _get_network_info(self, **kwargs):
        self.logger.info('Fetching Zigbee network information')
        client = None
        mqtt_args = self._mqtt_args(**kwargs)
        timeout = 30
        if 'timeout' in mqtt_args:
            timeout = mqtt_args.pop('timeout')

        info = {
            'state': None,
            'info': {},
            'config': {},
            'devices': [],
            'groups': [],
        }

        info_ready_events = {topic: threading.Event() for topic in info.keys()}

        def _on_message():
            def callback(_, __, msg):
                topic = msg.topic.split('/')[-1]
                if topic in info:
                    info[topic] = msg.payload.decode() if topic == 'state' else json.loads(msg.payload.decode())
                    info_ready_events[topic].set()

            return callback

        try:
            host = mqtt_args.pop('host')
            port = mqtt_args.pop('port')
            client = self._get_client(**mqtt_args)
            client.on_message = _on_message()
            client.connect(host, port, keepalive=timeout)
            client.subscribe(self.base_topic + '/bridge/#')
            client.loop_start()

            for event in info_ready_events.values():
                info_ready = event.wait(timeout=timeout)
                if not info_ready:
                    raise TimeoutError('A timeout occurred while fetching the Zigbee network information')

            # Cache the new results
            self._info['devices'] = {
                device.get('friendly_name', device['ieee_address']): device
                for device in info.get('devices', [])
            }

            self._info['groups'] = {
                group.get('name'): group
                for group in info.get('groups', [])
            }

            self.logger.info('Zigbee network configuration updated')
            return info
        finally:
            try:
                client.loop_stop()
                client.disconnect()
            except Exception as e:
                self.logger.warning('Error on MQTT client disconnection: {}'.format(str(e)))

    def _mqtt_args(self, **kwargs):
        return {
            'host': kwargs.get('host', self.host),
            'port': kwargs.get('port', self.port),
            'timeout': kwargs.get('timeout', self.timeout),
            'tls_certfile': kwargs.get('tls_certfile', self.tls_certfile),
            'tls_keyfile': kwargs.get('tls_keyfile', self.tls_keyfile),
            'tls_version': kwargs.get('tls_version', self.tls_version),
            'tls_ciphers': kwargs.get('tls_ciphers', self.tls_ciphers),
            'username': kwargs.get('username', self.username),
            'password': kwargs.get('password', self.password),
        }

    def _topic(self, topic):
        return self.base_topic + '/' + topic

    @staticmethod
    def _parse_response(response: Union[dict, Response]) -> dict:
        if isinstance(response, Response):
            response = response.output

        assert response.get('status') != 'error', response.get('error', 'zigbee2mqtt error')
        return response

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
                    "date_code": "20190608",
                    "friendly_name": "Coordinator",
                    "ieee_address": "0x00123456789abcde",
                    "network_address": 0,
                    "supported": false,
                    "type": "Coordinator",
                    "interviewing": false,
                    "interviewing_completed": true,
                    "definition": null,
                    "endpoints": {
                        "13": {
                            "bindings": [],
                            "clusters": {
                                "input": ["genOta"],
                                "output": []
                            },
                            "output": []
                        }
                    }
                },

                {
                    "date_code": "20180906",
                    "friendly_name": "My Lightbulb",
                    "ieee_address": "0x00123456789abcdf",
                    "network_address": 52715,
                    "power_source": "Mains (single phase)",
                    "software_build_id": "5.127.1.26581",
                    "model_id": "LCT001",
                    "supported": true,
                    "interviewing": false,
                    "interviewing_completed": true,
                    "type": "Router",
                    "definition": {
                        "description": "Hue white and color ambiance E26/E27/E14",
                        "model": "9290012573A",
                        "vendor": "Philips",
                        "exposes": [
                            {
                                "features": [
                                    {
                                        "access": 7,
                                        "description": "On/off state of this light",
                                        "name": "state",
                                        "property": "state",
                                        "type": "binary",
                                        "value_off": "OFF",
                                        "value_on": "ON",
                                        "value_toggle": "TOGGLE"
                                    },
                                    {
                                        "access": 7,
                                        "description": "Brightness of this light",
                                        "name": "brightness",
                                        "property": "brightness",
                                        "type": "numeric",
                                        "value_max": 254,
                                        "value_min": 0
                                    },
                                    {
                                        "access": 7,
                                        "description": "Color temperature of this light",
                                        "name": "color_temp",
                                        "property": "color_temp",
                                        "type": "numeric",
                                        "unit": "mired",
                                        "value_max": 500,
                                        "value_min": 150
                                    },
                                    {
                                        "description": "Color of this light in the CIE 1931 color space (x/y)",
                                        "features": [
                                            {
                                                "access": 7,
                                                "name": "x",
                                                "property": "x",
                                                "type": "numeric"
                                            },
                                            {
                                                "access": 7,
                                                "name": "y",
                                                "property": "y",
                                                "type": "numeric"
                                            }
                                        ],
                                        "name": "color_xy",
                                        "property": "color",
                                        "type": "composite"
                                    }
                                ],
                                "type": "light"
                            },
                            {
                                "access": 2,
                                "description": "Triggers an effect on the light (e.g. make light blink for a few seconds)",
                                "name": "effect",
                                "property": "effect",
                                "type": "enum",
                                "values": [
                                    "blink",
                                    "breathe",
                                    "okay",
                                    "channel_change",
                                    "finish_effect",
                                    "stop_effect"
                                ]
                            },
                            {
                                "access": 1,
                                "description": "Link quality (signal strength)",
                                "name": "linkquality",
                                "property": "linkquality",
                                "type": "numeric",
                                "unit": "lqi",
                                "value_max": 255,
                                "value_min": 0
                            }
                        ]
                    },

                    "endpoints": {
                        "11": {
                            "bindings": [],
                            "clusters": {
                                "input": [
                                    "genBasic",
                                    "genIdentify",
                                    "genGroups",
                                    "genScenes",
                                    "genOnOff",
                                    "genLevelCtrl",
                                    "touchlink",
                                    "lightingColorCtrl",
                                    "manuSpecificUbisysDimmerSetup"
                                ],
                                "output": [
                                    "genOta"
                                ]
                            },
                            "configured_reportings": []
                        },
                        "242": {
                            "bindings": [],
                            "clusters": {
                                "input": [
                                    "greenPower"
                                ],
                                "output": [
                                    "greenPower"
                                ]
                            },
                            "configured_reportings": []
                        }
                    }
                }
            ]

        """
        return self._get_network_info(**kwargs).get('devices')

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
        if timeout:
            return self._parse_response(
                self.publish(topic=self._topic('bridge/request/permit_join'),
                             msg={'value': permit, 'time': timeout},
                             reply_topic=self._topic('bridge/response/permit_join'),
                             **self._mqtt_args(**kwargs)))

        return self.publish(topic=self._topic('bridge/request/permit_join'),
                            msg={'value': permit},
                            **self._mqtt_args(**kwargs))

    @action
    def factory_reset(self, **kwargs):
        """
        Perform a factory reset of a device connected to the network, following the procedure required by the particular
        device (for instance, Hue bulbs require the Zigbee adapter to be close to the device while a button on the back
        of the bulb is pressed).

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(topic=self._topic('bridge/request/touchlink/factory_reset'), msg='', **self._mqtt_args(**kwargs))

    @action
    def log_level(self, level: str, **kwargs):
        """
        Change the log level at runtime. This change will not be persistent.

        :param level: Possible values: 'debug', 'info', 'warn', 'error'.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/config/log_level'), msg={'value': level},
                         reply_topic=self._topic('bridge/response/config/log_level'),
                         **self._mqtt_args(**kwargs)))

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
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/options'),
                         reply_topic=self._topic('bridge/response/device/options'),
                         msg={
                             'id': device,
                             'options': {
                                 option: value,
                             }
                         }, **self._mqtt_args(**kwargs)))

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
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/remove'),
                         msg={'id': device, 'force': force},
                         reply_topic=self._topic('bridge/response/device/remove'),
                         **self._mqtt_args(**kwargs)))

    @action
    def device_ban(self, device: str, **kwargs):
        """
        Ban a device from the network.

        :param device: Display name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/ban'),
                         reply_topic=self._topic('bridge/response/device/ban'),
                         msg={'id': device},
                         **self._mqtt_args(**kwargs)))

    @action
    def device_whitelist(self, device: str, **kwargs):
        """
        Whitelist a device on the network. Note: once at least a device is whitelisted, all the other non-whitelisted
        devices will be removed from the network.

        :param device: Display name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/whitelist'),
                         reply_topic=self._topic('bridge/response/device/whitelist'),
                         msg={'id': device},
                         **self._mqtt_args(**kwargs)))

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

        if device:
            req = {
                'from': device,
                'to': name,
            }
        else:
            req = {
                'last': True,
                'to': name,
            }

        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/rename'),
                         msg=req,
                         reply_topic=self._topic('bridge/response/device/rename'),
                         **self._mqtt_args(**kwargs)))

    @staticmethod
    def build_device_get_request(values: List[Dict[str, Any]]) -> dict:
        def extract_value(value: dict, root: dict):
            if not value.get('access', 1) & 0x1:
                # Property not readable
                return

            if 'features' not in value:
                if 'property' in value:
                    root[value['property']] = 0 if value['type'] == 'numeric' else ''
                return

            if 'property' in value:
                root[value['property']] = root.get(value['property'], {})
                root = root[value['property']]

            for feature in value['features']:
                extract_value(feature, root)

        ret = {}
        for value in values:
            extract_value(value, root=ret)

        return ret

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
        kwargs = self._mqtt_args(**kwargs)

        if property:
            properties = self.publish(topic=self._topic(device) + '/get/' + property, reply_topic=self._topic(device),
                                      msg={property: ''}, **kwargs).output

            assert property in properties, 'No such property: ' + property
            return {property: properties[property]}

        if device not in self._info.get('devices', {}):
            # Refresh devices info
            self._get_network_info(**kwargs)

        assert self._info.get('devices', {}).get(device), 'No such device: ' + device
        exposes = (self._info.get('devices', {}).get(device, {}).get('definition', {}) or {}).get('exposes', [])
        if not exposes:
            return {}

        return self.publish(topic=self._topic(device) + '/get', reply_topic=self._topic(device),
                            msg=self.build_device_get_request(exposes), **kwargs)

    @action
    def devices_get(self, devices: Optional[List[str]] = None, **kwargs) -> Dict[str, dict]:
        """
        Get the properties of the devices connected to the network. *NOTE*: Use this function instead of :meth:`.status`
        if you want to retrieve the status of *all* the components associated to the network - :meth:`.status` only
        returns the status of the devices with a writable ``ON``/``OFF`` ``state`` property.

        :param devices: If set, then only the status of these devices (by friendly name) will be retrieved (default:
            retrieve all).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        :return: Key->value map of the device properties:

            .. code-block:: json

                {
                    "Bulb": {
                        "state": "ON",
                        "brightness": 254
                    },
                    "Sensor": {
                        "temperature": 22.5
                    }
                }
        """
        kwargs = self._mqtt_args(**kwargs)

        if not devices:
            # noinspection PyUnresolvedReferences
            devices = set([
                device['friendly_name'] or device['ieee_address']
                for device in self.devices(**kwargs).output
            ])

        def worker(device: str, q: Queue):
            # noinspection PyUnresolvedReferences
            q.put(self.device_get(device, **kwargs).output)

        queues = {}
        workers = {}
        response = {}

        for device in devices:
            queues[device] = Queue()
            workers[device] = threading.Thread(target=worker, args=(device, queues[device]))
            workers[device].start()

        for device in devices:
            try:
                response[device] = queues[device].get(timeout=kwargs.get('timeout'))
                workers[device].join(timeout=kwargs.get('timeout'))
            except Exception as e:
                self.logger.warning('An error while getting the status of the device {}: {}'.format(
                    device, str(e)))

        return response

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
    def device_check_ota_updates(self, device: str, **kwargs) -> dict:
        """
        Check if the specified device has any OTA updates available to install.

        :param device: Address or friendly name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).

        :return:

            .. code-block:: json

                {
                    "id": "<device ID>",
                    "update_available": true,
                    "status": "ok"
                }

        """
        ret = self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/ota_update/check'),
                         reply_topic=self._topic('bridge/response/device/ota_update/check'),
                         msg={'id': device}, **self._mqtt_args(**kwargs)))

        return {
            'status': ret['status'],
            'id': ret.get('data', {}).get('id'),
            'update_available': ret.get('data', {}).get('update_available', False),
        }

    @action
    def device_install_ota_updates(self, device: str, **kwargs):
        """
        Install OTA updates for a device if available.

        :param device: Address or friendly name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/ota_update/update'),
                         reply_topic=self._topic('bridge/response/device/ota_update/update'),
                         msg={'id': device}, **self._mqtt_args(**kwargs)))

    @action
    def groups(self, **kwargs) -> List[dict]:
        """
        Get the groups registered on the device.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._get_network_info(**kwargs).get('groups')

    @action
    def info(self, **kwargs) -> dict:
        """
        Get the information, configuration and state of the network.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).

        :return: Example:

            .. code-block:: json

                {
                    "state": "online",
                    "commit": "07cdc9d",
                    "config": {
                        "advanced": {
                            "adapter_concurrent": null,
                            "adapter_delay": null,
                            "availability_blacklist": [],
                            "availability_blocklist": [],
                            "availability_passlist": [],
                            "availability_timeout": 0,
                            "availability_whitelist": [],
                            "cache_state": true,
                            "cache_state_persistent": true,
                            "cache_state_send_on_startup": true,
                            "channel": 11,
                            "elapsed": false,
                            "ext_pan_id": [
                                221,
                                221,
                                221,
                                221,
                                221,
                                221,
                                221,
                                221
                            ],
                            "homeassistant_discovery_topic": "homeassistant",
                            "homeassistant_legacy_triggers": true,
                            "homeassistant_status_topic": "hass/status",
                            "last_seen": "disable",
                            "legacy_api": true,
                            "log_directory": "/opt/zigbee2mqtt/data/log/%TIMESTAMP%",
                            "log_file": "log.txt",
                            "log_level": "debug",
                            "log_output": [
                                "console",
                                "file"
                            ],
                            "log_rotation": true,
                            "log_syslog": {},
                            "pan_id": 6754,
                            "report": false,
                            "soft_reset_timeout": 0,
                            "timestamp_format": "YYYY-MM-DD HH:mm:ss"
                        },
                        "ban": [],
                        "blocklist": [],
                        "device_options": {},
                        "devices": {
                            "0x00123456789abcdf": {
                                "friendly_name": "My Lightbulb"
                            }
                        },
                        "experimental": {
                            "output": "json"
                        },
                        "external_converters": [],
                        "groups": {},
                        "homeassistant": false,
                        "map_options": {
                            "graphviz": {
                                "colors": {
                                    "fill": {
                                        "coordinator": "#e04e5d",
                                        "enddevice": "#fff8ce",
                                        "router": "#4ea3e0"
                                    },
                                    "font": {
                                        "coordinator": "#ffffff",
                                        "enddevice": "#000000",
                                        "router": "#ffffff"
                                    },
                                    "line": {
                                        "active": "#009900",
                                        "inactive": "#994444"
                                    }
                                }
                            }
                        },
                        "mqtt": {
                            "base_topic": "zigbee2mqtt",
                            "force_disable_retain": false,
                            "include_device_information": false,
                            "server": "mqtt://localhost"
                        },
                        "passlist": [],
                        "permit_join": true,
                        "serial": {
                            "disable_led": false,
                            "port": "/dev/ttyUSB0"
                        },
                        "whitelist": []
                    },
                    "coordinator": {
                        "meta": {
                            "maintrel": 3,
                            "majorrel": 2,
                            "minorrel": 6,
                            "product": 0,
                            "revision": 20190608,
                            "transportrev": 2
                        },
                        "type": "zStack12"
                    },
                    "log_level": "debug",
                    "network": {
                        "channel": 11,
                        "extended_pan_id": "0xdddddddddddddddd",
                        "pan_id": 6754
                    },
                    "permit_join": true,
                    "version": "1.17.0"
                }

        """
        info = self._get_network_info(**kwargs)
        return {
            'state': info.get('state'),
            'info': info.get('info'),
        }

    @action
    def group_add(self, name: str, id: Optional[int] = None, **kwargs):
        """
        Add a new group.

        :param name: Display name of the group.
        :param id: Optional numeric ID (default: auto-generated).
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        payload = name if id is None else {
            'id': id,
            'friendly_name': name,
        }

        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/group/add'),
                         reply_topic=self._topic('bridge/response/group/add'),
                         msg=payload,
                         **self._mqtt_args(**kwargs))
        )

    @action
    def group_get(self, group: str, property: Optional[str] = None, **kwargs) -> dict:
        """
        Get one or more properties of a group. The compatible properties vary depending on the devices on the group.
        For example, a light bulb may have the "``state``" (with values ``"ON"`` and ``"OFF"``) and "``brightness``"
        properties, while an environment sensor may have the "``temperature``" and "``humidity``" properties, and so on.

        :param group: Display name of the group.
        :param property: Name of the property to retrieve (default: all available properties)
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        msg = {}
        if property:
            msg = {property: ''}

        properties = self.publish(topic=self._topic(group + '/get'),
                                  reply_topic=self._topic(group),
                                  msg=msg, **self._mqtt_args(**kwargs)).output

        if property:
            assert property in properties, 'No such property: ' + property
            return {property: properties[property]}

        return properties

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

        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/group/rename'),
                         reply_topic=self._topic('bridge/response/group/rename'),
                         msg={'from': group, 'to': name} if group else name,
                         **self._mqtt_args(**kwargs)))

    @action
    def group_remove(self, name: str, **kwargs):
        """
        Remove a group.

        :param name: Display name of the group.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/group/remove'),
                         reply_topic=self._topic('bridge/response/group/remove'),
                         msg=name,
                         **self._mqtt_args(**kwargs)))

    @action
    def group_add_device(self, group: str, device: str, **kwargs):
        """
        Add a device to a group.

        :param group: Display name of the group.
        :param device: Display name of the device to be added.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/group/members/add'),
                         reply_topic=self._topic('bridge/response/group/members/add'),
                         msg={
                             'group': group,
                             'device': device,
                         }, **self._mqtt_args(**kwargs)))

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
        return self._parse_response(
            self.publish(
                topic=self._topic('bridge/request/group/members/remove{}'.format('_all' if device is None else '')),
                reply_topic=self._topic(
                    'bridge/response/group/members/remove{}'.format('_all' if device is None else '')),
                msg={
                    'group': group,
                    'device': device,
                }, **self._mqtt_args(**kwargs)))

    @action
    def bind_devices(self, source: str, target: str, **kwargs):
        """
        Bind two devices. Binding makes it possible that devices can directly control each other without the
        intervention of zigbee2mqtt or any home automation software. You may want to use this feature to bind
        for example an IKEA/Philips Hue dimmer switch to a light bulb, or a Zigbee remote to a thermostat.
        Read more on the `zigbee2mqtt binding page <https://www.zigbee2mqtt.io/information/binding.html>`_.

        :param source: Name of the source device. It can also be a group name, although the support is
            `still experimental <https://www.zigbee2mqtt.io/information/binding.html#binding-a-group>`_.
            You can also bind a specific device endpoint - for example ``MySensor/temperature``.
        :param target: Name of the target device.
            You can also bind a specific device endpoint - for example ``MyLight/state``.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/bind'),
                         reply_topic=self._topic('bridge/response/device/bind'),
                         msg={'from': source, 'to': target}, **self._mqtt_args(**kwargs)))

    @action
    def unbind_devices(self, source: str, target: str, **kwargs):
        """
        Un-bind two devices.

        :param source: Name of the source device.
            You can also bind a specific device endpoint - for example ``MySensor/temperature``.
        :param target: Name of the target device.
            You can also bind a specific device endpoint - for example ``MyLight/state``.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(topic=self._topic('bridge/request/device/unbind'),
                         reply_topic=self._topic('bridge/response/device/unbind'),
                         msg={'from': source, 'to': target}, **self._mqtt_args(**kwargs)))

    @action
    def on(self, device, *args, **kwargs) -> dict:
        """
        Implements :meth:`platypush.plugins.switch.plugin.SwitchPlugin.on` and turns on a Zigbee device with a writable
        binary property.
        """
        switch_info = self._get_switches_info().get(device)
        assert switch_info, '{} is not a valid switch'.format(device)
        props = self.device_set(device, switch_info['property'], switch_info['value_on']).output
        return self._properties_to_switch(device=device, props=props, switch_info=switch_info)

    @action
    def off(self, device, *args, **kwargs) -> dict:
        """
        Implements :meth:`platypush.plugins.switch.plugin.SwitchPlugin.off` and turns off a Zigbee device with a
        writable binary property.
        """
        switch_info = self._get_switches_info().get(device)
        assert switch_info, '{} is not a valid switch'.format(device)
        props = self.device_set(device, switch_info['property'], switch_info['value_off']).output
        return self._properties_to_switch(device=device, props=props, switch_info=switch_info)

    @action
    def toggle(self, device, *args, **kwargs) -> dict:
        """
        Implements :meth:`platypush.plugins.switch.plugin.SwitchPlugin.toggle` and toggles a Zigbee device with a
        writable binary property.
        """
        switch_info = self._get_switches_info().get(device)
        assert switch_info, '{} is not a valid switch'.format(device)
        props = self.device_set(device, switch_info['property'], switch_info['value_toggle']).output
        return self._properties_to_switch(device=device, props=props, switch_info=switch_info)

    @staticmethod
    def _properties_to_switch(device: str, props: dict, switch_info: dict) -> dict:
        return {
            'on': props[switch_info['property']] == switch_info['value_on'],
            'friendly_name': device,
            'name': device,
            **props,
        }

    def _get_switches_info(self) -> dict:
        def switch_info(device_info: dict) -> dict:
            exposes = (device_info.get('definition', {}) or {}).get('exposes', [])
            for exposed in exposes:
                for feature in exposed.get('features', []):
                    if feature.get('type') == 'binary' and 'value_on' in feature and 'value_off' in feature and \
                            feature.get('access', 0) & 2:
                        return {
                            'property': feature['property'],
                            'value_on': feature['value_on'],
                            'value_off': feature['value_off'],
                            'value_toggle': feature.get('value_toggle', None),
                        }

            return {}

        # noinspection PyUnresolvedReferences
        devices = self.devices().output
        switches_info = {}

        for device in devices:
            info = switch_info(device)
            if not info:
                continue

            switches_info[device.get('friendly_name', device.get('ieee_address'))] = info

        return switches_info

    @property
    def switches(self) -> List[dict]:
        """
        Implements the :class:`platypush.plugins.switch.SwitchPlugin.switches` property and returns the state of any
        device on the Zigbee network identified as a switch (a device is identified as a switch if it exposes a writable
        ``state`` property that can be set to ``ON`` or ``OFF``).
        """
        switches_info = self._get_switches_info()
        # noinspection PyUnresolvedReferences
        return [
            self._properties_to_switch(device=name, props=switch, switch_info=switches_info[name])
            for name, switch in self.devices_get(list(switches_info.keys())).output.items()
        ]


# vim:sw=4:ts=4:et:
