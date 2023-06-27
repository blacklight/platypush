from abc import ABC
from typing import Optional, Tuple, Union
from platypush.message.event import Event


class SoundEvent(Event, ABC):
    """Base class for sound events"""

    def __init__(
        self, *args, device: Optional[Union[str, Tuple[str, str]]] = None, **kwargs
    ):
        super().__init__(*args, device=device, **kwargs)


class SoundEventWithResource(SoundEvent, ABC):
    """Base class for sound events with resource names attached"""

    def __init__(self, *args, resource: Optional[str] = None, **kwargs):
        super().__init__(*args, resource=resource, **kwargs)


class SoundPlaybackStartedEvent(SoundEventWithResource):
    """
    Event triggered when a new sound playback starts
    """


class SoundPlaybackStoppedEvent(SoundEventWithResource):
    """
    Event triggered when the sound playback stops
    """


class SoundPlaybackPausedEvent(SoundEventWithResource):
    """
    Event triggered when the sound playback pauses
    """


class SoundPlaybackResumedEvent(SoundEventWithResource):
    """
    Event triggered when the sound playback resumsed from a paused state
    """


class SoundRecordingStartedEvent(SoundEventWithResource):
    """
    Event triggered when a new recording starts
    """


class SoundRecordingStoppedEvent(SoundEventWithResource):
    """
    Event triggered when a sound recording stops
    """


class SoundRecordingPausedEvent(SoundEventWithResource):
    """
    Event triggered when a sound recording pauses
    """


class SoundRecordingResumedEvent(SoundEvent):
    """
    Event triggered when a sound recording resumes from a paused state
    """


# vim:sw=4:ts=4:et:
