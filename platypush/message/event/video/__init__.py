from platypush.message.event import Event


class VideoEvent(Event):
    """ Base class for video events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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

