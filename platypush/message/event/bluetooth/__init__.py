from typing import Dict, Optional

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


class BluetoothWithPortEvent(Event):
    """
    Base class for Bluetooth events with an associated port.
    """

    def __init__(self, *args, port: Optional[str] = None, **kwargs):
        """
        :param port: The communication port of the device.
        """
        super().__init__(*args, port=port, **kwargs)


class BluetoothDeviceEvent(BluetoothWithPortEvent):
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
        uuids: Optional[Dict[str, str]] = None,
        rssi: Optional[int] = None,
        tx_power: Optional[int] = None,
        manufacturers: Optional[Dict[int, str]] = None,
        manufacturer_data: Optional[Dict[int, str]] = None,
        service_data: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        :param address: The Bluetooth address of the device.
        :param connected: Whether the device is connected.
        :param paired: Whether the device is paired.
        :param trusted: Whether the device is trusted.
        :param blocked: Whether the device is blocked.
        :param name: The name of the device.
        :param uuids: The UUIDs of the services exposed by the device.
        :param rssi: Received Signal Strength Indicator.
        :param tx_power: Transmission power.
        :param manufacturers: The manufacturers published by the device, as a
            ``manufacturer_id -> registered_name`` map.
        :param manufacturer_data: The manufacturer data published by the
            device, as a ``manufacturer_id -> data`` map, where ``data`` is a
            hexadecimal string.
        :param service_data: The service data published by the device, as a
            ``service_uuid -> data`` map, where ``data`` is a hexadecimal string.
        """
        super().__init__(
            *args,
            address=address,
            name=name,
            connected=connected,
            paired=paired,
            blocked=blocked,
            trusted=trusted,
            uuids=uuids or {},
            rssi=rssi,
            tx_power=tx_power,
            manufacturers=manufacturers or {},
            manufacturer_data=manufacturer_data or {},
            service_data=service_data or {},
            **kwargs
        )


class BluetoothDeviceNewDataEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device publishes new manufacturer/service
    data.
    """


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


class BluetoothDeviceSignalUpdateEvent(BluetoothDeviceEvent):
    """
    Event triggered when the RSSI/TX power of a Bluetooth device is updated.
    """


class BluetoothDeviceUntrustedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth device is untrusted.
    """


class BluetoothConnectionRejectedEvent(BluetoothDeviceEvent):
    """
    Event triggered when a Bluetooth connection is rejected.
    """


class BluetoothFilePutRequestEvent(BluetoothWithPortEvent):
    """
    Event triggered when a file put request is received.
    """


class BluetoothFileGetRequestEvent(BluetoothWithPortEvent):
    """
    Event triggered when a file get request is received.
    """


class BluetoothFileReceivedEvent(BluetoothEvent):
    """
    Event triggered when a file transfer is completed.
    """

    def __init__(self, *args, path: str, **kwargs):
        super().__init__(*args, path=path, **kwargs)


# vim:sw=4:ts=4:et:
