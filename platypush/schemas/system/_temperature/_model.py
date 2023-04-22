from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Temperature:
    """
    System temperature sensor wrapper.
    """

    id: str = field(
        metadata={
            'metadata': {
                'description': 'Unique ID for the sensor',
                'example': 'acpi_1',
            }
        }
    )

    label: str = field(
        metadata={
            'metadata': {
                'description': 'Name of the sensor',
                'example': 'CPU',
            }
        }
    )

    value: float = field(
        metadata={
            'metadata': {
                'description': 'Current temperature value, in Celsius',
                'example': 55,
            }
        }
    )

    high: Optional[float] = field(
        metadata={
            'metadata': {
                'description': 'High threshold for the temperature sensor, in Celsius',
                'example': 75,
            }
        }
    )

    critical: Optional[float] = field(
        metadata={
            'metadata': {
                'description': 'Critical threshold for the temperature sensor, in Celsius',
                'example': 95,
            }
        }
    )
