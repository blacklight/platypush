from typing import Type

from platypush.common.gstreamer import Pipeline
from platypush.context import get_bus
from platypush.message.event.media import MediaEvent, MediaPlayEvent, MediaPauseEvent, MediaStopEvent, \
    NewPlayingMediaEvent, MediaMuteChangedEvent, MediaSeekEvent


class MediaPipeline(Pipeline):
    def __init__(self, resource: str):
        super().__init__()
        self.resource = resource
        self.add_source('playbin', uri=resource)

    @staticmethod
    def post_event(evt_class: Type[MediaEvent], **kwargs):
        kwargs['player'] = 'local'
        kwargs['plugin'] = 'media.gstreamer'
        evt = evt_class(**kwargs)
        get_bus().post(evt)

    def play(self):
        # noinspection PyUnresolvedReferences,PyPackageRequirements
        from gi.repository import Gst
        is_first_play = self.get_state() == Gst.State.NULL

        super().play()
        if is_first_play:
            self.post_event(NewPlayingMediaEvent, resource=self.resource)
        self.post_event(MediaPlayEvent, resource=self.resource)

    def pause(self):
        # noinspection PyUnresolvedReferences,PyPackageRequirements
        from gi.repository import Gst
        super().pause()
        self.post_event(MediaPauseEvent if self.get_state() == Gst.State.PAUSED else MediaPlayEvent)

    def stop(self):
        super().stop()
        self.post_event(MediaStopEvent)

    def mute(self):
        super().mute()
        self.post_event(MediaMuteChangedEvent, mute=self.is_muted())

    def unmute(self):
        super().unmute()
        self.post_event(MediaMuteChangedEvent, mute=self.is_muted())

    def seek(self, position: float):
        super().seek(position)
        self.post_event(MediaSeekEvent, position=self.get_position())


# vim:sw=4:ts=4:et:
