from typing import Collection, Optional

from platypush.message.event import Event


class BluetoothEvent(Event):
    """
    Base class for Bluetooth events.
    """


class BluetoothScanPausedEvent(BluetoothEvent):
    """
    Event triggered when the Bluetooth scan is paused.
    """

    def __init__(self, *args, duration: Optional[float] = None, **kwargs):
        super().__init__(*args, duration=duration, **kwargs)


class BluetoothScanResumedEvent(BluetoothEvent):
    """
    Event triggered when the Bluetooth scan is resumed.
    """

    def __init__(self, *args, duration: Optional[float] = None, **kwargs):
        super().__init__(*args, duration=duration, **kwargs)


class BluetoothDeviceEvent(BluetoothEvent):
    """
    Base class for Bluetooth device events.
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
        characteristics: Optional[Collection[str]] = None,
        **kwargs
    ):
        """
        :param address: The Bluetooth address of the device.
        :param connected: Whether the device is connected.
        :param paired: Whether the device is paired.
        :param trusted: Whether the device is trusted.
        :param blocked: Whether the device is blocked.
        :param name: The name of the device.
        :param characteristics: The UUIDs of the characteristics exposed by the
            device.
        """
        super().__init__(
            *args,
            address=address,
            name=name,
            connected=connected,
            paired=paired,
            blocked=blocked,
            trusted=trusted,
            characteristics=characteristics or [],
            **kwargs
        )


class BluetoothDeviceFoundEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is discovered during a scan.
    """


class BluetoothDeviceLostEvent(BluetoothDeviceEvent):
    """
    Event triggered when a previously discovered Bluetooth device is lost.
    """


class BluetoothDeviceConnectedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is connected.
    """


class BluetoothDeviceDisconnectedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is disconnected.
    """


class BluetoothDevicePairedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is paired.
    """


class BluetoothDeviceUnpairedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is unpaired.
    """


class BluetoothDeviceBlockedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is blocked.
    """


class BluetoothDeviceUnblockedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is unblocked.
    """


class BluetoothDeviceTrustedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is trusted.
    """


class BluetoothDeviceUntrustedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is untrusted.
    """


# vim:sw=4:ts=4:et:
