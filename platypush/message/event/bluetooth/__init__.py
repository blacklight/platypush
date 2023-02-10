from typing import Optional

from platypush.message.event import Event


class BluetoothEvent(Event):
    """
    Base class for Bluetooth events.
    """

    def __init__(self, address: str, *args, name: Optional[str] = None, **kwargs):
        super().__init__(*args, address=address, name=name, **kwargs)


class BluetoothWithPortEvent(BluetoothEvent):
    """
    Base class for Bluetooth events that include a communication port.
    """

    def __init__(self, *args, port: Optional[str] = None, **kwargs):
        super().__init__(*args, port=port, **kwargs)


class BluetoothDeviceFoundEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device is found during a scan.
    """


class BluetoothDeviceLostEvent(BluetoothEvent):
    """
    Event triggered when a Bluetooth device previously scanned is lost.
    """


class BluetoothDeviceConnectedEvent(BluetoothWithPortEvent):
    """
    Event triggered when a Bluetooth device is connected.
    """


class BluetoothDeviceDisconnectedEvent(BluetoothWithPortEvent):
    """
    Event triggered when a Bluetooth device is disconnected.
    """


class BluetoothConnectionRejectedEvent(BluetoothWithPortEvent):
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
