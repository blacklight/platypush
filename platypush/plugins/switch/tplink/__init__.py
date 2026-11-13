import asyncio
import threading
from typing import (
    Collection,
    Dict,
    List,
    Mapping,
    Optional,
    Union,
)

from kasa import (
    Device,
    Discover,
    KasaException,
    Module,
)

from platypush.entities import Entity, SwitchEntityManager
from platypush.plugins import RunnablePlugin, action


class SwitchTplinkPlugin(RunnablePlugin, SwitchEntityManager):
    """
    Plugin to interact with TP-Link smart switches/plugs like the HS100
    (https://www.tp-link.com/us/products/details/cat-5516_HS100.html).
    """

    _ip_to_dev: Dict[str, Device] = {}
    _alias_to_dev: Dict[str, Device] = {}

    _ASYNC_TIMEOUT = 30

    def __init__(
        self,
        plugs: Optional[Union[Mapping[str, str], List[str]]] = None,
        bulbs: Optional[Union[Mapping[str, str], List[str]]] = None,
        strips: Optional[Union[Mapping[str, str], List[str]]] = None,
        **kwargs,
    ):
        """
        :param plugs: Optional list of IP addresses or name->address mappings if you have a static list of
            TP-Link plugs and you want to save on the scan time.
        :param bulbs: Optional list of IP addresses or name->address mappings if you have a static list of
            TP-Link bulbs and you want to save on the scan time.
        :param strips: Optional list of IP addresses or name->address mappings if you have a static list of
            TP-Link strips and you want to save on the scan time.
        """
        super().__init__(**kwargs)
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()

        self._ip_to_dev = {}
        self._alias_to_dev = {}
        self._static_devices = {}

        if isinstance(plugs, list):
            plugs = {addr: addr for addr in plugs}
        if isinstance(bulbs, list):
            bulbs = {addr: addr for addr in bulbs}
        if isinstance(strips, list):
            strips = {addr: addr for addr in strips}

        for devices in (plugs, bulbs, strips):
            for name, addr in (devices or {}).items():
                self._static_devices[addr] = {'name': name}

        self._update_devices()

    def stop(self):
        super().stop()
        try:
            self._loop.call_soon_threadsafe(self._loop.stop)
        except RuntimeError:
            pass
        self._loop_thread.join(timeout=5)
        self._loop.close()

    def _run_async(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(
            timeout=self._ASYNC_TIMEOUT
        )

    def _update_devices(
        self,
        devices: Optional[Mapping[str, Device]] = None,
        publish_entities: bool = True,
    ):
        for addr, info in self._static_devices.items():
            try:
                dev = self._run_async(Device.connect(host=addr))
                self._run_async(dev.update())
                self._alias_to_dev[info.get('name', dev.alias)] = dev
                self._ip_to_dev[addr] = dev
            except (KasaException, OSError) as e:
                self.logger.warning('Could not update device %s: %s', addr, e)

        for ip, dev in (devices or {}).items():
            self._ip_to_dev[ip] = dev
            self._alias_to_dev[dev.alias] = dev

        if devices and publish_entities:
            self.publish_entities(devices.values())

    def transform_entities(self, entities: Collection[Device]):
        from platypush.entities.switches import Switch

        return super().transform_entities(
            [
                Switch(
                    id=dev.host,
                    name=dev.alias,
                    state=dev.is_on,
                    data={
                        'current_consumption': self._current_consumption(dev),
                        'ip': dev.host,
                        'host': dev.host,
                        'hw_info': dev.hw_info,
                    },
                )
                for dev in (entities or [])
            ]
        )

    def _scan(self, publish_entities: bool = True) -> Dict[str, Device]:
        try:
            devices = self._run_async(Discover.discover())
        except (KasaException, OSError) as e:
            self.logger.warning('Device discovery failed: %s', e)
            return {}
        for dev in devices.values():
            try:
                self._run_async(dev.update())
            except (KasaException, OSError) as e:
                self.logger.warning(
                    'Could not communicate with device %s: %s', dev.host, e
                )
        self._update_devices(devices, publish_entities=publish_entities)
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
        raise RuntimeError(f'Device {device} not found')

    def _set(self, device: Device, state: bool):
        action_name = 'turn_on' if state else 'turn_off'
        act = getattr(device, action_name, None)
        if not (act):
            raise AssertionError(
                f'No such action available on the device "{device.alias}": '
                f'"{action_name}"'
            )
        self._run_async(act())
        self._run_async(device.update())
        self.publish_entities([device])
        return self._serialize(device)

    @action
    def on(self, device, **_):  # pylint: disable=arguments-differ
        """
        Turn on a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        return self._set(device, True)

    @action
    def off(self, device, **_):  # pylint: disable=arguments-differ
        """
        Turn off a device

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        return self._set(device, False)

    @action
    def toggle(self, device, **_):  # pylint: disable=arguments-differ
        """
        Toggle the state of a device (on/off)

        :param device: Device IP, hostname or alias
        :type device: str
        """

        device = self._get_device(device)
        return self._set(device, not device.is_on)

    def _current_consumption(self, device: Device) -> Optional[float]:
        try:
            if Module.Energy not in device.modules:
                return None
            return device.modules[Module.Energy].current_consumption
        except (KasaException, OSError) as e:
            self.logger.debug(
                'Could not retrieve current consumption for device %s: %s',
                device.host,
                e,
            )
            return None

    def _serialize(self, device: Device) -> Optional[dict]:
        try:
            return {
                'current_consumption': self._current_consumption(device),
                'id': device.host,
                'ip': device.host,
                'host': device.host,
                'hw_info': device.hw_info,
                'name': device.alias,
                'on': device.is_on,
            }
        except (KasaException, OSError) as e:
            self.logger.warning('Could not serialize device %s: %s', device.host, e)

    @action
    def status(self, *_, **__) -> List[dict]:
        """
        Retrieve the current status of the devices. Return format:

            .. code-block:: json

                [
                    {
                        "current_consumption": 0.5,
                        "id": "192.168.1.123",
                        "ip": "192.168.1.123",
                        "host": "192.168.1.123",
                        "hw_info": "00:11:22:33:44:55",
                        "name": "My Switch",
                        "on": true,
                    }
                ]

        """
        return [
            ser_dev
            for ser_dev in [self._serialize(dev) for dev in self._scan().values()]
            if ser_dev
        ]

    def main(self):
        devices = {
            ip_: dev_
            for ip_, dev_ in {
                ip: self._serialize(dev) for ip, dev in self._ip_to_dev.items()
            }.items()
            if dev_
        }

        while not self.should_stop():
            new_devices = self._scan(publish_entities=False)
            new_serialized_devices = {
                ip_: dev_
                for ip_, dev_ in {
                    ip: self._serialize(dev) for ip, dev in new_devices.items()
                }.items()
                if dev_
            }

            updated_devices = {
                ip: new_devices[ip]
                for ip, dev in new_serialized_devices.items()
                if any(v != devices.get(ip, {}).get(k) for k, v in dev.items())
            }

            if updated_devices:
                self.publish_entities(updated_devices.values())

            devices = new_serialized_devices
            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
