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


class NewPlayingTrackEvent(MusicEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

