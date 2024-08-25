from typing import Type

from platypush.common.gstreamer import Pipeline
from platypush.context import get_bus
from platypush.message.event.media import (
    MediaEvent,
    MediaPlayEvent,
    MediaPauseEvent,
    MediaStopEvent,
    NewPlayingMediaEvent,
    MediaMuteChangedEvent,
    MediaSeekEvent,
)
from platypush.plugins.media import MediaResource


class MediaPipeline(Pipeline):
    def __init__(self, resource: MediaResource):
        super().__init__()

        self.resource = resource
        self._first_play = True
        if resource.resource and resource.fd is None:
            self.add_source('playbin', uri=resource.resource)
        elif resource.fd is not None:
            self.add_source('playbin', uri=f'fd://{resource.fd.fileno()}')
        else:
            raise AssertionError('No resource specified')

    def post_event(self, evt_class: Type[MediaEvent], **kwargs):
        kwargs['player'] = 'local'
        kwargs['plugin'] = 'media.gstreamer'

        if self.resource:
            resource_args = self.resource.to_dict()
            resource_args.pop('type', None)
            kwargs.update(resource_args)

        evt = evt_class(**kwargs)
        get_bus().post(evt)

    def on_play(self):
        super().on_play()
        if self._first_play:
            self.post_event(NewPlayingMediaEvent, resource=self.resource)
            self._first_play = False

        self.post_event(MediaPlayEvent)

    def on_pause(self):
        super().on_pause()
        self.post_event(MediaPauseEvent)

    def play(self):
        from gi.repository import Gst

        self._first_play = self.get_state() == Gst.State.NULL
        super().play()

    def stop(self):
        super().stop()
        self._first_play = True
        self.post_event(MediaStopEvent)

    def mute(self):
        super().mute()
        self.post_event(MediaMuteChangedEvent, mute=self.is_muted())

    def unmute(self):
        super().unmute()
        self.post_event(MediaMuteChangedEvent, mute=self.is_muted())

    def seek(self, position: float):
        from gi.repository import Gst

        if not self.source:
            self.logger.info('Cannot seek on a pipeline without a source')
            return

        position = max(0, position)
        duration = self.get_duration()
        if duration and position > duration:
            position = duration

        cur_pos = self.get_position() or 0
        seek_ns = int((position - cur_pos) * 1e9)
        self.source.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)
        self.post_event(MediaSeekEvent, position=self.get_position())


# vim:sw=4:ts=4:et:
