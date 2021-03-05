import asyncio
import aiohttp

from threading import RLock
from typing import Optional, Dict, List, Union

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class SmartthingsPlugin(SwitchPlugin):
    """
    Plugin to interact with devices and locations registered to a Samsung SmartThings account.

    Requires:

        * **pysmartthings** (``pip install pysmartthings``)

    """

    _timeout = aiohttp.ClientTimeout(total=20.)

    def __init__(self, access_token: str, **kwargs):
        """
        :param access_token: SmartThings API access token - you can get one at https://account.smartthings.com/tokens.
        """
        super().__init__(**kwargs)
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

        self._locations_by_id = {
            loc.location_id: loc
            for loc in self._locations
        }

        self._locations_by_name = {
            loc.name: loc
            for loc in self._locations
        }

    async def _refresh_devices(self, api):
        self._devices = await api.devices()

        self._devices_by_id = {
            dev.device_id: dev
            for dev in self._devices
        }

        self._devices_by_name = {
            dev.label: dev
            for dev in self._devices
        }

    async def _refresh_rooms(self, api, location_id: str):
        self._rooms_by_location[location_id] = await api.rooms(location_id=location_id)

        self._rooms_by_id.update(**{
            room.room_id: room
            for room in self._rooms_by_location[location_id]
        })

        self._rooms_by_location_and_id[location_id] = {
            room.room_id: room
            for room in self._rooms_by_location[location_id]
        }

        self._rooms_by_location_and_name[location_id] = {
            room.name: room
            for room in self._rooms_by_location[location_id]
        }

    async def _refresh_info(self):
        import pysmartthings

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
            }
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
            'locations': {loc.location_id: self._location_to_dict(loc) for loc in self._locations},
            'devices': {dev.device_id: self._device_to_dict(dev) for dev in self._devices},
        }

    @action
    def get_location(self, location_id: Optional[str] = None, name: Optional[str] = None) -> dict:
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
        if location_id not in self._locations_by_id or name not in self._locations_by_name:
            self.refresh_info()

        location = self._locations_by_id.get(location_id, self._locations_by_name.get(name))
        assert location, 'Location {} not found'.format(location_id or name)
        return self._location_to_dict(location)

    def _get_device(self, device: str):
        if device not in self._devices_by_id or device not in self._devices_by_name:
            self.refresh_info()

        device = self._devices_by_id.get(device, self._devices_by_name.get(device))
        assert device, 'Device {} not found'.format(device)
        return device

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

    async def _execute(self, device_id: str, capability: str, command, component_id: str, args: Optional[list]):
        import pysmartthings

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            api = pysmartthings.SmartThings(session, self._access_token)
            device = await api.device(device_id)
            ret = await device.command(component_id=component_id, capability=capability, command=command, args=args)

        assert ret, 'The command {capability}={command} failed on device {device}'.format(
            capability=capability, command=command, device=device_id)

    @action
    def execute(self,
                device: str,
                capability: str,
                command,
                component_id: str = 'main',
                args: Optional[list] = None):
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
                loop.run_until_complete(self._execute(
                    device_id=device.device_id, capability=capability, command=command,
                    component_id=component_id, args=args))
            finally:
                loop.stop()

    @staticmethod
    async def _get_device_status(api, device_id: str) -> dict:
        device = await api.device(device_id)
        await device.status.refresh()

        return {
            'device_id': device_id,
            'name': device.label,
            **{
                cap: getattr(device.status, cap)
                for cap in device.capabilities
                if hasattr(device.status, cap)
                and not callable(getattr(device.status, cap))
            }
        }

    async def _refresh_status(self, devices: List[str]) -> List[dict]:
        import pysmartthings

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
        assert not missing_device_ids, 'Could not find the following devices: {}'.format(list(missing_device_ids))

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            api = pysmartthings.SmartThings(session, self._access_token)
            status_tasks = [
                asyncio.ensure_future(self._get_device_status(api, device_id))
                for device_id in device_ids
            ]

            # noinspection PyTypeChecker
            return await asyncio.gather(*status_tasks)

    @action
    def status(self, device: Optional[Union[str, List[str]]] = None) -> List[dict]:
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
                return loop.run_until_complete(self._refresh_status(devices))
            finally:
                loop.stop()

    @action
    def on(self, device: str, *args, **kwargs) -> dict:
        """
        Turn on a device with ``switch`` capability.

        :param device: Device name or ID.
        :return: Device status
        """
        self.execute(device, 'switch', 'on')
        # noinspection PyUnresolvedReferences
        return self.status(device).output[0]

    @action
    def off(self, device: str, *args, **kwargs) -> dict:
        """
        Turn off a device with ``switch`` capability.

        :param device: Device name or ID.
        :return: Device status
        """
        self.execute(device, 'switch', 'off')
        # noinspection PyUnresolvedReferences
        return self.status(device).output[0]

    @action
    def toggle(self, device: str, *args, **kwargs) -> dict:
        """
        Toggle a device with ``switch`` capability.

        :param device: Device name or ID.
        :return: Device status
        """
        import pysmartthings

        device = self._get_device(device)
        device_id = device.device_id

        async def _toggle() -> bool:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                api = pysmartthings.SmartThings(session, self._access_token)
                dev = await api.device(device_id)
                assert 'switch' in dev.capabilities, 'The device {} has no switch capability'.format(dev.label)

                await dev.status.refresh()
                state = 'off' if dev.status.switch else 'on'
                ret = await dev.command(component_id='main', capability='switch', command=state, args=args)

            assert ret, 'The command switch={state} failed on device {device}'.format(state=state, device=dev.label)
            return not dev.status.switch

        with self._refresh_lock:
            loop = asyncio.new_event_loop()
            state = loop.run_until_complete(_toggle())
            return {
                'id': device_id,
                'name': device.label,
                'on': state,
            }

    @property
    def switches(self) -> List[dict]:
        """
        :return: List of switch devices statuses in :class:`platypush.plugins.switch.SwitchPlugin` compatible format.
            Example:

          .. code-block:: json

            [
              {
                "id": "switch-1",
                "name": "Fan",
                "on": false
              },
              {
                "id": "tv-1",
                "name": "Samsung Smart TV",
                "on": true
              }
            ]

        """
        # noinspection PyUnresolvedReferences
        devices = self.status().output
        return [
            {
                'name': device['name'],
                'id': device['device_id'],
                'on': device['switch'],
            }
            for device in devices
            if 'switch' in device
        ]


# vim:sw=4:ts=4:et:
