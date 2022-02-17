import time
from threading import Thread, RLock
from typing import Dict, Optional, List

from platypush.backend.sensor import SensorBackend
from platypush.context import get_plugin
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

    def __init__(self, device_id: Optional[int] = None, scan_duration: int = 10,
                 track_devices: Optional[List[str]] = None, **kwargs):
        """
        :param device_id: Bluetooth adapter ID to use (default configured on the ``bluetooth`` plugin if None).
        :param scan_duration:  How long the scan should run (default: 10 seconds).
        :param track_devices: List of addresses of devices to actively track, even if they aren't discoverable.
        """
        super().__init__(plugin='bluetooth', plugin_args={
            'device_id': device_id,
            'duration': scan_duration,
        }, **kwargs)

        self._last_seen_devices = {}
        self._tracking_thread: Optional[Thread] = None
        self._bt_lock = RLock()
        self.track_devices = set(track_devices or [])
        self.scan_duration = scan_duration

    def _add_last_seen_device(self, dev):
        addr = dev.pop('addr')
        if addr not in self._last_seen_devices:
            self.bus.post(BluetoothDeviceFoundEvent(address=addr, **dev))
        self._last_seen_devices[addr] = {'addr': addr, **dev}

    def _remove_last_seen_device(self, addr: str):
        dev = self._last_seen_devices.get(addr)
        if not dev:
            return

        self.bus.post(BluetoothDeviceLostEvent(address=addr, **dev))
        del self._last_seen_devices[addr]

    def _addr_tracker(self, addr):
        with self._bt_lock:
            name = get_plugin('bluetooth').lookup_name(addr, timeout=self.scan_duration).name

        if name is None:
            self._remove_last_seen_device(addr)
        else:
            self._add_last_seen_device({'addr': addr, 'name': name})

    def _bt_tracker(self):
        self.logger.info('Starting Bluetooth tracker')
        while not self.should_stop():
            trackers = []
            for addr in self.track_devices:
                tracker = Thread(target=self._addr_tracker, args=(addr,))
                tracker.start()
                trackers.append(tracker)

            for tracker in trackers:
                tracker.join(timeout=self.scan_duration)

            time.sleep(self.scan_duration)

        self.logger.info('Bluetooth tracker stopped')

    def get_measurement(self):
        with self._bt_lock:
            return super().get_measurement()

    def process_data(  # lgtm [py/inheritance/signature-mismatch]
        self, data: Dict[str, dict], new_data: Optional[Dict[str, dict]] = None, **_
    ):
        for addr, dev in data.items():
            self._add_last_seen_device(dev)

        for addr, dev in self._last_seen_devices.copy().items():
            if addr not in data and addr not in self.track_devices:
                self._remove_last_seen_device(addr)

    def run(self):
        self._tracking_thread = Thread(target=self._bt_tracker)
        self._tracking_thread.start()
        super().run()

    def on_stop(self):
        super().on_stop()
        if self._tracking_thread and self._tracking_thread.is_alive():
            self.logger.info('Waiting for the Bluetooth tracking thread to stop')
            self._tracking_thread.join(timeout=self.scan_duration)


# vim:sw=4:ts=4:et:
