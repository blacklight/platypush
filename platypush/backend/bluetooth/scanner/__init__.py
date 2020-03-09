from typing import Dict, Optional

from platypush.backend.sensor import SensorBackend
from platypush.message.event.bluetooth import BluetoothDeviceFoundEvent, BluetoothDeviceLostEvent


class BluetoothScannerBackend(SensorBackend):
    """
    This backend periodically scans for available bluetooth devices and returns events when a devices enter or exits
    the range.

    Triggers:

        * :class:`platypush.message.event.bluetooth.BluetoothDeviceFoundEvent` when a new bluetooth device is found.
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceLostEvent` when a bluetooth device is lost.

    Requires:

        * The :class:`platypush.plugins.bluetooth.BluetoothPlugin` plugin working.

    """

    def __init__(self, device_id: Optional[int] = None, scan_duration: int = 10, **kwargs):
        """
        :param device_id: Bluetooth adapter ID to use (default configured on the ``bluetooth`` plugin if None).
        :param scan_duration:  How long the scan should run (default: 10 seconds).
        """
        super().__init__(plugin='bluetooth', plugin_args={
            'device_id': device_id,
            'duration': scan_duration,
        }, **kwargs)

        self._last_seen_devices = {}

    def process_data(self, data: Dict[str, dict], new_data: Dict[str, dict]):
        for addr, dev in data.items():
            if addr not in self._last_seen_devices:
                self.bus.post(BluetoothDeviceFoundEvent(address=dev.pop('addr'), **dev))
            self._last_seen_devices[addr] = {'addr': addr, **dev}

        for addr, dev in self._last_seen_devices.copy().items():
            if addr not in data:
                self.bus.post(BluetoothDeviceLostEvent(address=dev.pop('addr'), **dev))
                del self._last_seen_devices[addr]


# vim:sw=4:ts=4:et:
