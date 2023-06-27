from dataclasses import dataclass
from enum import Enum
from typing import Union

DeviceType = Union[int, str]


@dataclass
class AudioDevice:
    """
    Maps the properties of an audio device.
    """

    index: int
    name: str
    hostapi: int
    max_input_channels: int
    max_output_channels: int
    default_samplerate: int
    default_low_input_latency: float = 0
    default_low_output_latency: float = 0
    default_high_input_latency: float = 0
    default_high_output_latency: float = 0


class AudioState(Enum):
    """
    Audio states.
    """

    STOPPED = 'STOPPED'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'


class StreamType(Enum):
    """
    Stream types.
    """

    INPUT = 'input'
    OUTPUT = 'output'
