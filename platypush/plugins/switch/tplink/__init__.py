from typing import Union, Mapping, List, Collection, Optional

from pyHS100 import (
    SmartDevice,
    SmartPlug,
    SmartBulb,
    SmartStrip,
    Discover,
    SmartDeviceException,
)

from platypush.entities import Entity
from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class SwitchTplinkPlugin(SwitchPlugin):
    """
    Plugin to interact with TP-Link smart switches/plugs like the HS100
    (https://www.tp-link.com/us/products/details/cat-5516_HS100.html).

    Requires:

        * **pyHS100** (``pip install pyHS100``)

    """

    _ip_to_dev = {}
    _alias_to_dev = {}

    def __init__(
        self,
        plugs: Optional[Union[Mapping[str, str], List[str]]] = None,
        bulbs: Optional[Union[Mapping[str, str], List[str]]] = None,
        strips: Optional[Union[Mapping[str, str], List[str]]] = None,
        **kwargs
    ):
        """
        :param plugs: Optional list of IP addresses or name->address mapping if you have a static list of
            TpLink plugs and you want to save on the scan time.
        :param bulbs: Optional list of IP addresses or name->address mapping if you have a static list of
            TpLink bulbs and you want to save on the scan time.
        :param strips: Optional list of IP addresses or name->address mapping if you have a static list of
            TpLink strips and you want to save on the scan time.
        """
        super().__init__(**kwargs)
        self._ip_to_dev = {}
        self._alias_to_dev = {}
        self._static_devices = {}

        if isinstance(plugs, list):
            plugs = {addr: addr for addr in plugs}
        if isinstance(bulbs, list):
            bulbs = {addr: addr for addr in bulbs}
        if isinstance(strips, list):
            strips = {addr: addr for addr in strips}

        for name, addr in (plugs or {}).items():
            self._static_devices[addr] = {
                'name': name,
                'type': SmartPlug,
            }

        for name, addr in (bulbs or {}).items():
            self._static_devices[addr] = {
                'name': name,
                'type': SmartBulb,
            }

        for name, addr in (strips or {}).items():
            self._static_devices[addr] = {
                'name': name,
                'type': SmartStrip,
            }

        self._update_devices()

    def _update_devices(self, devices: Optional[Mapping[str, SmartDevice]] = None):
        for (addr, info) in self._static_devices.items():
            try:
                dev = info['type'](addr)
                self._alias_to_dev[info.get('name', dev.alias)] = dev
                self._ip_to_dev[addr] = dev
            except SmartDeviceException as e:
                self.logger.warning(
                    'Could not communicate with device {}: {}'.format(addr, str(e))
                )

        for (ip, dev) in (devices or {}).items():
            self._ip_to_dev[ip] = dev
            self._alias_to_dev[dev.alias] = dev

        if devices:
            self.publish_entities(devices.values())  # type: ignore

    def transform_entities(self, devices: Collection[SmartDevice]):
        from platypush.entities.switches import Switch

        return super().transform_entities(  # type: ignore
            [
                Switch(
                    id=dev.host,
                    name=dev.alias,
                    state=dev.is_on,
                    data={
                        'current_consumption': dev.current_consumption(),
                        'ip': dev.host,
                        'host': dev.host,
                        'hw_info': dev.hw_info,
                    },
                )
                for dev in (devices or [])
            ]
        )

    def _scan(self):
        devices = Discover.discover()
        self._update_devices(devices)
        return devices

    def _get_device(self, device, use_cache=True):
        if not use_cache:
            self._scan()

        if isinstance(device, Entity):
            device = device.external_id or device.name

        if device in self._ip_to_dev:
            return self._ip_to_dev[device]

        if device in self._alias_to_dev:
            return self._alias_to_dev[device]

        if use_cache:
            return self._get_device(device, use_cache=False)
        else:
            raise RuntimeError('Device {} not found'.format(device))

    def _set(self, device: SmartDevice, state: bool):
        action_name = 'turn_on' if state else 'turn_off'
        action = getattr(device, action_name)
        action()
        self.publish_entities([device])  # type: ignore
        return self._serialize(device)

    @action
    def on(self, device, **_):
        """
        Turn on a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        return self._set(device, True)

    @action
    def off(self, device, **_):
        """
        Turn off a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        return self._set(device, False)

    @action
    def toggle(self, device, **_):
        """
        Toggle the state of a device (on/off)

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        return self._set(device, not device.is_on)

    @staticmethod
    def _serialize(device: SmartDevice) -> dict:
        return {
            'current_consumption': device.current_consumption(),
            'id': device.host,
            'ip': device.host,
            'host': device.host,
            'hw_info': device.hw_info,
            'name': device.alias,
            'on': device.is_on,
        }

    @property
    def switches(self) -> List[dict]:
        return [self._serialize(dev) for dev in self._scan().values()]


# vim:sw=4:ts=4:et:
