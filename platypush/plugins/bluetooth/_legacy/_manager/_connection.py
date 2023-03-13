from dataclasses import dataclass, field
from logging import getLogger
from threading import Event, Thread, current_thread
from typing import Optional

import bluetooth

from platypush.entities.bluetooth import BluetoothService

from ._types import ConnectionId

_logger = getLogger(__name__)


@dataclass
class BluetoothConnection:
    """
    Models a connection to a Bluetooth device.
    """

    address: str
    service: BluetoothService
    socket: bluetooth.BluetoothSocket = field(
        init=False, default_factory=bluetooth.BluetoothSocket
    )
    thread: Thread = field(default_factory=current_thread)
    stop_event: Event = field(default_factory=Event)

    def __post_init__(self):
        """
        Initialize the Bluetooth socket with the given protocol.
        """
        self.socket = bluetooth.BluetoothSocket(self.service.protocol.value)

    @property
    def key(self) -> ConnectionId:
        return self.address, self.service.port

    def close(self, timeout: Optional[float] = None):
        _logger.info('Closing connection to %s', self.address)

        # Set the stop event
        self.stop_event.set()

        # Close the socket
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                _logger.warning(
                    'Failed to close Bluetooth socket on %s: %s',
                    self.address,
                    e,
                )

        # Avoid deadlocking by waiting for our own thread to terminate
        if current_thread() is self.thread:
            return

        # Wait for the connection thread to terminate
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
        if self.thread and self.thread.is_alive():
            _logger.warning('Connection to %s still alive after closing', self.address)
