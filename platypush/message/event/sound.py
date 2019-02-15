from platypush.message.event import Event


class SoundEvent(Event):
    """ Base class for sound events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SoundPlaybackStartedEvent(SoundEvent):
    """
    Event triggered when a new sound playback starts
    """

    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)


class SoundPlaybackStoppedEvent(SoundEvent):
    """
    Event triggered when the sound playback stops
    """

    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)


class SoundPlaybackPausedEvent(SoundEvent):
    """
    Event triggered when the sound playback pauses
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SoundRecordingStartedEvent(SoundEvent):
    """
    Event triggered when a new recording starts
    """

    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)


class SoundRecordingStoppedEvent(SoundEvent):
    """
    Event triggered when a sound recording stops
    """

    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)


class SoundRecordingPausedEvent(SoundEvent):
    """
    Event triggered when a sound recording pauses
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:
