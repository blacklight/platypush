class MopidyException(Exception):
    """
    Base class for all Mopidy exceptions.
    """


class EmptyTrackException(MopidyException, ValueError):
    """
    Raised when a parsed track is empty.
    """
