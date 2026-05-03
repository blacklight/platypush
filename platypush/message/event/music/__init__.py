from platypush.message.event import Event


class MusicEvent(Event):
    """Base class for music events"""

    def __init__(self, status, track, plugin_name=None, *args, **kwargs):
        super().__init__(
            *args, status=status, track=track, plugin_name=plugin_name, **kwargs
        )


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


class SeekChangeEvent(MusicEvent):
    """
    Event fired upon seek change
    """

    def __init__(self, position, status=None, track=None, *args, **kwargs):
        super().__init__(*args, position=position, status=status, track=track, **kwargs)


class VolumeChangeEvent(MusicEvent):
    """
    Event fired upon volume change
    """

    def __init__(self, volume, status=None, track=None, *args, **kwargs):
        super().__init__(*args, volume=volume, status=status, track=track, **kwargs)


class MuteChangeEvent(MusicEvent):
    """
    Event fired upon mute change
    """

    def __init__(self, mute, status=None, track=None, *args, **kwargs):
        super().__init__(*args, mute=mute, status=status, track=track, **kwargs)


class PlaybackRepeatModeChangeEvent(MusicEvent):
    """
    Event fired upon repeat mode change
    """

    def __init__(self, state, status=None, track=None, *args, **kwargs):
        super().__init__(*args, state=state, status=status, track=track, **kwargs)


class PlaybackRandomModeChangeEvent(MusicEvent):
    """
    Event fired upon random mode change
    """

    def __init__(self, state, status=None, track=None, *args, **kwargs):
        super().__init__(*args, state=state, status=status, track=track, **kwargs)


class PlaybackConsumeModeChangeEvent(MusicEvent):
    """
    Event fired upon consume mode change
    """

    def __init__(self, state, status=None, track=None, *args, **kwargs):
        super().__init__(*args, state=state, status=status, track=track, **kwargs)


class PlaybackSingleModeChangeEvent(MusicEvent):
    """
    Event fired upon single mode change
    """

    def __init__(self, state, status=None, track=None, *args, **kwargs):
        super().__init__(*args, state=state, status=status, track=track, **kwargs)


class PlaylistChangeEvent(MusicEvent):
    """
    Event fired upon playlist change
    """

    def __init__(self, changes=None, status=None, track=None, *args, **kwargs):
        """
        :param changes: List with the tracks being added or removed
        :type changes: list

        :param status: Player status
        :type status: dict

        :param track: Track being played
        :type track: dict
        """

        super().__init__(*args, changes=changes, status=status, track=track, **kwargs)


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
