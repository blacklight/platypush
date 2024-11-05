from dataclasses import dataclass
from typing import Optional


@dataclass
class Temperature:
    """
    System temperature sensor data class.
    """

    id: str
    label: Optional[str] = None
    value: Optional[float] = None
    high: Optional[float] = None
    critical: Optional[float] = None
