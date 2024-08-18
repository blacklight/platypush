import enum


class PlayerState(enum.Enum):
    """
    Models the possible states of a media player
    """

    STOP = 'stop'
    PLAY = 'play'
    PAUSE = 'pause'
    IDLE = 'idle'


class DownloadState(enum.Enum):
    """
    Enum that represents the status of a download.
    """

    IDLE = 'idle'
    STARTED = 'started'
    DOWNLOADING = 'downloading'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ERROR = 'error'


# vim:sw=4:ts=4:et:
