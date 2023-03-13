from typing import Iterable, Optional

from platypush.entities.bluetooth import BluetoothDevice
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
        name: Optional[str] = None,
        rssi: Optional[int] = None,
        tx_power: Optional[int] = None,
        manufacturer: Optional[str] = None,
        services: Optional[Iterable[dict]] = None,
        **kwargs
    ):
        """
        :param address: The Bluetooth address of the device.
        :param connected: Whether the device is connected.
        :param name: The name of the device.
        :param rssi: Received Signal Strength Indicator.
        :param tx_power: Transmission power.
        :param manufacturers: The manufacturers published by the device, as a
            ``manufacturer_id -> registered_name`` map.
        :param services: The services published by the device.
        """
        super().__init__(
            *args,
            address=address,
            name=name,
            connected=connected,
            rssi=rssi,
            tx_power=tx_power,
            manufacturer=manufacturer,
            services=services,
            **kwargs
        )

    @classmethod
    def from_device(cls, device: BluetoothDevice, **kwargs) -> "BluetoothDeviceEvent":
        """
        Initialize a Bluetooth event from the parameters of a device.

        :param device: Bluetooth device.
        """
        return cls(
            address=device.address,
            name=device.name,
            connected=device.connected,
            rssi=device.rssi,
            tx_power=device.tx_power,
            manufacturer=device.manufacturer,
            services=[srv.to_dict() for srv in device.services],
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


class BluetoothDeviceSignalUpdateEvent(BluetoothDeviceEvent):
    """
    Event triggered when the RSSI/TX power of a Bluetooth device is updated.
    """


class BluetoothConnectionFailedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth connection fails.
    """


class BluetoothFileEvent(BluetoothDeviceEvent):
    """
    Base class for Bluetooth file events.
    """

    def __init__(self, *args, file: str, **kwargs):
        super().__init__(*args, file=file, **kwargs)


class BluetoothFileTransferStartedEvent(BluetoothFileEvent):
    """
    Event triggered when a file transfer is initiated.
    """


class BluetoothFileTransferCancelledEvent(BluetoothFileEvent):
    """
    Event triggered when a file transfer is cancelled.
    """


class BluetoothFileReceivedEvent(BluetoothFileEvent):
    """
    Event triggered when a file download is completed.
    """


class BluetoothFileSentEvent(BluetoothFileEvent):
    """
    Event triggered when a file upload is completed.
    """


class BluetoothFilePutRequestEvent(BluetoothFileEvent):
    """
    Event triggered when a file put request is received.
    """


class BluetoothFileGetRequestEvent(BluetoothFileEvent):
    """
    Event triggered when a file get request is received.
    """


# vim:sw=4:ts=4:et:
