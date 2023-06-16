from enum import Enum


class AudioState(Enum):
    """
    Audio states.
    """

    STOPPED = 'STOPPED'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
