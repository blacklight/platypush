import enum
import time
from typing import Any, Collection, Dict, List, Optional

from platypush.entities import EnumSwitchEntityManager
from platypush.entities.switches import EnumSwitch
from platypush.message.response.bluetooth import BluetoothScanResponse
from platypush.plugins import action
from platypush.plugins.bluetooth.ble import BluetoothBlePlugin


# pylint: disable=too-many-ancestors
class SwitchbotBluetoothPlugin(BluetoothBlePlugin, EnumSwitchEntityManager):
    """
    Plugin to interact with a Switchbot (https://www.switch-bot.com/) device and
    programmatically control switches over a Bluetooth interface.

    See :class:`platypush.plugins.bluetooth.ble.BluetoothBlePlugin` for how to enable BLE permissions for
    the platypush user (a simple solution may be to run it as root, but that's usually NOT a good idea).

    Requires:

        * **pybluez** (``pip install pybluez``)
        * **gattlib** (``pip install gattlib``)
        * **libboost** (on Debian ```apt-get install libboost-python-dev libboost-thread-dev``)

    """

    uuid = 'cba20002-224d-11e6-9fb8-0002a5d5c51b'
    handle = 0x16

    class Command(enum.Enum):
        """
        Base64 encoded commands
        """

        # \x57\x01\x00
        PRESS = 'VwEA'
        # # \x57\x01\x01
        ON = 'VwEB'
        # # \x57\x01\x02
        OFF = 'VwEC'

    def __init__(
        self,
        interface=None,
        connect_timeout=None,
        scan_timeout=2,
        devices=None,
        **kwargs
    ):
        """
        :param interface: Bluetooth interface to use (e.g. hci0) default: first available one
        :type interface: str

        :param connect_timeout: Timeout for the connection to the Switchbot device - default: None
        :type connect_timeout: float

        :param scan_timeout: Timeout for the scan operations
        :type scan_timeout: float

        :param devices: Devices to control, as a MAC address -> name map
        :type devices: dict
        """
        super().__init__(interface=interface, **kwargs)

        self.connect_timeout = connect_timeout if connect_timeout else 5
        self.scan_timeout = scan_timeout if scan_timeout else 2
        self.configured_devices = devices or {}
        self.configured_devices_by_name = {
            name: addr for addr, name in self.configured_devices.items()
        }

    def _run(self, device: str, command: Command):
        device = self.configured_devices_by_name.get(device, '')
        n_tries = 1

        try:
            self.write(
                device,
                command.value,
                handle=self.handle,
                channel_type='random',
                binary=True,
            )
        except Exception as e:
            self.logger.exception(e)
            n_tries -= 1

            if n_tries == 0:
                raise e
            time.sleep(5)

        return self.status(device)

    @action
    def press(self, device):
        """
        Send a press button command to a device

        :param device: Device name or address
        :type device: str
        """
        return self._run(device, self.Command.PRESS)

    @action
    def toggle(self, device, **_):
        return self.press(device)

    @action
    def on(self, device, **_):
        """
        Send a press-on button command to a device

        :param device: Device name or address
        :type device: str
        """
        return self._run(device, self.Command.ON)

    @action
    def off(self, device, **_):
        """
        Send a press-off button command to a device

        :param device: Device name or address
        :type device: str
        """
        return self._run(device, self.Command.OFF)

    @action
    # pylint: disable=arguments-differ
    def set_value(self, device: str, data: str, *_, **__):
        """
        Entity-compatible ``set_value`` method to send a command to a device.

        :param device: Device name or address
        :param data: Command to send. Possible values are:

            - ``on``: Press the button and remain in the pressed state.
            - ``off``: Release a previously pressed button.
            - ``press``: Press and release the button.

        """
        if data == 'on':
            return self.on(device)
        if data == 'off':
            return self.off(device)
        if data == 'press':
            return self.press(device)

        self.logger.warning('Unknown command for SwitchBot "%s": "%s"', device, data)
        return None

    @action
    def scan(
        self, interface: Optional[str] = None, duration: int = 10
    ) -> BluetoothScanResponse:
        """
        Scan for available Switchbot devices nearby.

        :param interface: Bluetooth interface to scan (default: default configured interface)
        :param duration: Scan duration in seconds
        """

        compatible_devices: Dict[str, Any] = {}
        devices = (
            super().scan(interface=interface, duration=duration).devices  # type: ignore
        )

        for dev in devices:
            try:
                characteristics = [
                    chrc
                    for chrc in self.discover_characteristics(  # type: ignore
                        dev['addr'],
                        channel_type='random',
                        wait=False,
                        timeout=self.scan_timeout,
                    ).characteristics
                    if chrc.get('uuid') == self.uuid
                ]

                if characteristics:
                    compatible_devices[dev['addr']] = None
            except Exception as e:
                self.logger.warning('Device scan error: %s', e)

        self.publish_entities(compatible_devices)
        return BluetoothScanResponse(devices=compatible_devices)

    @action
    def status(self, *_, **__) -> List[dict]:
        self.publish_entities(self.configured_devices)
        return [
            {
                'address': addr,
                'id': addr,
                'name': name,
                'on': False,
            }
            for addr, name in self.configured_devices.items()
        ]

    def transform_entities(self, entities: Collection[dict]) -> Collection[EnumSwitch]:
        return [
            EnumSwitch(
                id=addr,
                name=name,
                value='on',
                values=['on', 'off', 'press'],
                is_write_only=True,
            )
            for addr, name in entities
        ]


# vim:sw=4:ts=4:et:
