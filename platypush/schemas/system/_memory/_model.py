from dataclasses import dataclass


@dataclass
class MemoryStats:
    """
    Memory stats data class.
    """

    total: int
    available: int
    used: int
    free: int
    active: int
    inactive: int
    buffers: int
    cached: int
    shared: int
    percent: float


@dataclass
class SwapStats:
    """
    Swap memory stats data class.
    """

    total: int
    used: int
    free: int
    percent: float
