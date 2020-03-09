from typing import Optional

from platypush.backend.bluetooth.scanner import BluetoothScannerBackend


class BluetoothBleScannerBackend(BluetoothScannerBackend):
    """
    This backend periodically scans for available bluetooth low-energy devices and returns events when a devices enter
    or exits the range.

    Triggers:

        * :class:`platypush.message.event.bluetooth.BluetoothDeviceFoundEvent` when a new bluetooth device is found.
        * :class:`platypush.message.event.bluetooth.BluetoothDeviceLostEvent` when a bluetooth device is lost.

    Requires:

        * The :class:`platypush.plugins.bluetooth.BluetoothBlePlugin` plugin working.

    """

    def __init__(self, interface: Optional[int] = None, scan_duration: int = 10, **kwargs):
        """
        :param interface: Bluetooth adapter name to use (default configured on the ``bluetooth.ble`` plugin if None).
        :param scan_duration:  How long the scan should run (default: 10 seconds).
        """
        super().__init__(plugin='bluetooth.ble', plugin_args={
            'interface': interface,
            'duration': scan_duration,
        }, **kwargs)


# vim:sw=4:ts=4:et:
