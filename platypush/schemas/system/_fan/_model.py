from dataclasses import dataclass
from typing import Optional


@dataclass
class Fan:
    """
    System fan sensor data class.
    """

    id: str
    label: Optional[str] = None
    value: Optional[float] = None
