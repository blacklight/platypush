import logging
import os
from typing import Any, Type

from PyOBEX.client import Client

from platypush.context import get_bus
from platypush.entities.bluetooth import BluetoothDevice
from platypush.message.event.bluetooth import (
    BluetoothConnectionFailedEvent,
    BluetoothDeviceEvent,
    BluetoothFileSentEvent,
    BluetoothFileTransferCancelledEvent,
    BluetoothFileTransferStartedEvent,
)

from platypush.plugins.bluetooth._legacy import LegacyManager
from platypush.plugins.bluetooth.model import ServiceClass


# pylint: disable=too-few-public-methods
class FileSender:
    """
    Wrapper for the Bluetooth file send OBEX service.
    """

    def __init__(self, scanner: LegacyManager):
        self._scanner = scanner
        self.logger = logging.getLogger(__name__)

    def send_file(
        self,
        file: str,
        device: str,
        data: bytes,
    ):
        """
        Send a file to a device.

        :param file: Name/path of the file to send.
        :param device: Name or address of the device to send the file to.
        :param data: File data.
        """

        dev = self._scanner.get_device(device)
        service = dev.known_services.get(ServiceClass.OBEX_OBJECT_PUSH)
        assert service, (
            f'The device {device} does not expose the service '
            f'{str(ServiceClass.OBEX_OBJECT_PUSH)}'
        )

        port = service.port
        client = self._connect(dev, port)
        self._post_event(BluetoothFileTransferStartedEvent, dev, file=file)
        self._send_file(client, dev, file, data)

    def _send_file(
        self,
        client: Client,
        dev: BluetoothDevice,
        file: str,
        data: bytes,
    ):
        filename = os.path.basename(file)

        try:
            client.put(filename, data)
            self._post_event(BluetoothFileSentEvent, dev, file=file)
        except Exception as e:
            self._post_event(
                BluetoothFileTransferCancelledEvent,
                dev,
                reason=str(e),
                file=file,
            )

            raise AssertionError(
                f'Failed to send file {file} to device {dev.address}: {e}'
            ) from e
        finally:
            client.disconnect()

    def _connect(self, dev: BluetoothDevice, port: str) -> Client:
        client = Client(dev.address, port)

        try:
            client.connect()
            assert (
                client.connection_id is not None
            ), 'Could not establish a connection to the device'
        except Exception as e:
            self._post_event(BluetoothConnectionFailedEvent, dev, reason=str(e))
            raise AssertionError(
                f'Connection to device {dev.address} failed: {e}'
            ) from e

        return client

    def _post_event(
        self,
        event_type: Type[BluetoothDeviceEvent],
        device: BluetoothDevice,
        **event_args: Any,
    ):
        get_bus().post(event_type.from_device(device, **event_args))
