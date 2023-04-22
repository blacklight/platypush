from dataclasses import dataclass, field
from typing import Optional

from platypush.schemas.dataclasses import percent_field


@dataclass
class Battery:
    """
    System battery sensor wrapper.
    """

    seconds_left: Optional[float] = field(
        metadata={
            'metadata': {
                'description': 'High threshold for the temperature sensor, in Celsius',
                'example': 75,
            }
        }
    )

    power_plugged: Optional[bool] = field(
        metadata={
            'metadata': {
                'description': 'Whether the battery is plugged in or not',
                'example': False,
            }
        }
    )

    value: Optional[float] = percent_field(
        metadata={
            'metadata': {
                'description': 'Current charge left, as a percentage value '
                'between 0 and 1',
                'example': 0.5,
            }
        }
    )
