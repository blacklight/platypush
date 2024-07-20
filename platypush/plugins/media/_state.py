import enum


class PlayerState(enum.Enum):
    """
    Models the possible states of a media player
    """

    STOP = 'stop'
    PLAY = 'play'
    PAUSE = 'pause'
    IDLE = 'idle'
