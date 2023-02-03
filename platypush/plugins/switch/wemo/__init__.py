import contextlib
import ipaddress
from typing import Collection, Dict, List, Mapping, Optional, Union

from platypush.entities import Entity, SwitchEntityManager
from platypush.entities.switches import Switch
from platypush.plugins import RunnablePlugin, action
from platypush.utils.workers import Workers

from .lib import WemoRunner
from .scanner import Scanner


class SwitchWemoPlugin(RunnablePlugin, SwitchEntityManager):
    """
    Plugin to control a Belkin WeMo smart switches
    (https://www.belkin.com/us/Products/home-automation/c/wemo-home-automation/)
    """

    _default_port = 49153

    def __init__(
        self,
        devices: Optional[Union[Collection[str], Mapping[str, str]]] = None,
        netmask: Optional[str] = None,
        port: int = _default_port,
        **kwargs
    ):
        """
        This plugin previously used ``ouimeaux`` for auto-discovery, but it's
        been dropped because:

            1. Too slow
            2. Too heavy
            3. Auto-discovery failed too often

        However, this also means that you now have to specify either:

            - ``devices``: The devices you want to control, as a static list/map
            - ``netmask``: The IP netmask that should be scanned for WeMo devices

        :param devices: List of IP addresses or name->address map containing
            the WeMo Switch devices to control.
        :type devices: list or dict

        :param netmask: Alternatively to a list of static IP->name pairs,  you
            can specify the network mask where the devices should be scanned
            (e.g. '192.168.1.0/24')

        :param port: Port where the WeMo devices are expected to expose the
            RPC/XML over HTTP service (default: 49153)
        """

        super().__init__(**kwargs)
        assert devices or netmask, (
            'Please specify either a static list of devices (either a list of '
            'IP addresses or a name->address map) or an IP netmask to scan for '
            'devices'
        )

        self.port = port
        self.netmask = netmask
        self._devices: Dict[str, str] = {}
        self._init_devices(devices)

    def _init_devices(self, devices):
        if devices:
            self._devices.update(
                devices
                if isinstance(devices, dict)
                else {addr: addr for addr in devices}
            )
        else:
            self._devices = {}

        self._addresses = set(self._devices.values())

    def _get_address(self, device: str) -> str:
        if device not in self._addresses:
            with contextlib.suppress(KeyError):
                return self._devices[device]

        return device

    @action
    # pylint: disable=arguments-differ
    def status(
        self,
        device: Optional[Union[str, Collection[str]]] = None,
        publish_entities: bool = True,
        **__
    ) -> List[dict]:
        if device:
            if isinstance(device, str):
                devices = {device: device}
            else:
                devices = {d: d for d in device}
        else:
            devices = self._devices.copy()

        ret = [
            {
                "id": addr,
                "ip": addr,
                "name": name if name != addr else WemoRunner.get_name(addr),
                "on": WemoRunner.get_state(addr),
            }
            for (name, addr) in devices.items()
        ]

        if publish_entities:
            self.publish_entities(ret)
        return ret

    def transform_entities(self, entities: Collection[dict]) -> List[Entity]:
        return [
            Switch(
                id=dev["id"],
                name=dev["name"],
                state=dev["on"],
                data={
                    "ip": dev["ip"],
                },
            )
            for dev in (entities or [])
        ]

    @action
    def on(self, device: str, **_):  # pylint: disable=arguments-differ
        """
        Turn a switch on

        :param device: Device name or address
        """
        device = self._get_address(device)
        WemoRunner.on(device)
        return self.status(device)

    @action
    def off(self, device: str, **_):  # pylint: disable=arguments-differ
        """
        Turn a switch off

        :param device: Device name or address
        """
        device = self._get_address(device)
        WemoRunner.off(device)
        return self.status(device)

    @action
    def toggle(self, device: str, *_, **__):  # pylint: disable=arguments-differ
        """
        Toggle a device on/off state

        :param device: Device name or address
        """
        device = self._get_address(device)
        WemoRunner.toggle(device)
        return self.status(device)

    @action
    def get_state(self, device: str):
        """
        Get the on state of a device (True/False)

        :param device: Device name or address
        """
        device = self._get_address(device)
        return WemoRunner.get_state(device)

    @action
    def get_name(self, device: str):
        """
        Get the friendly name of a device

        :param device: Device name or address
        """
        device = self._get_address(device)
        return WemoRunner.get_name(device)

    @action
    def scan(
        self, netmask: Optional[str] = None, publish_entities: bool = True
    ) -> List[dict]:
        netmask = netmask or self.netmask
        assert netmask, "Scan not supported: No netmask specified"

        workers = Workers(10, Scanner, port=self.port)
        with workers:
            for addr in ipaddress.IPv4Network(netmask):
                workers.put(addr.exploded)

        devices = {dev.name: dev.addr for dev in workers.responses}

        self._init_devices(devices)
        return self.status(publish_entities=publish_entities).output

    def main(self):
        def scan():
            status = (
                self.scan(publish_entities=False).output
                if not self._devices
                else self.status(self._devices.values(), publish_entities=False).output
            )

            return {dev['ip']: dev for dev in status}

        devices = {}

        while not self.should_stop():
            new_devices = scan()
            updated_devices = {
                ip: new_devices[ip]
                for ip, dev in new_devices.items()
                if any(v != devices.get(ip, {}).get(k) for k, v in dev.items())
            }

            if updated_devices:
                self.publish_entities(updated_devices.values())

            devices = new_devices
            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
