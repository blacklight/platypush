import os
from typing import Optional

from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import MediaPlayRequestEvent, MediaVolumeChangedEvent

from platypush.plugins import action
from platypush.plugins.media import MediaResource
from platypush.plugins.media.gstreamer.model import MediaPipeline


class MediaGstreamerPlugin(MediaPlugin):
    """
    Plugin to play media over GStreamer.
    """

    def __init__(self, sink: Optional[str] = None, *args, **kwargs):
        """
        :param sink: GStreamer audio sink (default: ``None``, automatic).
        """
        super().__init__(*args, **kwargs)
        self.sink = sink
        self._player: Optional[MediaPipeline] = None

    def _allocate_pipeline(self, resource: MediaResource) -> MediaPipeline:
        pipeline = MediaPipeline(resource)
        if self.sink:
            sink = pipeline.add_sink(self.sink, sync=False)
            pipeline.link(pipeline.get_source(), sink)

        self._player = pipeline
        self._latest_resource = resource
        return pipeline

    def _status(self) -> dict:
        if not self._player:
            return {'state': PlayerState.STOP.value}

        pos = self._player.get_position()
        length = self._player.get_duration()

        status = {
            'duration': length,
            'mute': self._player.is_muted(),
            'pause': self._player.is_paused(),
            'percent_pos': (
                pos / length
                if pos is not None and length is not None and pos >= 0 and length > 0
                else 0
            ),
            'position': pos,
            'seekable': length is not None and length > 0,
            'state': self._gst_to_player_state(self._player.get_state()).value,
            'volume': self._player.get_volume() * 100,
        }

        if self._latest_resource:
            status.update(
                {
                    k: v
                    for k, v in self._latest_resource.to_dict().items()
                    if v is not None
                }
            )

        return status

    def _get_volume(self) -> float:
        assert self._player, 'No instance is running'
        return self._player.get_volume() * 100.0

    def _set_position(self, position: float) -> dict:
        assert self._player, 'No instance is running'
        self._player.seek(position)
        return self._status()

    @action
    def play(self, resource: Optional[str] = None, **kwargs):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL
        """

        if not resource:
            if self._player:
                self._player.play()
            return self._status()

        self._bus.post(
            MediaPlayRequestEvent(
                player='local', plugin='media.gstreamer', resource=resource
            )
        )
        media = self._latest_resource = self._get_resource(resource, **kwargs)
        media.open(**kwargs)
        if media.resource and os.path.isfile(os.path.abspath(media.resource)):
            media.resource = 'file://' + media.resource

        pipeline = self._allocate_pipeline(media)
        pipeline.play()
        if self.volume:
            pipeline.set_volume(self.volume / 100.0)

        return self._status()

    @action
    def pause(self, *_, **__):
        """Toggle the paused state"""
        assert self._player, 'No instance is running'
        self._player.pause()
        return self._status()

    @action
    def quit(self, *_, **__):
        """Stop and quit the player (alias for :meth:`.stop`)"""
        if self._latest_resource:
            self._latest_resource.close()
            self._latest_resource = None

        if self._player:
            self._player.stop()
            self._player = None
        else:
            self.logger.info('No instance is running')

        return {'state': PlayerState.STOP.value}

    @action
    def stop(self):
        """Stop and quit the player (alias for :meth:`.quit`)"""
        return self.quit()

    @action
    def voldown(self, step=10.0):
        """Volume down by (default: 10)%"""
        return self.set_volume(self._get_volume() - step)

    @action
    def volup(self, step=10.0):
        """Volume up by (default: 10)%"""
        return self.set_volume(self._get_volume() + step)

    @action
    def get_volume(self) -> float:
        """
        Get the volume.

        :return: Volume value between 0 and 100.
        """
        assert self._player, 'No instance is running'
        return self._player.get_volume() * 100.0

    @action
    def set_volume(self, volume):
        """
        Set the volume.

        :param volume: Volume value between 0 and 100.
        """
        assert self._player, 'Player not running'
        volume = max(0, min(1, volume / 100.0))
        self._player.set_volume(volume)
        self._player.post_event(MediaVolumeChangedEvent, volume=volume * 100)
        return self._status()

    @action
    def seek(self, position: float) -> dict:
        """
        Seek backward/forward by the specified number of seconds.

        :param position: Number of seconds relative to the current cursor.
        """
        assert self._player, 'No instance is running'
        cur_pos = self._player.get_position()
        # return self._set_position(cur_pos + position)
        return self._set_position((cur_pos or 0) + float(position))

    @action
    def back(self, offset=60.0):
        """Back by (default: 60) seconds"""
        return self.seek(-offset)

    @action
    def forward(self, offset=60.0):
        """Forward by (default: 60) seconds"""
        return self.seek(offset)

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """
        return self._player and self._player.is_playing()

    @action
    def load(self, resource, **_):
        """
        Load/queue a resource/video to the player (alias for :meth:`.play`).
        """
        return self.play(resource)

    @action
    def mute(self):
        """Toggle mute state"""
        assert self._player, 'No instance is running'
        muted = self._player.is_muted()
        if muted:
            self._player.unmute()
        else:
            self._player.mute()

        return {'muted': self._player.is_muted()}

    @action
    def set_position(self, position: float) -> dict:
        """
        Seek backward/forward to the specified absolute position.

        :param position: Stream position in seconds.
        :return: Player state.
        """
        assert self._player, 'No instance is running'
        self._player.seek(position)
        return self._status()

    @action
    def status(self) -> dict:
        """
        Get the current player state.
        """
        return self._status()

    @staticmethod
    def _gst_to_player_state(state) -> PlayerState:
        from gi.repository import Gst  # type: ignore

        if state == Gst.State.PAUSED:
            return PlayerState.PAUSE
        if state == Gst.State.PLAYING:
            return PlayerState.PLAY

        return PlayerState.STOP

    def toggle_subtitles(self, *_, **__):
        raise NotImplementedError

    def set_subtitles(self, *_, **__):
        raise NotImplementedError

    def remove_subtitles(self, *_, **__):
        raise NotImplementedError


# vim:sw=4:ts=4:et:
