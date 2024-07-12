import os
from dataclasses import asdict
from typing import Any, Dict, Optional, Type
from urllib.parse import quote

from platypush.plugins import action
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import (
    MediaEvent,
    MediaPlayEvent,
    MediaPlayRequestEvent,
    MediaPauseEvent,
    MediaStopEvent,
    NewPlayingMediaEvent,
    MediaSeekEvent,
    MediaResumeEvent,
)


class MediaMpvPlugin(MediaPlugin):
    """
    Plugin to control MPV instances.
    """

    _default_mpv_args = {
        'ytdl': True,
        'start_event_thread': True,
    }

    def __init__(
        self, args: Optional[Dict[str, Any]] = None, fullscreen: bool = False, **kwargs
    ):
        """
        :param args: Default arguments that will be passed to the mpv executable
            as a key-value dict (names without the `--` prefix). See `man mpv`
            for available options.
        :param fullscreen: Set to True if you want media files to be opened in
            fullscreen by default (can be overridden by `.play()`) (default: False)
        """

        super().__init__(**kwargs)

        self.args = {**self._default_mpv_args}
        if args:
            self.args.update(args)
        if fullscreen:
            self.args['fs'] = True

        self._player = None
        self._latest_state = PlayerState.STOP

    def _init_mpv(self, args=None):
        import mpv

        mpv_args = self.args.copy()
        if args:
            mpv_args.update(args)

        for k, v in self._env.items():
            os.environ[k] = v

        self._player = mpv.MPV(**mpv_args)
        self._player._event_callbacks += [self._event_callback()]

    def _post_event(self, evt_type: Type[MediaEvent], **evt):
        self._bus.post(
            evt_type(
                player='local',
                plugin='media.mpv',
                resource=evt.pop('resource', self._resource),
                title=self._filename,
                **evt,
            )
        )

    @property
    def _cur_player(self):
        if self._player and not self._player.core_shutdown:
            return self._player

        return None

    @property
    def _state(self):
        player = self._cur_player
        if not player:
            return PlayerState.STOP

        return PlayerState.PAUSE if player.pause else PlayerState.PLAY

    @property
    def _resource(self):
        if not self._cur_player:
            return None

        cur_resource = self._cur_player.stream_path
        if not cur_resource:
            return None

        return quote(
            ('file://' if os.path.isfile(cur_resource) else '') + str(cur_resource)
        )

    @property
    def _filename(self):
        if not self._cur_player:
            return None

        return self._cur_player.filename

    def _event_callback(self):
        def callback(event):
            from mpv import MpvEvent

            self.logger.info('Received mpv event: %s', event)

            if isinstance(event, MpvEvent):
                event = event.as_dict()
            if not isinstance(event, dict):
                return

            evt_type = event.get('event', b'').decode()
            if not evt_type:
                return

            if evt_type == 'start-file':
                self._post_event(NewPlayingMediaEvent)
            elif evt_type == 'playback-restart':
                self._post_event(MediaPlayEvent)
            elif evt_type in ('shutdown', 'idle', 'end-file'):
                if self._state != PlayerState.PLAY:
                    self._post_event(MediaStopEvent)

                if evt_type == 'shutdown' and self._player:
                    self._player = None
            elif evt_type == 'seek' and self._cur_player:
                self._post_event(
                    MediaSeekEvent, position=self._cur_player.playback_time
                )

            self._latest_state = self._state

        return callback

    @action
    def execute(self, cmd, **args):
        """
        Execute a raw mpv command.
        """
        if not self._cur_player:
            return None

        return self._cur_player.command(cmd, *args)

    @action
    def play(
        self,
        resource: str,
        *_,
        subtitles: Optional[str] = None,
        fullscreen: Optional[bool] = None,
        **args,
    ):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL
        :param subtitles: Path to optional subtitle file
        :param args: Extra runtime arguments that will be passed to the
            mpv executable as a key-value dict (keys without `--` prefix)
        """

        self._post_event(MediaPlayRequestEvent, resource=resource)
        if fullscreen is not None:
            args['fs'] = fullscreen

        self._init_mpv(args)

        resource = self._get_resource(resource)
        if resource.startswith('file://'):
            resource = resource[7:]

        assert self._cur_player, 'The player is not ready'
        self._cur_player.play(resource)
        if self.volume:
            self.set_volume(volume=self.volume)
        if subtitles:
            self.add_subtitles(subtitles)

        return self.status()

    @action
    def pause(self, *_, **__):
        """Toggle the paused state"""
        if not self._cur_player:
            return None

        self._cur_player.pause = not self._cur_player.pause
        return self.status()

    @action
    def quit(self, *_, **__):
        """Stop and quit the player"""
        player = self._cur_player
        if not player:
            return None

        player.stop()
        player.quit(code=0)
        player.wait_for_shutdown(timeout=10)
        player.terminate()
        self._player = None
        return self.status()

    @action
    def stop(self, *_, **__):
        """Stop and quit the player"""
        return self.quit()

    def _set_vol(self, *_, step=10.0, **__):
        if not self._cur_player:
            return None

        return self.set_volume(float(self._cur_player.volume or 0) - step)

    @action
    def voldown(self, *_, step: float = 10.0, **__):
        """Volume down by (default: 10)%"""
        if not self._cur_player:
            return None

        return self.set_volume(float(self._cur_player.volume or 0) - step)

    @action
    def volup(self, step: float = 10.0, **_):
        """Volume up by (default: 10)%"""
        if not self._cur_player:
            return None

        return self.set_volume(float(self._cur_player.volume or 0) + step)

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: float
        """
        if not self._cur_player:
            return None

        max_vol = (
            self._cur_player.volume_max
            if self._cur_player.volume_max is not None
            else 100
        )
        volume = max(0, min([max_vol, volume]))
        self._cur_player.volume = volume
        return self.status()

    @action
    def seek(self, position: float, **_):
        """
        Seek backward/forward by the specified number of seconds

        :param position: Number of seconds relative to the current cursor
        """
        if not self._cur_player:
            return None

        assert self._cur_player.seekable, 'The resource is not seekable'
        self._cur_player.time_pos = min(
            float(self._cur_player.time_pos or 0)
            + float(self._cur_player.time_remaining or 0),
            max(0, position),
        )
        return self.status()

    @action
    def back(self, offset=30.0, **_):
        """Back by (default: 30) seconds"""
        if not self._cur_player:
            return None

        assert self._cur_player.seekable, 'The resource is not seekable'
        cur_pos = float(self._cur_player.time_pos or 0)
        return self.seek(cur_pos - offset)

    @action
    def forward(self, offset=30.0, **_):
        """Forward by (default: 30) seconds"""
        if not self._cur_player:
            return None

        assert self._cur_player.seekable, 'The resource is not seekable'
        cur_pos = float(self._cur_player.time_pos or 0)
        return self.seek(cur_pos + offset)

    @action
    def next(self, **_):
        """Play the next item in the queue"""
        if not self._cur_player:
            return None

        self._cur_player.playlist_next()
        return self.status()

    @action
    def prev(self, **_):
        """Play the previous item in the queue"""
        if not self._cur_player:
            return None

        self._cur_player.playlist_prev()
        return self.status()

    @action
    def toggle_subtitles(self, *_, **__):
        """Toggle the subtitles visibility"""
        return self.toggle_property('sub_visibility')

    @action
    def add_subtitles(self, filename):
        """Add a subtitles file"""
        if not self._cur_player:
            return None

        return self._cur_player.sub_add(filename)

    @action
    def toggle_fullscreen(self):
        """Toggle the fullscreen mode"""
        return self.toggle_property('fullscreen')

    @action
    def toggle_property(self, property):
        """
        Toggle or sets the value of an mpv property (e.g. fullscreen,
        sub_visibility etc.). See ``man mpv`` for a full list of properties

        :param property: Property to toggle
        """
        if not self._player:
            return None

        if not hasattr(self._player, property):
            self.logger.warning('No such mpv property: {}'.format(property))

        value = not getattr(self._player, property)
        setattr(self._player, property, value)
        return {property: value}

    @action
    def get_property(self, property):
        """
        Get a player property (e.g. pause, fullscreen etc.). See
        ``man mpv`` for a full list of the available properties
        """
        if not self._player:
            return None
        return getattr(self._player, property)

    @action
    def set_property(self, **props):
        """
        Set the value of an mpv property (e.g. fullscreen, sub_visibility
        etc.). See ``man mpv`` for a full list of properties

        :param props: Key-value args for the properties to set
        :type props: dict
        """
        if not self._player:
            return None

        for k, v in props.items():
            setattr(self._player, k, v)
        return props

    @action
    def set_subtitles(self, filename, *_, **__):
        """Sets media subtitles from filename"""
        return self.set_property(subfile=filename, sub_visibility=True)

    @action
    def remove_subtitles(self, sub_id=None, **_):
        """Removes (hides) the subtitles"""
        if not self._player:
            return None
        if sub_id:
            return self._player.sub_remove(sub_id)
        self._player.sub_visibility = False

    @action
    def is_playing(self, **_):
        """
        :returns: True if it's playing, False otherwise
        """
        if not self._player:
            return False
        return not self._player.pause

    @action
    def load(self, resource, **args):
        """
        Load/queue a resource/video to the player
        """
        if not self._player:
            return self.play(resource, **args)
        return self._player.loadfile(resource, mode='append-play')

    @action
    def mute(self, **_):
        """Toggle mute state"""
        if not self._player:
            return None
        mute = not self._player.mute
        self._player.mute = mute
        return {'muted': mute}

    @action
    def set_position(self, position: float, **_):
        """
        Seek backward/forward to the specified absolute position (same as ``seek``)
        """
        return self.seek(position)

    @action
    def status(self, **_):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example:

            .. code-block:: javascript

                {
                    "audio_channels": 2,
                    "audio_codec": "mp3",
                    "delay": 0,
                    "duration": 300.0,
                    "file_size": 123456,
                    "filename": "filename or stream URL",
                    "fullscreen": false,
                    "mute": false,
                    "name": "mpv",
                    "pause": false,
                    "percent_pos": 10.0,
                    "position": 30.0,
                    "seekable": true,
                    "state": "play",  // or "stop" or "pause"
                    "title": "filename or stream URL",
                    "url": "file:///path/to/file.mp3",
                    "video_codec": "h264",
                    "video_format": "avc1",
                    "volume": 50.0,
                    "volume_max": 100.0,
                    "width": 1280
                }

        """
        if not self._cur_player:
            return {'state': PlayerState.STOP.value}

        status = {
            'audio_channels': getattr(self._player, 'audio_channels', None),
            'audio_codec': getattr(self._player, 'audio_codec_name', None),
            'delay': getattr(self._player, 'delay', None),
            'duration': (
                (getattr(self._player, 'playback_time', 0) or 0)
                + getattr(self._player, 'playtime_remaining', 0)
                if getattr(self._player, 'playtime_remaining', None)
                else None
            ),
            'filename': getattr(self._player, 'filename', None),
            'file_size': getattr(self._player, 'file_size', None),
            'fullscreen': getattr(self._player, 'fs', None),
            'mute': getattr(self._player, 'mute', None),
            'name': getattr(self._player, 'name', None),
            'pause': getattr(self._player, 'pause', None),
            'percent_pos': getattr(self._player, 'percent_pos', None),
            'position': getattr(self._player, 'playback_time', None),
            'seekable': getattr(self._player, 'seekable', None),
            'state': self._state.value,
            'title': getattr(self._player, 'media_title', None)
            or getattr(self._player, 'filename', None),
            'url': self._resource,
            'video_codec': getattr(self._player, 'video_codec', None),
            'video_format': getattr(self._player, 'video_format', None),
            'volume': getattr(self._player, 'volume', None),
            'volume_max': getattr(self._player, 'volume_max', None),
            'width': getattr(self._player, 'width', None),
        }

        if self._latest_resource:
            status.update(
                {
                    k: v
                    for k, v in asdict(self._latest_resource).items()
                    if v is not None
                }
            )

        if self._state != self._latest_state:
            if not self._cur_player:
                self._post_event(MediaStopEvent)
            else:
                self._post_event(
                    MediaPauseEvent
                    if self._state == PlayerState.PAUSE
                    else MediaResumeEvent
                )

        self._latest_state = self._state
        return status

    def _get_resource(self, resource):
        if self._is_youtube_resource(resource):
            return resource  # mpv can handle YouTube streaming natively

        return super()._get_resource(resource)


# vim:sw=4:ts=4:et:
