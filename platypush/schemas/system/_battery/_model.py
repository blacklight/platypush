from dataclasses import dataclass
from typing import Optional


@dataclass
class Battery:
    """
    System battery sensor representation.
    """

    seconds_left: Optional[float] = None
    power_plugged: Optional[bool] = None
    value: Optional[float] = None
