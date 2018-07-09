from platypush.message.event import Event


class MusicEvent(Event):
    """ Base class for music events """

    def __init__(self, status, track, *args, **kwargs):
        super().__init__(*args, status=status, track=track, **kwargs)


class MusicPlayEvent(MusicEvent):
    """
    Event fired upon music player playback start
    """

    def __init__(self, status=None, track=None, *args, **kwargs):
        """
        :param status: Player status
        :type status: dict

        :param track: Track being played
        :type track: dict
        """

        super().__init__(*args, status=status, track=track, **kwargs)


class MusicStopEvent(MusicEvent):
    """
    Event fired upon playback stop
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MusicPauseEvent(MusicEvent):
    """
    Event fired upon playback paused
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlaylistChangeEvent(MusicEvent):
    """
    Event fired upon playlist change
    """

    def __init__(self, changes, status=None, track=None, *args, **kwargs):
        """
        :param changes: List with the tracks being added or removed
        :type changes: list

        :param status: Player status
        :type status: dict

        :param track: Track being played
        :type track: dict
        """

        super().__init__(changes=changes, status=status, track=track, *args, **kwargs)


class NewPlayingTrackEvent(MusicEvent):
    """
    Event fired when a new track is being played
    """

    def __init__(self, status=None, track=None, *args, **kwargs):
        """
        :param status: Player status
        :type status: dict

        :param track: Track being played
        :type track: dict
        """

        super().__init__(*args, status=status, track=track, **kwargs)


# vim:sw=4:ts=4:et:

