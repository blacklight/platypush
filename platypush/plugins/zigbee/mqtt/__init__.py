import json
import re
import threading

from queue import Queue
from typing import Optional, List, Any, Dict, Union

from platypush.entities import manages
from platypush.entities.batteries import Battery
from platypush.entities.electricity import (
    CurrentSensor,
    EnergySensor,
    PowerSensor,
    VoltageSensor,
)
from platypush.entities.humidity import HumiditySensor
from platypush.entities.lights import Light
from platypush.entities.linkquality import LinkQuality
from platypush.entities.sensors import Sensor, BinarySensor, NumericSensor
from platypush.entities.switches import Switch
from platypush.entities.temperature import TemperatureSensor
from platypush.message import Mapping
from platypush.message.response import Response
from platypush.plugins.mqtt import MqttPlugin, action


@manages(Light, Switch, LinkQuality, Battery, Sensor)
class ZigbeeMqttPlugin(MqttPlugin):  # lgtm [py/missing-call-to-init]
    """
    This plugin allows you to interact with Zigbee devices over MQTT through any Zigbee sniffer and
    `zigbee2mqtt <https://www.zigbee2mqtt.io/>`_.

    In order to get started you'll need:

        - A Zigbee USB adapter/sniffer (in this example I'll use the
          `CC2531 <https://hackaday.io/project/163487-zigbee-cc2531-smart-home-usb-adapter>`_.
        - A Zigbee debugger/emulator + downloader cable (only to flash the firmware).

    Instructions:

        - Install `cc-tool <https://github.com/dashesy/cc-tool>`_ either from sources or from a package manager.
        - Connect the Zigbee to your PC/RaspberryPi in this way: ::

            USB -> CC debugger -> downloader cable -> CC2531 -> USB

        - The debugger and the adapter should be connected *at the same time*. If the later ``cc-tool`` command throws
          up an error, put the device in sync while connected by pressing the _Reset_ button on the debugger.
        - Check where the device is mapped. On Linux it will usually be ``/dev/ttyACM0``.
        - Download the latest `Z-Stack firmware <https://github.com/Koenkk/Z-Stack-firmware/tree/master/coordinator>`_
          to your device. Instructions for a CC2531 device:

          .. code-block:: shell

              wget https://github.com/Koenkk/Z-Stack-firmware/raw/master\
                      /coordinator/Z-Stack_Home_1.2/bin/default/CC2531_DEFAULT_20201127.zip
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
          `official documentation <https://www.zigbee2mqtt.io/getting_started
           /running_zigbee2mqtt.html#5-optional-running-as-a-daemon-with-systemctl>`_
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

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 1883,
        base_topic: str = 'zigbee2mqtt',
        timeout: int = 10,
        tls_certfile: Optional[str] = None,
        tls_keyfile: Optional[str] = None,
        tls_version: Optional[str] = None,
        tls_ciphers: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
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
        super().__init__(
            host=host,
            port=port,
            tls_certfile=tls_certfile,
            tls_keyfile=tls_keyfile,
            tls_version=tls_version,
            tls_ciphers=tls_ciphers,
            username=username,
            password=password,
            **kwargs,
        )

        self.base_topic = base_topic
        self.timeout = timeout
        self._info = {
            'devices': {},
            'groups': {},
            'devices_by_addr': {},
        }

    def transform_entities(self, devices):
        from platypush.entities.switches import Switch

        compatible_entities = []
        for dev in devices:
            if not dev:
                continue

            dev_def = dev.get("definition") or {}
            dev_info = {
                "type": dev.get("type"),
                "date_code": dev.get("date_code"),
                "ieee_address": dev.get("ieee_address"),
                "network_address": dev.get("network_address"),
                "power_source": dev.get("power_source"),
                "software_build_id": dev.get("software_build_id"),
                "model_id": dev.get("model_id"),
                "model": dev_def.get("model"),
                "vendor": dev_def.get("vendor"),
                "supported": dev.get("supported"),
            }

            light_info = self._get_light_meta(dev)
            switch_info = self._get_switch_meta(dev)
            sensors = self._get_sensors(dev)

            if light_info:
                compatible_entities.append(
                    Light(
                        id=f'{dev["ieee_address"]}:light',
                        name=dev.get('friendly_name'),
                        on=dev.get('state', {}).get('state')
                        == switch_info.get('value_on'),
                        brightness_min=light_info.get('brightness_min'),
                        brightness_max=light_info.get('brightness_max'),
                        temperature_min=light_info.get('temperature_min'),
                        temperature_max=light_info.get('temperature_max'),
                        hue_min=light_info.get('hue_min'),
                        hue_max=light_info.get('hue_max'),
                        saturation_min=light_info.get('saturation_min'),
                        saturation_max=light_info.get('saturation_max'),
                        brightness=(
                            dev.get('state', {}).get(
                                light_info.get('brightness_name', 'brightness')
                            )
                        ),
                        temperature=(
                            dev.get('state', {}).get(
                                light_info.get('temperature_name', 'temperature')
                            )
                        ),
                        hue=(
                            dev.get('state', {})
                            .get('color', {})
                            .get(light_info.get('hue_name', 'hue'))
                        ),
                        saturation=(
                            dev.get('state', {})
                            .get('color', {})
                            .get(light_info.get('saturation_name', 'saturation'))
                        ),
                        x=(
                            dev.get('state', {})
                            .get('color', {})
                            .get(light_info.get('x_name', 'x'))
                        ),
                        y=(
                            dev.get('state', {})
                            .get('color', {})
                            .get(light_info.get('y_name', 'y'))
                        ),
                        description=dev_def.get('description'),
                        data=dev_info,
                    )
                )
            elif switch_info and dev.get('state', {}).get('state') is not None:
                compatible_entities.append(
                    Switch(
                        id=f'{dev["ieee_address"]}:switch',
                        name=dev.get('friendly_name'),
                        state=dev.get('state', {}).get('state')
                        == switch_info['value_on'],
                        description=dev_def.get("description"),
                        data=dev_info,
                        is_read_only=switch_info['is_read_only'],
                        is_write_only=switch_info['is_write_only'],
                    )
                )

            if sensors:
                compatible_entities += sensors

        return super().transform_entities(compatible_entities)  # type: ignore

    def _get_network_info(self, **kwargs) -> dict:
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
                    info[topic] = (
                        msg.payload.decode()
                        if topic == 'state'
                        else json.loads(msg.payload.decode())
                    )
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
                    raise TimeoutError(
                        'A timeout occurred while fetching the Zigbee network information'
                    )

            # Cache the new results
            self._info['devices'] = {
                device.get('friendly_name', device['ieee_address']): device
                for device in info.get('devices', [])
            }

            self._info['devices_by_addr'] = {
                device['ieee_address']: device for device in info.get('devices', [])
            }

            self._info['groups'] = {
                group.get('name'): group for group in info.get('groups', [])
            }

            self.logger.info('Zigbee network configuration updated')
        finally:
            try:
                if client:
                    client.loop_stop()
                    client.disconnect()
            except Exception as e:
                self.logger.warning(
                    'Error on MQTT client disconnection: {}'.format(str(e))
                )

        return info

    def _topic(self, topic):
        return self.base_topic + '/' + topic

    @staticmethod
    def _parse_response(response: Union[dict, Response]) -> dict:
        if isinstance(response, Response):
            response = response.output  # type: ignore[reportGeneralTypeIssues]

        assert response.get('status') != 'error', response.get(  # type: ignore[reportGeneralTypeIssues]
            'error', 'zigbee2mqtt error'
        )
        return response  # type: ignore[reportGeneralTypeIssues]

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
                                        "description": "Color of this light in the XY space",
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
                                "description": "Triggers an effect on the light",
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
        return self._get_network_info(**kwargs).get('devices', {})

    @action
    def permit_join(
        self, permit: bool = True, timeout: Optional[float] = None, **kwargs
    ):
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
                self.publish(  # type: ignore[reportGeneralTypeIssues]
                    topic=self._topic('bridge/request/permit_join'),
                    msg={'value': permit, 'time': timeout},
                    reply_topic=self._topic('bridge/response/permit_join'),
                    **self._mqtt_args(**kwargs),
                )
                or {}
            )

        return self.publish(
            topic=self._topic('bridge/request/permit_join'),
            msg={'value': permit},
            **self._mqtt_args(**kwargs),
        )

    @action
    def factory_reset(self, **kwargs):
        """
        Perform a factory reset of a device connected to the network, following the procedure required by the particular
        device (for instance, Hue bulbs require the Zigbee adapter to be close to the device while a button on the back
        of the bulb is pressed).

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        self.publish(
            topic=self._topic('bridge/request/touchlink/factory_reset'),
            msg='',
            **self._mqtt_args(**kwargs),
        )

    @action
    def log_level(self, level: str, **kwargs):
        """
        Change the log level at runtime. This change will not be persistent.

        :param level: Possible values: 'debug', 'info', 'warn', 'error'.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/config/log_level'),
                msg={'value': level},
                reply_topic=self._topic('bridge/response/config/log_level'),
                **self._mqtt_args(**kwargs),
            )
        )

    @action
    def device_set_option(self, device: str, option: str, value: Any, **kwargs):
        """
        Change the options of a device. Options can only be changed, not added or deleted.

        :param device: Display name or IEEE address of the device.
        :param option: Option name.
        :param value: New value.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/options'),
                reply_topic=self._topic('bridge/response/device/options'),
                msg={
                    'id': device,
                    'options': {
                        option: value,
                    },
                },
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/remove'),
                msg={'id': device, 'force': force},
                reply_topic=self._topic('bridge/response/device/remove'),
                **self._mqtt_args(**kwargs),
            )
        )

    @action
    def device_ban(self, device: str, **kwargs):
        """
        Ban a device from the network.

        :param device: Display name of the device.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/ban'),
                reply_topic=self._topic('bridge/response/device/ban'),
                msg={'id': device},
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/whitelist'),
                reply_topic=self._topic('bridge/response/device/whitelist'),
                msg={'id': device},
                **self._mqtt_args(**kwargs),
            )
        )

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

        devices = self.devices().output  # type: ignore[reportGeneralTypeIssues]
        assert not [
            dev for dev in devices if dev.get('friendly_name') == name
        ], 'A device named {} already exists on the network'.format(name)

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/rename'),
                msg=req,
                reply_topic=self._topic('bridge/response/device/rename'),
                **self._mqtt_args(**kwargs),
            )
        )

    @staticmethod
    def build_device_get_request(values: List[Dict[str, Any]]) -> dict:
        def extract_value(value: dict, root: dict, depth: int = 0):
            for feature in value.get('features', []):
                new_root = root
                if depth > 0:
                    new_root = root[value['property']] = root.get(value['property'], {})

                extract_value(feature, new_root, depth=depth + 1)

            if not value.get('access', 1) & 0x4:
                # Property not readable/query-able
                return

            if 'features' not in value:
                if 'property' in value:
                    root[value['property']] = 0 if value['type'] == 'numeric' else ''
                return

            if 'property' in value:
                root[value['property']] = root.get(value['property'], {})
                root = root[value['property']]

        ret = {}
        for value in values:
            extract_value(value, root=ret)

        return ret

    def _get_device_info(self, device: str) -> Mapping:
        return self._info['devices'].get(
            device, self._info['devices_by_addr'].get(device, {})
        )

    @action
    def device_get(
        self, device: str, property: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
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
        device_info = self._get_device_info(device)
        if device_info:
            device = device_info.get('friendly_name') or self._ieee_address(device_info)

        if property:
            properties = self.publish(
                topic=self._topic(device) + f'/get/{property}',
                reply_topic=self._topic(device),
                msg={property: ''},
                **kwargs,
            ).output  # type: ignore[reportGeneralTypeIssues]

            assert property in properties, f'No such property: {property}'
            return {property: properties[property]}

        if device not in self._info.get('devices', {}):
            # Refresh devices info
            self._get_network_info(**kwargs)

        dev = self._info.get('devices', {}).get(
            device, self._info.get('devices_by_addr', {}).get(device)
        )

        assert dev, f'No such device: {device}'
        exposes = (
            self._info.get('devices', {}).get(device, {}).get('definition', {}) or {}
        ).get('exposes', [])
        if not exposes:
            return {}

        device_state = self.publish(
            topic=self._topic(device) + '/get',
            reply_topic=self._topic(device),
            msg=self.build_device_get_request(exposes),
            **kwargs,
        ).output  # type: ignore[reportGeneralTypeIssues]

        if device_info:
            self.publish_entities(  # type: ignore
                [
                    {
                        **device_info,
                        'state': device_state,
                    }
                ]
            )

        return device_state

    @action
    def devices_get(
        self, devices: Optional[List[str]] = None, **kwargs
    ) -> Dict[str, dict]:
        """
        Get the properties of the devices connected to the network.

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
            devices = list(
                {
                    device['friendly_name'] or device['ieee_address']
                    for device in self.devices(**kwargs).output  # type: ignore[reportGeneralTypeIssues]
                }
            )

        def worker(device: str, q: Queue):
            q.put(self.device_get(device, **kwargs).output)  # type: ignore[reportGeneralTypeIssues]

        queues = {}
        workers = {}
        response = {}

        for device in devices:
            queues[device] = Queue()
            workers[device] = threading.Thread(
                target=worker, args=(device, queues[device])
            )
            workers[device].start()

        for device in devices:
            try:
                response[device] = queues[device].get(timeout=kwargs.get('timeout'))
                workers[device].join(timeout=kwargs.get('timeout'))
            except Exception as e:
                self.logger.warning(
                    'An error while getting the status of the device {}: {}'.format(
                        device, str(e)
                    )
                )

        return response

    @action
    def status(self, device: Optional[str] = None, *args, **kwargs):
        """
        Get the status of a device (by friendly name) or of all the connected devices (it wraps :meth:`.devices_get`).

        :param device: Device friendly name (default: get all devices).
        """
        return self.devices_get([device] if device else None, *args, **kwargs)

    @action
    def device_set(
        self,
        device: str,
        property: Optional[str] = None,
        value: Optional[Any] = None,
        values: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Set a properties on a device. The compatible properties vary depending on the device. For example, a light bulb
        may have the "``state``" and "``brightness``" properties, while an environment sensor may have the
        "``temperature``" and "``humidity``" properties, and so on.

        :param device: Display name of the device.
        :param property: Name of the property that should be set.
        :param value: New value of the property.
        :param values: If you want to set multiple values, then pass this mapping instead of ``property``+``value``.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        msg = (values or {}).copy()
        if property:
            msg[property] = value

        properties = self.publish(
            topic=self._topic(device + '/set'),
            reply_topic=self._topic(device),
            msg=msg,
            **self._mqtt_args(**kwargs),
        ).output  # type: ignore[reportGeneralTypeIssues]

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/ota_update/check'),
                reply_topic=self._topic('bridge/response/device/ota_update/check'),
                msg={'id': device},
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/ota_update/update'),
                reply_topic=self._topic('bridge/response/device/ota_update/update'),
                msg={'id': device},
                **self._mqtt_args(**kwargs),
            )
        )

    @action
    def groups(self, **kwargs) -> List[dict]:
        """
        Get the groups registered on the device.

        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._get_network_info(**kwargs).get('groups', [])

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
        payload = (
            name
            if id is None
            else {
                'id': id,
                'friendly_name': name,
            }
        )

        return self._parse_response(
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/group/add'),
                reply_topic=self._topic('bridge/response/group/add'),
                msg=payload,
                **self._mqtt_args(**kwargs),
            )
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

        properties = self.publish(
            topic=self._topic(group + '/get'),
            reply_topic=self._topic(group),
            msg=msg,
            **self._mqtt_args(**kwargs),
        ).output  # type: ignore[reportGeneralTypeIssues]

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
        properties = self.publish(
            topic=self._topic(group + '/set'),
            reply_topic=self._topic(group),
            msg={property: value},
            **self._mqtt_args(**kwargs),
        ).output  # type: ignore[reportGeneralTypeIssues]

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

        groups = {
            group.get('friendly_name'): group
            for group in self.groups().output  # type: ignore[reportGeneralTypeIssues]
        }

        assert (
            name not in groups
        ), 'A group named {} already exists on the network'.format(name)

        return self._parse_response(
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/group/rename'),
                reply_topic=self._topic('bridge/response/group/rename'),
                msg={'from': group, 'to': name} if group else name,
                **self._mqtt_args(**kwargs),
            )
        )

    @action
    def group_remove(self, name: str, **kwargs):
        """
        Remove a group.

        :param name: Display name of the group.
        :param kwargs: Extra arguments to be passed to :meth:`platypush.plugins.mqtt.MqttPlugin.publish``
            (default: query the default configured device).
        """
        return self._parse_response(
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/group/remove'),
                reply_topic=self._topic('bridge/response/group/remove'),
                msg=name,
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/group/members/add'),
                reply_topic=self._topic('bridge/response/group/members/add'),
                msg={
                    'group': group,
                    'device': device,
                },
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic(
                    'bridge/request/group/members/remove{}'.format(
                        '_all' if device is None else ''
                    )
                ),
                reply_topic=self._topic(
                    'bridge/response/group/members/remove{}'.format(
                        '_all' if device is None else ''
                    )
                ),
                msg={
                    'group': group,
                    'device': device,
                },
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/bind'),
                reply_topic=self._topic('bridge/response/device/bind'),
                msg={'from': source, 'to': target},
                **self._mqtt_args(**kwargs),
            )
        )

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
            self.publish(  # type: ignore[reportGeneralTypeIssues]
                topic=self._topic('bridge/request/device/unbind'),
                reply_topic=self._topic('bridge/response/device/unbind'),
                msg={'from': source, 'to': target},
                **self._mqtt_args(**kwargs),
            )
        )

    @action
    def on(self, device, *_, **__) -> dict:
        """
        Implements :meth:`platypush.plugins.switch.plugin.SwitchPlugin.on` and turns on a Zigbee device with a writable
        binary property.
        """
        switch_info = self._get_switch_info(device)
        assert switch_info, '{} is not a valid switch'.format(device)
        device = switch_info.get('friendly_name') or self._ieee_address(switch_info)
        props = self.device_set(
            device, switch_info['property'], switch_info['value_on']
        ).output  # type: ignore[reportGeneralTypeIssues]
        return self._properties_to_switch(
            device=device, props=props, switch_info=switch_info
        )

    @action
    def off(self, device, *_, **__) -> dict:
        """
        Implements :meth:`platypush.plugins.switch.plugin.SwitchPlugin.off` and turns off a Zigbee device with a
        writable binary property.
        """
        switch_info = self._get_switch_info(device)
        assert switch_info, '{} is not a valid switch'.format(device)
        device = switch_info.get('friendly_name') or self._ieee_address(switch_info)
        props = self.device_set(
            device, switch_info['property'], switch_info['value_off']
        ).output  # type: ignore[reportGeneralTypeIssues]
        return self._properties_to_switch(
            device=device, props=props, switch_info=switch_info
        )

    @action
    def toggle(self, device, *_, **__) -> dict:
        """
        Implements :meth:`platypush.plugins.switch.plugin.SwitchPlugin.toggle`
        and toggles a Zigbee device with a writable binary property.
        """
        switch_info = self._get_switch_info(device)
        assert switch_info, '{} is not a valid switch'.format(device)
        device = switch_info.get('friendly_name') or self._ieee_address(switch_info)
        props = self.device_set(
            device, switch_info['property'], switch_info['value_toggle']
        ).output  # type: ignore[reportGeneralTypeIssues]
        return self._properties_to_switch(
            device=device, props=props, switch_info=switch_info
        )

    def _get_switch_info(self, device: str):
        device = self._ieee_address(device)
        switches_info = self._get_switches_info()
        info = switches_info.get(device)
        if info:
            return info

        device_info = self._get_device_info(device)
        if device_info:
            device = device_info.get('friendly_name') or device_info['ieee_address']
            return switches_info.get(device)

    @staticmethod
    def _properties_to_switch(device: str, props: dict, switch_info: dict) -> dict:
        return {
            'on': props[switch_info['property']] == switch_info['value_on'],
            'friendly_name': device,
            'name': device,
            **props,
        }

    @staticmethod
    def _is_read_only(feature: dict) -> bool:
        return bool(feature.get('access', 0) & 2) == 0 and (
            bool(feature.get('access', 0) & 1) == 1
            or bool(feature.get('access', 0) & 4) == 1
        )

    @staticmethod
    def _is_write_only(feature: dict) -> bool:
        return bool(feature.get('access', 0) & 2) == 1 and (
            bool(feature.get('access', 0) & 1) == 0
            or bool(feature.get('access', 0) & 4) == 0
        )

    @staticmethod
    def _ieee_address(device: Union[dict, str]) -> str:
        # Entity value IDs are stored in the `<address>:<property>`
        # format. Therefore, we need to split by `:` if we want to
        # retrieve the original address.
        if isinstance(device, dict):
            dev = device['ieee_address']
        else:
            dev = device

        # IEEE address + property format
        if re.search(r'^0x[0-9a-fA-F]{16}:', dev):
            return dev.split(':')[0]
        return dev

    @classmethod
    def _get_switch_meta(cls, device_info: dict) -> dict:
        exposes = (device_info.get('definition', {}) or {}).get('exposes', [])
        for exposed in exposes:
            for feature in exposed.get('features', []):
                if (
                    feature.get('property') == 'state'
                    and feature.get('type') == 'binary'
                    and 'value_on' in feature
                    and 'value_off' in feature
                ):
                    return {
                        'friendly_name': device_info.get('friendly_name'),
                        'ieee_address': device_info.get('friendly_name'),
                        'property': feature['property'],
                        'value_on': feature['value_on'],
                        'value_off': feature['value_off'],
                        'value_toggle': feature.get('value_toggle', None),
                        'is_read_only': cls._is_read_only(feature),
                        'is_write_only': cls._is_write_only(feature),
                    }

        return {}

    @classmethod
    def _get_sensors(cls, device_info: dict) -> List[Sensor]:
        sensors = []
        exposes = [
            exposed
            for exposed in (device_info.get('definition', {}) or {}).get('exposes', [])
            if (exposed.get('property') and cls._is_read_only(exposed))
        ]

        for exposed in exposes:
            entity_type = None
            sensor_args = {
                'id': f'{device_info["ieee_address"]}:{exposed["property"]}',
                'name': (
                    device_info.get('friendly_name', '[Unnamed device]')
                    + ' ['
                    + exposed.get('description', '')
                    + ']'
                ),
                'value': device_info.get('state', {}).get(exposed['property']),
                'description': exposed.get('description'),
                'is_read_only': cls._is_read_only(exposed),
                'is_write_only': cls._is_write_only(exposed),
                'data': device_info,
            }

            if exposed.get('type') == 'numeric':
                sensor_args.update(
                    {
                        'min': exposed.get('value_min'),
                        'max': exposed.get('value_max'),
                        'unit': exposed.get('unit'),
                    }
                )

            if exposed.get('property') == 'battery':
                entity_type = Battery
            elif exposed.get('property') == 'linkquality':
                entity_type = LinkQuality
            elif exposed.get('property') == 'current':
                entity_type = CurrentSensor
            elif exposed.get('property') == 'energy':
                entity_type = EnergySensor
            elif exposed.get('property') == 'power':
                entity_type = PowerSensor
            elif exposed.get('property') == 'voltage':
                entity_type = VoltageSensor
            elif exposed.get('property', '').endswith('temperature'):
                entity_type = TemperatureSensor
            elif exposed.get('property', '').endswith('humidity'):
                entity_type = HumiditySensor
            elif exposed.get('type') == 'binary':
                entity_type = BinarySensor
                sensor_args['value'] = sensor_args['value'] == exposed.get(
                    'value_on', True
                )
            elif exposed.get('type') == 'numeric':
                entity_type = NumericSensor

            if entity_type:
                sensors.append(entity_type(**sensor_args))

        return sensors

    @classmethod
    def _get_light_meta(cls, device_info: dict) -> dict:
        exposes = (device_info.get('definition', {}) or {}).get('exposes', [])
        for exposed in exposes:
            if exposed.get('type') == 'light':
                features = exposed.get('features', [])
                switch = {}
                brightness = {}
                temperature = {}
                color = {}

                for feature in features:
                    if (
                        feature.get('property') == 'state'
                        and feature.get('type') == 'binary'
                        and 'value_on' in feature
                        and 'value_off' in feature
                    ):
                        switch = {
                            'value_on': feature['value_on'],
                            'value_off': feature['value_off'],
                            'state_name': feature['name'],
                            'value_toggle': feature.get('value_toggle', None),
                            'is_read_only': cls._is_read_only(feature),
                            'is_write_only': cls._is_write_only(feature),
                        }
                    elif (
                        feature.get('property') == 'brightness'
                        and feature.get('type') == 'numeric'
                        and 'value_min' in feature
                        and 'value_max' in feature
                    ):
                        brightness = {
                            'brightness_name': feature['name'],
                            'brightness_min': feature['value_min'],
                            'brightness_max': feature['value_max'],
                            'is_read_only': cls._is_read_only(feature),
                            'is_write_only': cls._is_write_only(feature),
                        }
                    elif (
                        feature.get('property') == 'color_temp'
                        and feature.get('type') == 'numeric'
                        and 'value_min' in feature
                        and 'value_max' in feature
                    ):
                        temperature = {
                            'temperature_name': feature['name'],
                            'temperature_min': feature['value_min'],
                            'temperature_max': feature['value_max'],
                            'is_read_only': cls._is_read_only(feature),
                            'is_write_only': cls._is_write_only(feature),
                        }
                    elif (
                        feature.get('property') == 'color'
                        and feature.get('type') == 'composite'
                    ):
                        color_features = feature.get('features', [])
                        for color_feature in color_features:
                            if color_feature.get('property') == 'hue':
                                color.update(
                                    {
                                        'hue_name': color_feature['name'],
                                        'hue_min': color_feature.get('value_min', 0),
                                        'hue_max': color_feature.get(
                                            'value_max', 65535
                                        ),
                                        'is_read_only': cls._is_read_only(feature),
                                        'is_write_only': cls._is_write_only(feature),
                                    }
                                )
                            elif color_feature.get('property') == 'saturation':
                                color.update(
                                    {
                                        'saturation_name': color_feature['name'],
                                        'saturation_min': color_feature.get(
                                            'value_min', 0
                                        ),
                                        'saturation_max': color_feature.get(
                                            'value_max', 255
                                        ),
                                        'is_read_only': cls._is_read_only(feature),
                                        'is_write_only': cls._is_write_only(feature),
                                    }
                                )
                            elif color_feature.get('property') == 'x':
                                color.update(
                                    {
                                        'x_name': color_feature['name'],
                                        'x_min': color_feature.get('value_min', 0.0),
                                        'x_max': color_feature.get('value_max', 1.0),
                                        'is_read_only': cls._is_read_only(feature),
                                        'is_write_only': cls._is_write_only(feature),
                                    }
                                )
                            elif color_feature.get('property') == 'y':
                                color.update(
                                    {
                                        'y_name': color_feature['name'],
                                        'y_min': color_feature.get('value_min', 0),
                                        'y_max': color_feature.get('value_max', 255),
                                        'is_read_only': cls._is_read_only(feature),
                                        'is_write_only': cls._is_write_only(feature),
                                    }
                                )

                return {
                    'friendly_name': device_info.get('friendly_name'),
                    'ieee_address': device_info.get('friendly_name'),
                    **switch,
                    **brightness,
                    **temperature,
                    **color,
                }

        return {}

    def _get_switches_info(self) -> dict:
        devices = self.devices().output  # type: ignore[reportGeneralTypeIssues]
        switches_info = {}

        for device in devices:
            info = self._get_switch_meta(device)
            if not info:
                continue

            switches_info[
                device.get('friendly_name', device['ieee_address'] + ':switch')
            ] = info

        return switches_info

    @property
    def switches(self) -> List[dict]:
        """
        Implements the :class:`platypush.plugins.switch.SwitchPlugin.switches` property and returns the state of any
        device on the Zigbee network identified as a switch (a device is identified as a switch if it exposes a writable
        ``state`` property that can be set to ``ON`` or ``OFF``).
        """
        switches_info = self._get_switches_info()
        return [
            self._properties_to_switch(
                device=name, props=switch, switch_info=switches_info[name]
            )
            for name, switch in self.devices_get(
                list(switches_info.keys())
            ).output.items()  # type: ignore[reportGeneralTypeIssues]
        ]

    @action
    def set_lights(self, lights, **kwargs):
        """
        Set the state for one or more Zigbee lights.
        """
        lights = [lights] if isinstance(lights, str) else lights
        lights = [self._ieee_address(t) for t in lights]
        devices = [
            dev
            for dev in self._get_network_info().get('devices', [])
            if self._ieee_address(dev) in lights or dev.get('friendly_name') in lights
        ]

        for dev in devices:
            light_meta = self._get_light_meta(dev)
            assert light_meta, f'{dev["name"]} is not a light'
            data = {}

            for attr, value in kwargs.items():
                if attr == 'on':
                    data[light_meta['state_name']] = value
                elif attr in {'brightness', 'bri'}:
                    data[light_meta['brightness_name']] = int(value)
                elif attr in {'temperature', 'ct'}:
                    data[light_meta['temperature_name']] = int(value)
                elif attr in {'saturation', 'sat'}:
                    data['color'] = {
                        **data.get('color', {}),
                        light_meta['saturation_name']: int(value),
                    }
                elif attr == 'hue':
                    data['color'] = {
                        **data.get('color', {}),
                        light_meta['hue_name']: int(value),
                    }
                elif attr == 'xy':
                    data['color'] = {
                        **data.get('color', {}),
                        light_meta['x_name']: float(value[0]),
                        light_meta['y_name']: float(value[1]),
                    }
                elif attr == 'x':
                    data['color'] = {
                        **data.get('color', {}),
                        light_meta['x_name']: float(value),
                    }
                elif attr == 'y':
                    data['color'] = {
                        **data.get('color', {}),
                        light_meta['y_name']: float(value),
                    }
                else:
                    data[attr] = value

            self.device_set(
                dev.get('friendly_name', dev.get('ieee_address')), values=data
            )


# vim:sw=4:ts=4:et:
