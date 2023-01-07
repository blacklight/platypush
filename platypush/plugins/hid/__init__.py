from collections.abc import Iterable
from multiprocessing import Process
from typing import Dict, List, Optional
from time import sleep

import hid

from platypush.context import get_bus
from platypush.message.event.hid import (
    HidDeviceConnectedEvent,
    HidDeviceDataEvent,
    HidDeviceDisconnectedEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.hid import HidDeviceSchema, HidMonitoredDeviceSchema


class HidPlugin(RunnablePlugin):
    """
    This plugin can be used to interact directly with HID devices (including
    Bluetooth, USB and several serial and wireless devices) over the raw
    interface.

    This is the preferred way of communicating with joypads.

    Note that on Linux reading from the devices requires the user running the
    Platypush service to have (at least) read access to the ``/dev/hidraw*``
    devices. However, it is still possible to get connected/disconnected events
    even without having to open a connection to the device. A way to make HID
    raw devices accessible to e.g. a particular user group is via udev rules.
    For example, create a file named ``/etc/udev/rules.d/99-hid.rules`` with
    the following content::

        # Make all /dev/hidraw* devices accessible in read/write to users in
        # the group input
        KERNEL=="hidraw*", GROUP="input", MODE="0660"

    A more granular solution is to provide read and/or write access only to a
    specific device that you want to access, and only to the specific user
    running the Platypush service::

        KERNEL=="hidraw*", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", USER="user", MODE="0660"

    If you don't want to reboot the device after adding the rules, then you can
    reload the rules for udev service and re-trigger them::

        # udevadm control --reload && udevadm trigger

    Triggers:

        * :class:`platypush.message.event.hid.HidDeviceConnectedEvent` when a
          device is connected
        * :class:`platypush.message.event.hid.HidDeviceDisconnectedEvent` when
          a previously available device is disconnected
        * :class:`platypush.message.event.hid.HidDeviceDataEvent` when a
          monitored device sends some data

    """

    def __init__(
        self,
        monitored_devices: Optional[Iterable[dict]] = None,
        poll_seconds: int = 1,
        **kwargs,
    ):
        """
        :param monitored_devices: Map of devices that should be monitored for
            new data. Format (note that all the device filtering attributes are
            optional):

            .. schema:: hid.HidMonitoredDeviceSchema(many=True)

        :param poll_seconds: How often the plugin should check for changes in
            the list of devices (default: 1 second).
        """
        super().__init__(**kwargs)
        self._poll_seconds = poll_seconds
        self._filters = HidMonitoredDeviceSchema().load(
            monitored_devices or [], many=True
        )

        self._device_monitors: Dict[str, Process] = {}
        self._available_devices: Dict[str, dict] = {}

    def main(self):
        while not self.should_stop():
            scanned_devices = {
                dev['path']: dev for dev in self.get_devices().output  # type: ignore
            }

            self._handle_device_events(scanned_devices)
            self._available_devices = scanned_devices
            if self._poll_seconds and self._poll_seconds > 0:
                sleep(self._poll_seconds)

    def stop(self):
        device_monitors = self._device_monitors.copy()
        for monitored_device in device_monitors:
            self._unregister_device_monitor(monitored_device)

        super().stop()

    @action
    def get_devices(self) -> List[dict]:
        """
        Get the HID devices available on the host.

        :return: .. schema:: hid.HidDeviceSchema(many=True)
        """
        return list(  # type: ignore
            {
                dev['path']: HidDeviceSchema().load(dev)
                for dev in hid.enumerate()  # type: ignore
            }.values()
        )

    def _get_monitor_rule(self, device: dict) -> Optional[dict]:
        """
        :return: .. schema:: hid.HidMonitoredDeviceSchema
        """
        matching_rules = [
            rule
            for rule in (self._filters or [])
            if all(
                rule[attr] == device.get(attr)
                for attr in (
                    'path',
                    'serial_number',
                    'vendor_id',
                    'product_id',
                    'manufacturer_string',
                    'product_string',
                )
                if rule.get(attr)
            )
        ]

        if matching_rules:
            return matching_rules[0]

    def _device_monitor(self, dev_def: dict, rule: dict):
        path = dev_def['path']
        data_size = rule['data_size']
        poll_seconds = rule['poll_seconds']
        notify_only_if_changed = rule['notify_only_if_changed']
        last_data = None
        self.logger.info(f'Starting monitor for device {path}')

        def wait():
            if poll_seconds and poll_seconds > 0:
                sleep(poll_seconds)

        while True:
            device = None

            try:
                if not device:
                    device = hid.Device(dev_def['vendor_id'], dev_def['product_id'])  # type: ignore
                data = device.read(data_size)
            except Exception as e:
                if device:
                    self.logger.warning(f'Read error from {path}: {e}')
                device = None
                sleep(5)
                continue

            if not notify_only_if_changed or data != last_data:
                data_dump = ''.join(f'{x:02x}' for x in data)
                get_bus().post(HidDeviceDataEvent(data=data_dump, **dev_def))
                last_data = data

            wait()

    def _register_device_monitor(self, device: dict, rule: dict):
        """
        Register a monitor for a device.
        """
        path = device['path']
        # Make sure that no other monitors are registered for this device
        self._unregister_device_monitor(path)
        monitor_proc = self._device_monitors[path] = Process(
            target=self._device_monitor, args=(device, rule)
        )

        monitor_proc.start()

    def _unregister_device_monitor(self, path: str):
        """
        Unregister a monitor for a device.
        """
        monitor_proc = self._device_monitors.get(path)
        if monitor_proc and monitor_proc.is_alive():
            self.logger.info(f'Terminating monitor for device {path}')

            try:
                monitor_proc.terminate()
                monitor_proc.join(2)
                if monitor_proc.is_alive():
                    monitor_proc.kill()
            except Exception as e:
                self.logger.warning(f'Error while terminating monitor for {path}: {e}')

            del self._device_monitors[path]

    def _handle_new_devices(self, scanned_devices: dict):
        """
        Handles connection events and monitor registering.
        """
        scanned_device_paths = set(scanned_devices.keys())
        available_device_paths = set(self._available_devices)
        new_device_paths = scanned_device_paths.difference(available_device_paths)

        for path in new_device_paths:
            device = scanned_devices[path]
            get_bus().post(HidDeviceConnectedEvent(**device))
            monitor_rule = self._get_monitor_rule(device)
            if monitor_rule:
                self._register_device_monitor(device, monitor_rule)

    def _handle_disconnected_devices(self, scanned_devices: dict):
        """
        Handles disconnection events and monitor unregistering.
        """
        scanned_device_paths = set(scanned_devices.keys())
        available_device_paths = set(self._available_devices)
        lost_device_paths = available_device_paths.difference(scanned_device_paths)

        for path in lost_device_paths:
            device = self._available_devices.get(path)
            if device:
                get_bus().post(HidDeviceDisconnectedEvent(**device))
                self._unregister_device_monitor(device['path'])

    def _handle_device_events(self, scanned_devices: dict):
        """
        Handles connected/disconnected device events and register/unregister the
        monitors based on the user-provided rules when required.
        """
        self._handle_new_devices(scanned_devices)
        self._handle_disconnected_devices(scanned_devices)
