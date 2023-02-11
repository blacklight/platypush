from typing import Collection, Optional

from platypush.message.event import Event


class BluetoothEvent(Event):
    """
    Base class for Bluetooth Low-Energy device events.
    """

    def __init__(
        self,
        *args,
        address: str,
        connected: bool,
        paired: bool,
        trusted: bool,
        blocked: bool,
        name: Optional[str] = None,
        service_uuids: Optional[Collection[str]] = None,
        **kwargs
    ):
        """
        :param address: The Bluetooth address of the device.
        :param connected: Whether the device is connected.
        :param paired: Whether the device is paired.
        :param trusted: Whether the device is trusted.
        :param blocked: Whether the device is blocked.
        :param name: The name of the device.
        :param service_uuids: The service UUIDs of the device.
        """
        super().__init__(
            *args,
            address=address,
            name=name,
            connected=connected,
            paired=paired,
            blocked=blocked,
            trusted=trusted,
            service_uuids=service_uuids or [],
            **kwargs
        )


class BluetoothDeviceFoundEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is discovered during a scan.
    """


class BluetoothDeviceLostEvent(BluetoothEvent):
    """
    Event triggered when a previously discovered Bluetooth device is lost.
    """


class BluetoothDeviceConnectedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is connected.
    """


class BluetoothDeviceDisconnectedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is disconnected.
    """


class BluetoothDevicePairedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is paired.
    """


class BluetoothDeviceUnpairedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is unpaired.
    """


class BluetoothDeviceBlockedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is blocked.
    """


class BluetoothDeviceUnblockedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is unblocked.
    """


class BluetoothDeviceTrustedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is trusted.
    """


class BluetoothDeviceUntrustedEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is untrusted.
    """


# vim:sw=4:ts=4:et:
