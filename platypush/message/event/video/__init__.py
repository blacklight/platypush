from platypush.message.event import Event


class VideoEvent(Event):
    """ Base class for music events """

    def __init__(self, status, track, *args, **kwargs):
        super().__init__(*args, status=status, video=video, **kwargs)


class VideoPlayEvent(VideoEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VideoStopEvent(VideoEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VideoPauseEvent(VideoEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NewPlayingVideoEvent(VideoEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

