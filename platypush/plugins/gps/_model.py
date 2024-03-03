from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class DeviceMode(Enum):
    """
    GPS device mode.
    """

    NO_FIX = 1  # No fix
    TWO_D = 2  # 2D fix
    THREE_D = 3  # 3D fix (including altitude)


@dataclass
class GpsDevice:
    """
    Models the GPS device.
    """

    path: str
    activated: Optional[datetime] = None
    native: bool = False
    baudrate: Optional[int] = None
    parity: str = 'N'
    stopbits: Optional[int] = None
    cycle: Optional[float] = None
    driver: Optional[str] = None
    subtype: Optional[str] = None
    mode: Optional[DeviceMode] = None


@dataclass
class GpsStatus:
    """
    Models the status of the GPS service.
    """

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    satellites_used: int = 0
    devices: Dict[str, GpsDevice] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
