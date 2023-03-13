import asyncio
from dataclasses import dataclass
import threading
from typing import Optional

from bleak import BleakClient
from bleak.backends.device import BLEDevice


@dataclass
class BluetoothConnection:
    """
    A class to store information and context about a Bluetooth connection.
    """

    client: BleakClient
    device: BLEDevice
    loop: asyncio.AbstractEventLoop
    close_event: Optional[asyncio.Event] = None
    thread: Optional[threading.Thread] = None
