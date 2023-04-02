import queue
import threading
from typing import Any, Collection, Dict, List, Optional, Tuple, Union

import requests

from platypush.entities import (
    DimmerEntityManager,
    EnumSwitchEntityManager,
    Entity,
    LightEntityManager,
    SwitchEntityManager,
)
from platypush.entities.devices import Device
from platypush.entities.dimmers import Dimmer
from platypush.entities.electricity import CurrentSensor, PowerSensor, VoltageSensor
from platypush.entities.lights import Light
from platypush.entities.humidity import HumiditySensor
from platypush.entities.motion import MotionSensor
from platypush.entities.sensors import BinarySensor, EnumSensor, NumericSensor
from platypush.entities.switches import EnumSwitch, Switch
from platypush.entities.temperature import TemperatureSensor
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.switchbot import DeviceSchema, DeviceStatusSchema, SceneSchema

from ._constants import DeviceType
from ._setters import entity_setters


# pylint: disable=too-many-ancestors
class SwitchbotPlugin(
    RunnablePlugin,
    DimmerEntityManager,
    EnumSwitchEntityManager,
    LightEntityManager,
    SwitchEntityManager,
):
    """
    Plugin to interact with the devices registered to a `Switchbot`_
    account/hub.

    In order to use this plugin:

        - Set up a Switchbot Hub and configure your devices through the
          Switchbot app.
        - Follow the steps on `get started page`_ to get an API token from the app.

    .. _get started page: https://github.com/OpenWonderLabs/SwitchBotAPI#getting-started
    .. _Switchbot: https://www.switch-bot.com/

    """

    def __init__(self, api_token: str, **kwargs):
        """
        :param api_token: API token (see `get started page`_).
        """
        super().__init__(**kwargs)
        self._api_token = api_token
        self._devices_by_id: Dict[str, dict] = {}
        self._devices_by_name: Dict[str, dict] = {}

    @staticmethod
    def _url_for(*args, device=None):
        url = 'https://api.switch-bot.com/v1.0/'
        if device:
            url += f'devices/{device["id"]}/'
        url += '/'.join(args)
        return url

    # pylint: disable=keyword-arg-before-vararg
    def _run(self, method: str = 'get', *args, device=None, **kwargs):
        response = getattr(requests, method)(
            self._url_for(*args, device=device),
            headers={
                'Authorization': self._api_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
            },
            timeout=10,
            **kwargs,
        )

        response.raise_for_status()
        response = response.json()
        assert (
            response.get('statusCode') == 100
        ), f'Switchbot API request failed: {response.get("statusCode")}: {response.get("message")}'

        return response.get('body')

    @staticmethod
    def _split_device_id_and_property(device: str) -> Tuple[str, Optional[str]]:
        tokens = device.split(':')[:2]
        return tokens[0], (tokens[1] if len(tokens) == 2 else None)

    def _get_device(self, device: str, use_cache=True) -> dict:
        if not use_cache:
            self.devices()

        if device in self._devices_by_name:
            return self._devices_by_name[device]

        device, _ = self._split_device_id_and_property(device)
        if device in self._devices_by_id:
            return self._devices_by_id[device]

        assert use_cache, f'Device not found: {device}'
        return self._get_device(device, use_cache=False)

    @action
    def devices(self) -> List[dict]:
        """
        Get the list of devices associated to the specified Switchbot API account.

        :return: .. schema:: switchbot.DeviceSchema(many=True)
        """
        devices = self._run('get', 'devices')
        devices = [
            DeviceSchema().dump(
                {
                    **device,
                    'is_virtual': False,
                }
            )
            for device in devices.get('deviceList', [])
        ] + [
            DeviceSchema().dump(
                {
                    **device,
                    'is_virtual': True,
                }
            )
            for device in devices.get('infraredRemoteList', [])
        ]

        for device in devices:
            self._devices_by_id[device['id']] = device
            self._devices_by_name[device['name']] = device

        return devices

    @staticmethod
    def _get_device_metadata(device: dict) -> dict:
        return {
            "device_type": device.get("device_type"),
            "is_virtual": device.get("is_virtual", False),
            "hub_id": device.get("hub_id"),
        }

    @classmethod
    def _get_device_base(cls, device_dict: dict) -> Device:
        args: Dict[str, Any] = {
            'data': cls._get_device_metadata(device_dict),
        }

        return Device(
            id=f'{device_dict["id"]}',
            name=f'{device_dict["name"]}',
            **args,
        )

    @staticmethod
    def _matches_device_types(device: dict, *device_types: DeviceType) -> bool:
        return device.get('device_type') in {
            device_type.value for device_type in device_types
        }

    @classmethod
    def _get_bots(cls, *entities: dict) -> List[EnumSwitch]:
        return [
            EnumSwitch(
                id=dev["id"],
                name=dev["name"],
                value="on" if dev.get("on") else "off",
                values=["on", "off", "press"],
                is_write_only=True,
                data=cls._get_device_metadata(dev),
            )
            for dev in (entities or [])
            if cls._matches_device_types(dev, DeviceType.BOT)
        ]

    @classmethod
    def _get_lights(cls, *entities: dict) -> List[Light]:
        return [
            Light(
                id=dev["id"],
                name=dev["name"],
                on="on" if dev.get("on") else "off",
                brightness=dev.get("brightness"),
                color_temperature=dev.get("color_temperature"),
                color=dev.get("color"),
                data=cls._get_device_metadata(dev),
            )
            for dev in (entities or [])
            if cls._matches_device_types(
                dev,
                DeviceType.CEILING_LIGHT,
                DeviceType.CEILING_LIGHT_PRO,
                DeviceType.COLOR_BULB,
                DeviceType.STRIP_LIGHT,
            )
        ]

    @classmethod
    def _get_curtains(cls, *entities: dict) -> List[Dimmer]:
        return [
            Dimmer(
                id=dev["id"],
                name=dev["name"],
                value=dev.get("position"),
                min=0,
                max=100,
                unit='%',
                data=cls._get_device_metadata(dev),
            )
            for dev in (entities or [])
            if cls._matches_device_types(dev, DeviceType.CURTAIN)
        ]

    @classmethod
    def _get_meters(cls, device_dict: dict) -> List[Device]:
        devices = [cls._get_device_base(device_dict)]
        if device_dict.get('temperature') is not None:
            devices[0].children.append(
                TemperatureSensor(
                    id=f'{device_dict["id"]}:temperature',
                    name='Temperature',
                    value=device_dict['temperature'],
                    unit='C',
                )
            )

        if device_dict.get('humidity') is not None:
            devices[0].children.append(
                HumiditySensor(
                    id=f'{device_dict["id"]}:humidity',
                    name='Humidity',
                    value=device_dict['humidity'],
                    min=0,
                    max=100,
                    unit='%',
                )
            )

        if not devices[0].children:
            return []
        return devices

    @classmethod
    def _get_motion_sensors(cls, device_dict: dict) -> List[Device]:
        devices = [cls._get_device_base(device_dict)]
        if device_dict.get('moveDetected') is not None:
            devices[0].children.append(
                MotionSensor(
                    id=f'{device_dict["id"]}:motion',
                    name='Motion Detected',
                    value=bool(device_dict['moveDetected']),
                )
            )

        if device_dict.get('brightness') is not None:
            devices[0].children.append(
                BinarySensor(
                    id=f'{device_dict["id"]}:brightness',
                    name='Bright',
                    value=device_dict['brightness'] == 'bright',
                )
            )

        if not devices[0].children:
            return []
        return devices

    @classmethod
    def _get_contact_sensors(cls, device_dict: dict) -> List[Device]:
        devices = cls._get_motion_sensors(device_dict)
        if not devices:
            return []

        if device_dict.get('openState') is not None:
            devices[0].children.append(
                EnumSensor(
                    id=f'{device_dict["id"]}:open',
                    name='Open State',
                    value=device_dict['openState'],
                    values=['open', 'close', 'timeOutNotClose'],
                )
            )

        return devices

    @classmethod
    def _get_sensors(cls, *entities: dict) -> List[Device]:
        sensors: List[Entity] = []
        for dev in entities:
            if cls._matches_device_types(dev, DeviceType.METER, DeviceType.METER_PLUS):
                sensors.extend(cls._get_meters(dev))
            elif cls._matches_device_types(dev, DeviceType.MOTION_SENSOR):
                sensors.extend(cls._get_motion_sensors(dev))
            elif cls._matches_device_types(dev, DeviceType.CONTACT_SENSOR):
                sensors.extend(cls._get_contact_sensors(dev))

        return sensors

    @classmethod
    def _get_humidifiers(cls, *entities: dict) -> List[Device]:
        humidifiers = [
            dev
            for dev in entities
            if cls._matches_device_types(dev, DeviceType.HUMIDIFIER)
        ]

        devs = [Device(**cls._get_device_base(dev)) for dev in humidifiers]

        for dev_dict, entity in zip(humidifiers, devs):
            if dev_dict.get('power') is not None:
                entity.children.append(
                    Switch(
                        id=f'{dev_dict["id"]}:state',
                        name='State',
                        state=cls._is_on(dev_dict['power']),
                    )
                )

            if dev_dict.get('auto') is not None:
                entity.children.append(
                    Switch(
                        id=f'{dev_dict["id"]}:auto',
                        name='Automatic Mode',
                        state=cls._is_on(dev_dict['auto']),
                    )
                )

            if dev_dict.get('child_lock') is not None:
                entity.children.append(
                    Switch(
                        id=f'{dev_dict["id"]}:child_lock',
                        name='Child Lock',
                        state=cls._is_on(dev_dict['child_lock']),
                    )
                )

            if dev_dict.get('nebulization_efficiency') is not None:
                entity.children.append(
                    Dimmer(
                        id=f'{dev_dict["id"]}:nebulization_efficiency',
                        name='Nebulization Efficiency',
                        value=cls._is_on(dev_dict['nebulization_efficiency']),
                        min=0,
                        max=100,
                    )
                )

            if dev_dict.get('low_water') is not None:
                entity.children.append(
                    BinarySensor(
                        id=f'{dev_dict["id"]}:low_water',
                        name='Low Water',
                        value=cls._is_on(dev_dict['low_water']),
                    )
                )

            if dev_dict.get('temperature') is not None:
                entity.children.append(
                    TemperatureSensor(
                        id=f'{dev_dict["id"]}:temperature',
                        name='temperature',
                        value=dev_dict['temperature'],
                    )
                )

            if dev_dict.get('humidity') is not None:
                entity.children.append(
                    HumiditySensor(
                        id=f'{dev_dict["id"]}:humidity',
                        name='humidity',
                        value=dev_dict['humidity'],
                    )
                )

        return devs

    @classmethod
    def _get_locks(cls, *entities: dict) -> List[Device]:
        locks = [
            dev
            for dev in (entities or [])
            if cls._matches_device_types(dev, DeviceType.LOCK)
        ]

        devices = [Device(**cls._get_device_base(plug)) for plug in locks]

        for plug, device in zip(locks, devices):
            if plug.get('locked') is not None:
                device.children.append(
                    Switch(
                        id=f'{plug["id"]}:locked',
                        name='Locked',
                        state=cls._is_on(plug['locked']),
                    )
                )

            if plug.get('door_open') is not None:
                device.children.append(
                    BinarySensor(
                        id=f'{plug["id"]}:door_open',
                        name='Door Open',
                        value=cls._is_on(plug['door_open']),
                    )
                )

        return devices

    @classmethod
    def _get_plugs(cls, *entities: dict) -> List[Device]:
        plugs = [
            dev
            for dev in (entities or [])
            if cls._matches_device_types(
                dev, DeviceType.PLUG, DeviceType.PLUG_MINI_JP, DeviceType.PLUG_MINI_US
            )
        ]

        devices = [Device(**cls._get_device_base(plug)) for plug in plugs]

        for plug, device in zip(plugs, devices):
            if plug.get('on') is not None:
                device.children.append(
                    Switch(
                        id=f'{plug["id"]}:state',
                        name='State',
                        state=cls._is_on(plug['on']),
                    )
                )

            if plug.get('power') is not None:
                device.children.append(
                    PowerSensor(
                        id=f'{plug["id"]}:power',
                        name='Power',
                        value=plug['power'],
                        unit='W',
                    )
                )

            if plug.get('voltage') is not None:
                device.children.append(
                    VoltageSensor(
                        id=f'{plug["id"]}:voltage',
                        name='Voltage',
                        value=plug['voltage'],
                        unit='V',
                    )
                )

            if plug.get('current') is not None:
                device.children.append(
                    CurrentSensor(
                        id=f'{plug["id"]}:current',
                        name='Current',
                        value=plug['current'],
                        unit='A',
                    )
                )

            if plug.get('active_time') is not None:
                device.children.append(
                    NumericSensor(
                        id=f'{plug["id"]}:active_time',
                        name='Active Time',
                        value=plug['active_time'],
                        unit='min',
                    )
                )

        return devices

    @staticmethod
    def _is_on(state: Union[bool, str, int]) -> bool:
        if isinstance(state, str):
            state = state.lower()
        else:
            state = bool(state)
        return state in {'on', 'true', '1', True}

    def transform_entities(self, entities: Collection[dict]) -> Collection[Entity]:
        return [
            *self._get_bots(*entities),
            *self._get_curtains(*entities),
            *self._get_humidifiers(*entities),
            *self._get_lights(*entities),
            *self._get_locks(*entities),
            *self._get_plugs(*entities),
            *self._get_sensors(*entities),
        ]

    def _worker(  # pylint: disable=keyword-arg-before-vararg
        self,
        q: queue.Queue,
        method: str = 'get',
        *args,
        device: Optional[dict] = None,
        **kwargs,
    ):
        schema = DeviceStatusSchema()
        try:
            if (
                method == 'get'
                and args
                and args[0] == 'status'
                and device
                and device.get('is_virtual')
            ):
                res = schema.load(device)
            else:
                res = self._run(method, *args, device=device, **kwargs)

            q.put(schema.dump(res))
        except Exception as e:
            self.logger.exception(e)
            q.put(e)

    @action
    # pylint: disable=arguments-differ
    def status(
        self, device: Optional[str] = None, publish_entities: bool = True, **_
    ) -> Union[dict, List[dict]]:
        """
        Get the status of all the registered devices or of a specific device.

        :param device: Filter by device ID or name.
        :return: .. schema:: switchbot.DeviceStatusSchema(many=True)
        """
        devices = self.devices().output
        if device:
            device_info = self._get_device(device)
            status = (
                {}
                if device_info['is_virtual']
                else self._run('get', 'status', device=device_info)
            )
            return {
                **device_info,
                **status,
            }

        devices_by_id = {dev['id']: dev for dev in devices}
        queues: List[queue.Queue] = [queue.Queue()] * len(devices)
        workers = [
            threading.Thread(
                target=self._worker,
                args=(queues[i], 'get', 'status'),
                kwargs={'device': dev},
            )
            for i, dev in enumerate(devices)
        ]

        results = []
        for worker in workers:
            worker.start()

        for q in queues:
            response = q.get()
            if not response:
                continue

            assert not isinstance(response, Exception), str(response)
            results.append(
                {
                    **devices_by_id.get(response.get('id'), {}),
                    **response,
                }
            )

        for worker in workers:
            worker.join()

        if publish_entities:
            self.publish_entities(results)
        return results

    @action
    def press(self, device: str):
        """
        Send a press-button command to a device.

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run('post', 'commands', device=dev, json={'command': 'press'})

    @action
    def toggle(self, device: str, **_):  # pylint: disable=arguments-differ
        """
        Shortcut for :meth:`.press`.

        :param device: Device name or ID.
        """
        return self.press(device)

    @action
    def on(self, device: str, **_):  # pylint: disable=arguments-differ
        """
        Send a turn-on command to a device

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run('post', 'commands', device=dev, json={'command': 'turnOn'})

    @action
    def off(self, device: str, **_):  # pylint: disable=arguments-differ
        """
        Send a turn-off command to a device

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run('post', 'commands', device=dev, json={'command': 'turnOff'})

    @action
    def lock(self, device: str, **_):
        """
        Lock a compatible lock device.

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run('post', 'commands', device=dev, json={'command': 'lock'})

    @action
    def unlock(self, device: str, **_):
        """
        Unlock a compatible lock device.

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run('post', 'commands', device=dev, json={'command': 'unlock'})

    @action
    def set_curtain_position(self, device: str, position: int):
        """
        Set the position of a curtain device.

        :param device: Device name or ID.
        :param position: An integer between 0 (open) and 100 (closed).
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'setPosition',
                'commandType': 'command',
                'parameter': f'0,ff,{position}',
            },
        )

    @action
    def set_humidifier_efficiency(self, device: str, efficiency: Union[int, str]):
        """
        Set the nebulization efficiency of a humidifier device.

        :param device: Device name or ID.
        :param efficiency: Possible values:

            - ``auto``: Automatic mode.
            - A value between ``0`` and ``100``.

        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'setMode',
                'commandType': 'command',
                'parameter': efficiency,
            },
        )

    @action
    def set_fan_speed(self, device: str, speed: int):
        """
        Set the speed of a fan.

        :param device: Device name or ID.
        :param speed: Speed between 1 and 4.
        """
        status = self.status(device=device).output
        mode = status.get('mode')
        swing_range = status.get('swing_range')
        return self._run(
            'post',
            'commands',
            device=device,
            json={
                'command': 'set',
                'commandType': 'command',
                'parameter': ','.join(['on', str(mode), str(speed), str(swing_range)]),
            },
        )

    @action
    def set_fan_mode(self, device: str, mode: int):
        """
        Set the mode of a fan.

        :param device: Device name or ID.
        :param mode: Fan mode (1 or 2).
        """
        status = self.status(device=device).output
        speed = status.get('speed')
        swing_range = status.get('swing_range')
        return self._run(
            'post',
            'commands',
            device=device,
            json={
                'command': 'set',
                'commandType': 'command',
                'parameter': ','.join(['on', str(mode), str(speed), str(swing_range)]),
            },
        )

    @action
    def set_swing_range(self, device: str, swing_range: int):
        """
        Set the swing range of a fan.

        :param device: Device name or ID.
        :param swing_range: Swing range angle, between 0 and 120.
        """
        status = self.status(device=device).output
        speed = status.get('speed')
        mode = status.get('mode')
        return self._run(
            'post',
            'commands',
            device=device,
            json={
                'command': 'set',
                'commandType': 'command',
                'parameter': ','.join(['on', str(mode), str(speed), str(swing_range)]),
            },
        )

    @action
    def set_temperature(self, device: str, temperature: float):
        """
        Set the temperature of an air conditioner.

        :param device: Device name or ID.
        :param temperature: Temperature, in Celsius.
        """
        status = self.status(device=device).output
        mode = status.get('mode')
        fan_speed = status.get('fan_speed')
        return self._run(
            'post',
            'commands',
            device=device,
            json={
                'command': 'setAll',
                'commandType': 'command',
                'parameter': ','.join(
                    [str(temperature), str(mode), str(fan_speed), 'on']
                ),
            },
        )

    @action
    def set_ac_mode(self, device: str, mode: int):
        """
        Set the mode of an air conditioner.

        :param device: Device name or ID.
        :param mode: Air conditioner mode. Supported values:

            * 1: ``auto``
            * 2: ``cool``
            * 3: ``dry``
            * 4: ``fan``
            * 5: ``heat``

        """
        status = self.status(device=device).output
        temperature = status.get('temperature')
        fan_speed = status.get('fan_speed')
        return self._run(
            'post',
            'commands',
            device=device,
            json={
                'command': 'setAll',
                'commandType': 'command',
                'parameter': ','.join(
                    [str(temperature), str(mode), str(fan_speed), 'on']
                ),
            },
        )

    @action
    def set_ac_fan_speed(self, device: str, fan_speed: int):
        """
        Set the fan speed for an air conditioner.

        :param device: Device name or ID.
        :param fan_speed: Possible values:

            * 1: ``auto``
            * 2: ``low``
            * 3: ``medium``
            * 4: ``high``

        """
        status = self.status(device=device).output
        temperature = status.get('temperature')
        mode = status.get('mode')
        return self._run(
            'post',
            'commands',
            device=device,
            json={
                'command': 'setAll',
                'commandType': 'command',
                'parameter': ','.join(
                    [str(temperature), str(mode), str(fan_speed), 'on']
                ),
            },
        )

    @action
    def set_channel(self, device: str, channel: int):
        """
        Set the channel on a TV, IPTV/Streamer, Set Top Box device.

        :param device: Device name or ID.
        :param channel: Channel number.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'SetChannel',
                'commandType': 'command',
                'parameter': [str(channel)],
            },
        )

    @action
    def volup(self, device: str):
        """
        Send volume up IR event to a device (for TV, IPTV/Streamer, Set Top Box, DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'volumeAdd',
                'commandType': 'command',
            },
        )

    @action
    def voldown(self, device: str):
        """
        Send volume down IR event to a device (for TV, IPTV/Streamer, Set Top Box, DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'volumeSub',
                'commandType': 'command',
            },
        )

    @action
    def mute(self, device: str):
        """
        Send mute/unmute IR event to a device (for TV, IPTV/Streamer, Set Top Box, DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'setMute',
                'commandType': 'command',
            },
        )

    @action
    def channel_next(self, device: str):
        """
        Send next channel IR event to a device (for TV, IPTV/Streamer, and Set Top Box).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'channelAdd',
                'commandType': 'command',
            },
        )

    @action
    def channel_prev(self, device: str):
        """
        Send previous channel IR event to a device (for TV, IPTV/Streamer, and Set Top Box).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'channelSub',
                'commandType': 'command',
            },
        )

    @action
    def play(self, device: str):
        """
        Send play IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'Play',
                'commandType': 'command',
            },
        )

    @action
    def pause(self, device: str):
        """
        Send pause IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'Pause',
                'commandType': 'command',
            },
        )

    @action
    def ir_stop(self, device: str):
        """
        Send stop IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'Stop',
                'commandType': 'command',
            },
        )

    @action
    def forward(self, device: str):
        """
        Send forward IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'FastForward',
                'commandType': 'command',
            },
        )

    @action
    def back(self, device: str):
        """
        Send backward IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'Rewind',
                'commandType': 'command',
            },
        )

    @action
    def next(self, device: str):
        """
        Send next IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'Next',
                'commandType': 'command',
            },
        )

    @action
    def previous(self, device: str):
        """
        Send previous IR event to a device (for DVD and Speaker).

        :param device: Device name or ID.
        """
        dev = self._get_device(device)
        return self._run(
            'post',
            'commands',
            device=dev,
            json={
                'command': 'Previous',
                'commandType': 'command',
            },
        )

    @action
    def scenes(self) -> List[dict]:
        """
        Get the list of registered scenes.

        :return: .. schema:: switchbot.SceneSchema(many=True)
        """
        return SceneSchema().dump(self._run('get', 'scenes'), many=True)

    @action
    def run_scene(self, scene: str):
        """
        Execute a scene.

        :param scene: Scene ID or name.
        """
        scenes = [
            s
            for s in self.scenes().output
            if s.get('id') == scene or s.get('name') == scene
        ]

        assert scenes, f'No such scene: {scene}'
        return self._run('post', 'scenes', scenes[0]['id'], 'execute')

    @action
    # pylint: disable=redefined-builtin
    def set_value(
        self, device: str, property: Optional[str] = None, value: Any = None, **__
    ):
        """
        Set the value of a property of a device.

        :param device: Device name or ID, or entity (external) ID.
        :param property: Property to set. It should be present if you are
            passing a root device ID to ``device`` and not an atomic entity in
            the format ``<device_id>:<property_name>``.
        :param value: Value to set.
        """
        entity = self._to_entity(device, property)
        assert entity, f'No such device: "{device}"'

        dt = entity.data.get('device_type')
        assert dt, f'Could not infer the device type for "{device}"'

        device_type = DeviceType(dt)
        setter_class = entity_setters.get(device_type)
        assert setter_class, f'No setters found for device type "{device_type}"'

        setter = setter_class(entity)
        return setter(property=property, value=value)

    @action
    def set(self, entity: str, value: Any, attribute: Optional[str] = None, **kwargs):
        return self.set_value(entity, property=attribute, value=value, **kwargs)

    def _to_entity(
        self,
        device: str,
        property: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> Optional[Entity]:
        dev = self._get_device(device)
        entities = list(self.transform_entities([dev]))
        if not entities:
            return None
        if len(entities) == 1:
            return entities[0]
        if not property:
            device, property = self._split_device_id_and_property(device)
        assert property, 'No property specified'

        entity_id = f'{device}:{property}'
        return next(iter([e for e in entities if e.id == entity_id]), None)

    @action
    def set_lights(
        self,
        *_,
        lights: Collection[str],
        on: Optional[bool] = None,
        brightness: Optional[int] = None,
        hex: Optional[str] = None,  # pylint: disable=redefined-builtin
        temperature: Optional[int] = None,
        **__,
    ):
        """
        Change the settings for compatible lights.

        :param lights: Light names or IDs.
        :param on: Turn on the lights.
        :param brightness: Set the brightness of the lights.
        :param hex: Set the color of the lights.
        :param temperature: Set the temperature of the lights.
        """
        devices = [self._get_device(light) for light in lights]
        for dev in devices:
            if on is not None:
                method = self.on if on else self.off
                method(dev['id'])

            if brightness is not None:
                self._run(
                    'post',
                    'commands',
                    device=dev,
                    json={
                        'command': 'setBrightness',
                        'commandType': 'command',
                        'parameter': brightness,
                    },
                )

            if hex is not None:
                self._run(
                    'post',
                    'commands',
                    device=dev,
                    json={
                        'command': 'setColor',
                        'commandType': 'command',
                        'parameter': hex,
                    },
                )

            if temperature is not None:
                self._run(
                    'post',
                    'commands',
                    device=dev,
                    json={
                        'command': 'setColorTemperature',
                        'commandType': 'command',
                        'parameter': temperature,
                    },
                )

    def main(self):
        entities = {}

        while not self.should_stop():
            status = self.status(publish_entities=False).output
            new_entities = {e['id']: e for e in status}
            updated_entities = {
                id: e
                for id, e in new_entities.items()
                if any(v != entities.get(id, {}).get(k) for k, v in e.items())
            }

            if updated_entities:
                self.publish_entities(updated_entities.values())

            entities = new_entities
            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
