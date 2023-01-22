import asyncio
import aiohttp

from threading import RLock
from typing import Optional, Dict, List, Set, Tuple, Type, Union, Iterable

import pysmartthings

from platypush.entities import Entity, manages

from platypush.entities.batteries import Battery
from platypush.entities.devices import Device
from platypush.entities.dimmers import Dimmer
from platypush.entities.lights import Light
from platypush.entities.motion import MotionSensor
from platypush.entities.sensors import Sensor
from platypush.entities.switches import Switch
from platypush.plugins import RunnablePlugin, action
from platypush.utils import camel_case_to_snake_case


@manages(Device, Dimmer, Sensor, Switch, Light)
class SmartthingsPlugin(RunnablePlugin):
    """
    Plugin to interact with devices and locations registered to a Samsung SmartThings account.

    Requires:

        * **pysmartthings** (``pip install pysmartthings``)

    """

    _timeout = aiohttp.ClientTimeout(total=20.0)

    def __init__(
        self, access_token: str, poll_interval: Optional[float] = 20.0, **kwargs
    ):
        """
        :param access_token: SmartThings API access token - you can get one at https://account.smartthings.com/tokens.
        :param poll_interval: How often the plugin should poll for changes, in seconds (default: 20).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
        self._access_token = access_token
        self._refresh_lock = RLock()
        self._execute_lock = RLock()

        self._locations = []
        self._devices = []
        self._rooms_by_location = {}

        self._locations_by_id = {}
        self._locations_by_name = {}
        self._devices_by_id = {}
        self._devices_by_name = {}
        self._rooms_by_id = {}
        self._rooms_by_location_and_id = {}
        self._rooms_by_location_and_name = {}

    async def _refresh_locations(self, api):
        self._locations = await api.locations()
        self._locations_by_id = {loc.location_id: loc for loc in self._locations}
        self._locations_by_name = {loc.name: loc for loc in self._locations}

    async def _refresh_devices(self, api):
        self._devices = await api.devices()
        self._devices_by_id = {dev.device_id: dev for dev in self._devices}
        self._devices_by_name = {dev.label: dev for dev in self._devices}

    async def _refresh_rooms(self, api, location_id: str):
        self._rooms_by_location[location_id] = await api.rooms(location_id=location_id)

        self._rooms_by_id.update(
            **{room.room_id: room for room in self._rooms_by_location[location_id]}
        )

        self._rooms_by_location_and_id[location_id] = {
            room.room_id: room for room in self._rooms_by_location[location_id]
        }

        self._rooms_by_location_and_name[location_id] = {
            room.name: room for room in self._rooms_by_location[location_id]
        }

    async def _refresh_info(self):

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            api = pysmartthings.SmartThings(session, self._access_token)
            tasks = [
                asyncio.ensure_future(self._refresh_locations(api)),
                asyncio.ensure_future(self._refresh_devices(api)),
            ]

            await asyncio.gather(*tasks)

            room_tasks = [
                asyncio.ensure_future(self._refresh_rooms(api, location.location_id))
                for location in self._locations
            ]

            await asyncio.gather(*room_tasks)

    def refresh_info(self):
        with self._refresh_lock:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._refresh_info())
            finally:
                loop.stop()

    def _location_to_dict(self, location) -> Dict:
        return {
            'name': location.name,
            'location_id': location.location_id,
            'country_code': location.country_code,
            'locale': location.locale,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'temperature_scale': location.temperature_scale,
            'region_radius': location.region_radius,
            'timezone_id': location.timezone_id,
            'rooms': {
                room.room_id: self._room_to_dict(room)
                for room in self._rooms_by_location.get(location.location_id, {})
            },
        }

    @staticmethod
    def _device_to_dict(device) -> Dict:
        return {
            'capabilities': device.capabilities,
            'name': device.label,
            'device_id': device.device_id,
            'location_id': device.location_id,
            'room_id': device.room_id,
            'device_type_id': device.device_type_id,
            'device_type_name': device.device_type_name,
            'device_type_network': device.device_type_network,
        }

    @staticmethod
    def _room_to_dict(room) -> Dict:
        return {
            'name': room.name,
            'background_image': room.background_image,
            'room_id': room.room_id,
            'location_id': room.location_id,
        }

    @action
    def info(self) -> Dict[str, Dict[str, dict]]:
        """
        Return the objects registered to the account, including locations and devices.

          .. code-block:: json

            {
                "devices": {
                    "smart-tv-id": {
                        "capabilities": [
                            "ocf",
                            "switch",
                            "audioVolume",
                            "audioMute",
                            "tvChannel",
                            "mediaInputSource",
                            "mediaPlayback",
                            "mediaTrackControl",
                            "custom.error",
                            "custom.picturemode",
                            "custom.soundmode",
                            "custom.accessibility",
                            "custom.launchapp",
                            "custom.recording",
                            "custom.tvsearch",
                            "custom.disabledCapabilities",
                            "samsungvd.ambient",
                            "samsungvd.ambientContent",
                            "samsungvd.ambient18",
                            "samsungvd.mediaInputSource",
                            "refresh",
                            "execute",
                            "samsungvd.firmwareVersion",
                            "samsungvd.supportsPowerOnByOcf"
                        ],
                        "device_id": "smart-tv-id",
                        "device_type_id": null,
                        "device_type_name": null,
                        "device_type_network": null,
                        "location_id": "location-id",
                        "name": "Samsung Smart TV",
                        "room_id": "room-1"
                    },
                    "tv-switch-id": {
                        "capabilities": [
                            "switch",
                            "refresh",
                            "healthCheck"
                        ],
                        "device_id": "tv-switch-id",
                        "device_type_id": null,
                        "device_type_name": null,
                        "device_type_network": null,
                        "location_id": "location-id",
                        "name": "TV Smart Switch",
                        "room_id": "room-1"
                    },
                    "lights-switch-id": {
                        "capabilities": [
                            "switch",
                            "refresh",
                            "healthCheck"
                        ],
                        "device_id": "lights-switch-id",
                        "device_type_id": null,
                        "device_type_name": null,
                        "device_type_network": null,
                        "location_id": "location-id",
                        "name": "Lights Switch",
                        "room_id": "room-2"
                    }
                },
                "locations": {
                    "location-id": {
                        "name": "My home",
                        "location_id": "location-id",
                        "country_code": "us",
                        "locale": "en-US",
                        "latitude": "latitude",
                        "longitude": "longitude",
                        "temperature_scale": null,
                        "region_radius": null,
                        "timezone_id": null,
                        "rooms": {
                            "room-1": {
                                "background_image": null,
                                "location_id": "location-1",
                                "name": "Living Room",
                                "room_id": "room-1"
                            },
                            "room-2": {
                                "background_image": null,
                                "location_id": "location-1",
                                "name": "Bedroom",
                                "room_id": "room-2"
                            }
                        }
                    }
                }
            }

        """
        self.refresh_info()
        return {
            'locations': {
                loc.location_id: self._location_to_dict(loc) for loc in self._locations
            },
            'devices': {
                dev.device_id: self._device_to_dict(dev) for dev in self._devices
            },
        }

    @action
    def get_location(
        self, location_id: Optional[str] = None, name: Optional[str] = None
    ) -> dict:
        """
        Get the info of a location by ID or name.

          .. code-block:: json

            {
                "name": "My home",
                "location_id": "location-id",
                "country_code": "us",
                "locale": "en-US",
                "latitude": "latitude",
                "longitude": "longitude",
                "temperature_scale": null,
                "region_radius": null,
                "timezone_id": null,
                "rooms": {
                    "room-1": {
                        "background_image": null,
                        "location_id": "location-1",
                        "name": "Living Room",
                        "room_id": "room-1"
                    },
                    "room-2": {
                        "background_image": null,
                        "location_id": "location-1",
                        "name": "Bedroom",
                        "room_id": "room-2"
                    }
                }
            }

        """
        assert location_id or name, 'Specify either location_id or name'
        if (
            location_id not in self._locations_by_id
            or name not in self._locations_by_name
        ):
            self.refresh_info()

        location = self._locations_by_id.get(
            location_id, self._locations_by_name.get(name)
        )
        assert location, 'Location {} not found'.format(location_id or name)
        return self._location_to_dict(location)

    def _get_device(self, device: str):
        return self._get_devices(device)[0]

    def _get_found_and_missing_devs(
        self, *devices: str
    ) -> Tuple[List[Device], List[str]]:
        # Split the external_id:type indicators and always return the parent device
        devices = tuple(dev.split(':')[0] for dev in devices)

        found_devs = {
            dev: self._devices_by_id.get(dev, self._devices_by_name.get(dev))
            for dev in devices
            if self._devices_by_id.get(dev, self._devices_by_name.get(dev))
        }

        missing_devs = {dev for dev in devices if dev not in found_devs}

        return list(found_devs.values()), list(missing_devs)  # type: ignore

    def _get_devices(self, *devices: str):
        devs, missing_devs = self._get_found_and_missing_devs(*devices)
        if missing_devs:
            self.refresh_info()

        devs, missing_devs = self._get_found_and_missing_devs(*devices)
        assert not missing_devs, f'Devices not found: {missing_devs}'
        return devs

    @action
    def get_device(self, device: str) -> dict:
        """
        Get a device info by ID or name.

        :param device: Device ID or name.
        :return:

          .. code-block:: json

            "tv-switch-id": {
                "capabilities": [
                    "switch",
                    "refresh",
                    "healthCheck"
                ],
                "device_id": "tv-switch-id",
                "device_type_id": null,
                "device_type_name": null,
                "device_type_network": null,
                "location_id": "location-id",
                "name": "TV Smart Switch",
                "room_id": "room-1"
            }

        """
        device = self._get_device(device)
        return self._device_to_dict(device)

    async def _execute(
        self,
        device_id: str,
        capability: str,
        command,
        component_id: str,
        args: Optional[list],
    ):
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            api = pysmartthings.SmartThings(session, self._access_token)
            device = await api.device(device_id)
            ret = await device.command(
                component_id=component_id,
                capability=capability,
                command=command,
                args=args,
            )

        assert (
            ret
        ), 'The command {capability}={command} failed on device {device}'.format(
            capability=capability, command=command, device=device_id
        )

    @action
    def execute(
        self,
        device: str,
        capability: str,
        command,
        component_id: str = 'main',
        args: Optional[list] = None,
    ):
        """
        Execute a command on a device.

        Example request to turn on a device with ``switch`` capability:

          .. code-block:: json

            {
              "type": "request",
              "action": "smartthings.execute",
              "args": {
                "device": "My Switch",
                "capability": "switch",
                "command": "on"
              }
            }

        :param device: Device ID or name.
        :param capability: Property to be read/written (see device ``capabilities`` returned from :meth:`.get_device`).
        :param command: Command to execute on the ``capability``
            (see https://smartthings.developer.samsung.com/docs/api-ref/capabilities.html).
        :param component_id: ID of the component to execute the command on (default: ``main``, i.e. the device itself).
        :param args: Command extra arguments, as a list.
        """
        device = self._get_device(device)

        with self._execute_lock:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self._execute(
                        device_id=device.device_id,
                        capability=capability,
                        command=command,
                        component_id=component_id,
                        args=args,
                    )
                )
            finally:
                loop.stop()

    @staticmethod
    def _get_capabilities(device) -> Set[str]:
        if isinstance(device, dict):
            return set(device.get('capabilities', []))
        return set(device.capabilities)

    @staticmethod
    def _to_entity(entity_type: Type[Entity], device, **kwargs) -> Entity:
        return entity_type(
            id=device.device_id + ':' + entity_type.__name__.lower(),
            name=entity_type.__name__,
            **kwargs,
        )

    @classmethod
    def _get_lights(cls, device) -> Iterable[Light]:
        # TODO double-check conversion values here according to the docs
        if not (
            {'colorControl', 'colorTemperature'}.intersection(
                cls._get_capabilities(device)
            )
        ):
            return []

        light_attrs = {}
        if 'switch' in device.capabilities:
            light_attrs['on'] = device.status.switch
        if getattr(device.status, 'level', None) is not None:
            light_attrs['brightness'] = device.status.level
            light_attrs['brightness_min'] = 0
            light_attrs['brightness_max'] = 100
        if 'colorTemperature' in device.capabilities:
            # Color temperature range on SmartThings is expressed in Kelvin
            light_attrs['temperature_min'] = 2000
            light_attrs['temperature_max'] = 6500
            if device.status.color_temperature >= light_attrs['temperature_min']:
                light_attrs['temperature'] = (
                    light_attrs['temperature_max'] - light_attrs['temperature_min']
                ) / 2
        if getattr(device.status, 'hue', None) is not None:
            light_attrs['hue'] = device.status.hue
            light_attrs['hue_min'] = 0
            light_attrs['hue_max'] = 100
        if getattr(device.status, 'saturation', None) is not None:
            light_attrs['saturation'] = device.status.saturation
            light_attrs['saturation_min'] = 0
            light_attrs['saturation_max'] = 100

        return [cls._to_entity(Light, device, **light_attrs)]

    @classmethod
    def _get_switches(cls, device) -> Iterable[Switch]:
        if 'switch' not in cls._get_capabilities(device):
            return []

        return [
            cls._to_entity(
                Switch,
                device,
                state=device.status.switch,
            )
        ]

    @classmethod
    def _get_dimmers(cls, device: pysmartthings.Device) -> Iterable[Dimmer]:
        if 'switchLevel' not in cls._get_capabilities(device):
            return []

        kwargs = cls._get_status_attr_info(device, 'level')
        return [
            cls._to_entity(
                Dimmer, device, value=device.status.level, min=0, max=100, **kwargs
            )
        ]

    @classmethod
    def _get_sensors(cls, device) -> Iterable[Sensor]:
        sensors = []

        if 'motionSensor' in cls._get_capabilities(device):
            kwargs = cls._get_status_attr_info(device, 'motion')
            sensors.append(
                cls._to_entity(
                    MotionSensor,
                    device,
                    value=device.status.motion,
                    **kwargs,
                )
            )

        if 'battery' in cls._get_capabilities(device):
            kwargs = cls._get_status_attr_info(device, 'battery')
            sensors.append(
                cls._to_entity(
                    Battery,
                    device,
                    value=device.status.attributes['battery'].value,
                    **kwargs,
                )
            )

        return sensors

    @staticmethod
    def _get_status_attr_info(device: pysmartthings.Device, attr: str) -> dict:
        status = device.status.attributes.get(attr)
        info = {}
        if status:
            if getattr(status, 'unit', None) is not None:
                info['unit'] = status.unit
            if getattr(status, 'min', None) is not None:
                info['min'] = status.min
            if getattr(status, 'max', None) is not None:
                info['max'] = status.max

        return info

    def transform_entities(self, entities):
        compatible_entities = []

        for entity in entities:
            device_entities = [
                *self._get_lights(entity),
                *self._get_switches(entity),
                *self._get_dimmers(entity),
                *self._get_sensors(entity),
            ]

            if device_entities:
                parent = Device(
                    id=entity.device_id,
                    name=entity.label,
                )

                for child in device_entities:
                    child.parent = parent

                device_entities.insert(0, parent)

            compatible_entities += device_entities

        return super().transform_entities(compatible_entities)  # type: ignore

    async def _get_device_status(
        self, api, device_id: str, publish_entities: bool
    ) -> dict:
        device = await api.device(device_id)
        assert device, f'No such device: {device_id}'
        await device.status.refresh()
        if publish_entities:
            self.publish_entities([device])  # type: ignore

        self._devices_by_id[device_id] = device
        self._devices_by_name[device.label] = device
        for i, dev in enumerate(self._devices):
            if dev.device_id == device_id:
                self._devices[i] = device
                break

        return {
            'device_id': device_id,
            'name': device.label,
            **{
                cap: getattr(device.status, cap)
                for cap in device.capabilities
                if hasattr(device.status, cap)
                and not callable(getattr(device.status, cap))
            },
        }

    async def _refresh_status(
        self, devices: List[str], publish_entities: bool = True
    ) -> List[dict]:
        device_ids = []
        missing_device_ids = set()

        def parse_device_id(device):
            device_id = None
            if device in self._devices_by_id:
                device_id = device
                device_ids.append(device_id)
            elif device in self._devices_by_name:
                device_id = self._devices_by_name[device].device_id
                device_ids.append(device_id)
            else:
                missing_device_ids.add(device)

            if device_id and device in missing_device_ids:
                missing_device_ids.remove(device)

        for dev in devices:
            parse_device_id(dev)

        # Fail if some devices haven't been found after refreshing
        assert (
            not missing_device_ids
        ), 'Could not find the following devices: {}'.format(list(missing_device_ids))

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            api = pysmartthings.SmartThings(session, self._access_token)
            status_tasks = [
                asyncio.ensure_future(
                    self._get_device_status(
                        api, device_id, publish_entities=publish_entities
                    )
                )
                for device_id in device_ids
            ]

            # noinspection PyTypeChecker
            return await asyncio.gather(*status_tasks)

    @action
    def status(
        self, device: Optional[Union[str, List[str]]] = None, publish_entities=True
    ) -> List[dict]:
        """
        Refresh and return the status of one or more devices.

        :param device: Device or list of devices to refresh (default: all)
        :return: A list containing on entry per device, and each entry containing the current device state. Example:

          .. code-block:: json

            [
              {
                "device_id": "switch-1",
                "name": "Fan",
                "switch": false
              },
              {
                "device_id": "tv-1",
                "name": "Samsung Smart TV",
                "switch": true
              }
            ]

        """
        self.refresh_info()

        if not device:
            self.refresh_info()
            devices = self._devices_by_id.keys()
        elif isinstance(device, str):
            devices = [device]
        else:
            devices = device

        with self._refresh_lock:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(
                    self._refresh_status(
                        list(devices), publish_entities=publish_entities
                    )
                )
            finally:
                loop.stop()

    @action
    def on(self, device: str, *_, **__) -> dict:
        """
        Turn on a device with ``switch`` capability.

        :param device: Device name or ID.
        :return: Device status
        """
        self.execute(device, 'switch', 'on')
        return self.status(device).output[0]  # type: ignore

    @action
    def off(self, device: str, *_, **__) -> dict:
        """
        Turn off a device with ``switch`` capability.

        :param device: Device name or ID.
        :return: Device status
        """
        self.execute(device, 'switch', 'off')
        return self.status(device).output[0]  # type: ignore

    @action
    def toggle(self, device: str, *args, **__) -> dict:
        """
        Toggle a device with ``switch`` capability.

        :param device: Device name or ID.
        :return: Device status
        """
        device = self._get_device(device)
        device_id = device.device_id

        async def _toggle():
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                api = pysmartthings.SmartThings(session, self._access_token)
                dev = await api.device(device_id)
                assert (
                    'switch' in dev.capabilities
                ), 'The device {} has no switch capability'.format(dev.label)

                await dev.status.refresh()
                state = 'off' if dev.status.switch else 'on'
                ret = await dev.command(
                    component_id='main', capability='switch', command=state, args=args
                )

            assert ret, 'The command switch={state} failed on device {device}'.format(
                state=state, device=dev.label
            )

        with self._refresh_lock:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_toggle())
            updated_device = loop.run_until_complete(self._refresh_status([device_id]))[
                0
            ]

            return {
                'id': device_id,
                'name': updated_device['name'],
                'on': updated_device['switch'],
            }

    @action
    def set_level(self, device: str, level: int, **kwargs):
        """
        Set the level of a device with ``switchLevel`` capabilities (e.g. the
        brightness of a lightbulb or the speed of a fan).

        :param device: Device ID or name.
        :param level: Level, usually a percentage value between 0 and 1.
        :param kwarsg: Extra arguments that should be passed to :meth:`.execute`.
        """
        self.execute(device, 'switchLevel', 'setLevel', args=[int(level)], **kwargs)

    @action
    def set_value(
        self, device: str, property: Optional[str] = None, data=None, **kwargs
    ):
        """
        Set the value of a device. It is compatible with the generic
        ``set_value`` method required by entities.

        :param device: Device ID or device+property name string in the format ``device_id:property``.
        :param property: Name of the property to be set. If not specified here
            then it should be specified on the ``device`` level.
        :param data: Value to be set.
        """
        device_tokens = device.split(':')
        if len(device_tokens) > 1:
            device, property = device_tokens[:2]
        assert property, 'No property name specified'

        if property.startswith('dimmer'):
            assert data is not None, 'No value specified'
            self.execute(device, 'switchLevel', 'setLevel', args=[int(data)], **kwargs)
        elif property.startswith('switch'):
            self.execute(device, 'switch', 'on' if data else 'off', **kwargs)

    @action
    def set_lights(
        self,
        lights: Iterable[str],
        on: Optional[bool] = None,
        brightness: Optional[int] = None,
        hue: Optional[int] = None,
        saturation: Optional[int] = None,
        hex: Optional[str] = None,
        temperature: Optional[int] = None,
        **_,
    ):
        err = None

        with self._execute_lock:
            for light in lights:
                try:
                    if on is not None:
                        self.execute(light, 'switch', 'on' if on else 'off')
                    if brightness is not None:
                        self.execute(
                            light, 'switchLevel', 'setLevel', args=[brightness]
                        )
                    if hue is not None:
                        self.execute(light, 'colorControl', 'setHue', args=[hue])
                    if saturation is not None:
                        self.execute(
                            light, 'colorControl', 'setSaturation', args=[saturation]
                        )
                    if temperature is not None:
                        self.execute(
                            light,
                            'colorTemperature',
                            'setColorTemperature',
                            args=[temperature],
                        )
                    if hex is not None:
                        self.execute(light, 'colorControl', 'setColor', args=[hex])
                except Exception as e:
                    self.logger.error('Could not set attributes on %s: %s', light, e)
                    err = e

            if err:
                raise err

    @staticmethod
    def _device_status_to_dict(status: pysmartthings.DeviceStatus) -> dict:
        status_dict = {}
        for attr in status.attributes.keys():
            attr = camel_case_to_snake_case(attr)
            if hasattr(status, attr):
                status_dict[attr] = getattr(status, attr)

        return status_dict

    def _get_devices_status_dict(self) -> Dict[str, dict]:
        return {
            device_id: self._device_status_to_dict(device.status)
            for device_id, device in self._devices_by_id.items()
        }

    @staticmethod
    def _has_status_changed(status: dict, new_status: dict) -> bool:
        if not status and new_status:
            return True

        for attr, value in status.items():
            if attr in new_status:
                new_value = new_status[attr]
                if value != new_value:
                    return True

        return False

    def main(self):
        while not self.should_stop():
            updated_devices = {}
            devices = self._get_devices_status_dict()
            self.status(publish_entities=False)
            new_devices = self._get_devices_status_dict()

            updated_devices = {
                device_id: self._devices_by_id[device_id]
                for device_id, new_status in new_devices.items()
                if self._has_status_changed(devices.get(device_id, {}), new_status)
            }

            self.publish_entities(updated_devices.values())  # type: ignore
            devices = new_devices
            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
