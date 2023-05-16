from dataclasses import dataclass, field
import threading


@dataclass
class ComponentContext:
    """
    This class is used to store the context of a component type.
    """

    init_lock: threading.RLock = field(default_factory=threading.RLock)
    refreshed: threading.Event = field(default_factory=threading.Event)
