from platypush.message.event import Event


class MusicEvent(Event):
    """ Base class for music events """

    def __init__(self, status, track, *args, **kwargs):
        super().__init__(*args, status=status, track=track, **kwargs)


class MusicPlayEvent(MusicEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MusicStopEvent(MusicEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MusicPauseEvent(MusicEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlaylistChangeEvent(MusicEvent):
    def __init__(self, changes, status=None, track=None, *args, **kwargs):
        super().__init__(changes=changes, status=status, track=track, *args, **kwargs)


class NewPlayingTrackEvent(MusicEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

