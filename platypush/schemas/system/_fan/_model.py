from dataclasses import dataclass, field


@dataclass
class Fan:
    """
    System fan sensor data class.
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
                'description': 'Current fan speed, in RPM',
                'example': 3000,
            }
        }
    )
