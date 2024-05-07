from dataclasses import dataclass, field


@dataclass
class Intent:
    """
    Speech intent data class.
    """

    name: str
    slots: dict = field(default_factory=dict)
