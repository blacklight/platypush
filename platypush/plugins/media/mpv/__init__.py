import os
import threading

from platypush.context import get_bus
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import (
    MediaPlayEvent,
    MediaPlayRequestEvent,
    MediaPauseEvent,
    MediaStopEvent,
    NewPlayingMediaEvent,
    MediaSeekEvent,
    MediaResumeEvent,
)

from platypush.plugins import action


class MediaMpvPlugin(MediaPlugin):
    """
    Plugin to control MPV instances

    Requires:

        * **python-mpv** (``pip install python-mpv``)
        * **mpv** executable on your system
    """

    _default_mpv_args = {
        'ytdl': True,
        'start_event_thread': True,
    }

    def __init__(self, args=None, *argv, **kwargs):
        """
        Create the MPV wrapper.

        :param args: Default arguments that will be passed to the mpv executable
            as a key-value dict (names without the `--` prefix). See `man mpv`
            for available options.
        :type args: dict[str, str]
        """

        super().__init__(*argv, **kwargs)

        self.args = self._default_mpv_args
        if args:
            # noinspection PyTypeChecker
            self.args.update(args)

        self._player = None
        self._playback_rebounce_event = threading.Event()
        self._on_stop_callbacks = []

    def _init_mpv(self, args=None):
        import mpv

        mpv_args = self.args.copy()
        if args:
            mpv_args.update(args)

        for k, v in self._env.items():
            os.environ[k] = v

        self._player = mpv.MPV(**mpv_args)
        # noinspection PyProtectedMember
        self._player._event_callbacks += [self._event_callback()]

    @staticmethod
    def _post_event(evt_type, **evt):
        bus = get_bus()
        bus.post(evt_type(player='local', plugin='media.mpv', **evt))

    def _event_callback(self):
        def callback(event):
            from mpv import (
                MpvEvent,
                MpvEventID as Event,
                MpvEventEndFile as EndFile,
            )

            self.logger.info('Received mpv event: {}'.format(event))

            if isinstance(event, MpvEvent):
                event = event.as_dict()

            evt = event.get('event_id')
            if not evt:
                return

            if (
                evt == Event.FILE_LOADED or evt == Event.START_FILE
            ) and self._get_current_resource():
                self._playback_rebounce_event.set()
                self._post_event(
                    NewPlayingMediaEvent,
                    resource=self._get_current_resource(),
                    title=self._player.filename,
                )
            elif evt == Event.PLAYBACK_RESTART:
                self._playback_rebounce_event.set()
                self._post_event(
                    MediaPlayEvent,
                    resource=self._get_current_resource(),
                    title=self._player.filename,
                )
            elif evt == Event.PAUSE:
                self._post_event(
                    MediaPauseEvent,
                    resource=self._get_current_resource(),
                    title=self._player.filename,
                )
            elif evt == Event.UNPAUSE:
                self._post_event(
                    MediaResumeEvent,
                    resource=self._get_current_resource(),
                    title=self._player.filename,
                )
            elif (
                evt == Event.SHUTDOWN
                or evt == Event.IDLE
                or (
                    evt == Event.END_FILE
                    and event.get('event', {}).get('reason')
                    in [EndFile.EOF, EndFile.ABORTED, EndFile.QUIT]
                )
            ):
                playback_rebounced = self._playback_rebounce_event.wait(timeout=0.5)
                if playback_rebounced:
                    self._playback_rebounce_event.clear()
                    return

                self._player = None
                self._post_event(MediaStopEvent)

                for cbk in self._on_stop_callbacks:
                    cbk()
            elif evt == Event.SEEK:
                self._post_event(MediaSeekEvent, position=self._player.playback_time)

        return callback

    @action
    def execute(self, cmd, **args):
        """
        Execute a raw mpv command.
        """
        if not self._player:
            return None, 'No mpv instance is running'
        return self._player.command(cmd, *args)

    @action
    def play(self, resource, subtitles=None, **args):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL
        :type resource: str

        :param subtitles: Path to optional subtitle file
        :type subtitles: str

        :param args: Extra runtime arguments that will be passed to the
            mpv executable as a key-value dict (keys without `--` prefix)
        :type args: dict[str,str]
        """

        self._post_event(MediaPlayRequestEvent, resource=resource)
        self._init_mpv(args)

        resource = self._get_resource(resource)
        if resource.startswith('file://'):
            resource = resource[7:]

        assert self._player, 'The player is not ready'
        self._player.play(resource)
        if self.volume:
            self.set_volume(volume=self.volume)
        if subtitles:
            self.add_subtitles(subtitles)

        return self.status()

    @action
    def pause(self):
        """Toggle the paused state"""
        if not self._player:
            return None, 'No mpv instance is running'

        self._player.pause = not self._player.pause
        return self.status()

    @action
    def quit(self):
        """Stop and quit the player"""
        if not self._player:
            return None, 'No mpv instance is running'

        self._player.quit()
        self._player.terminate()
        self._player = None
        return {'state': PlayerState.STOP.value}

    @action
    def stop(self):
        """Stop and quit the player"""
        return self.quit()

    @action
    def voldown(self, step=10.0):
        """Volume down by (default: 10)%"""
        if not self._player:
            return None, 'No mpv instance is running'
        return self.set_volume(self._player.volume - step)

    @action
    def volup(self, step=10.0):
        """Volume up by (default: 10)%"""
        if not self._player:
            return None, 'No mpv instance is running'
        return self.set_volume(self._player.volume + step)

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: float
        """
        if not self._player:
            return None, 'No mpv instance is running'

        volume = max(0, min([self._player.volume_max, volume]))
        self._player.volume = volume
        return self.status()

    @action
    def seek(self, position):
        """
        Seek backward/forward by the specified number of seconds

        :param position: Number of seconds relative to the current cursor
        :type position: int
        """
        if not self._player:
            return None, 'No mpv instance is running'
        if not self._player.seekable:
            return None, 'The resource is not seekable'
        pos = min(self._player.time_pos + self._player.time_remaining, max(0, position))
        self._player.time_pos = pos
        return self.status()

    @action
    def back(self, offset=30.0):
        """Back by (default: 30) seconds"""
        if not self._player:
            return None, 'No mpv instance is running'
        if not self._player.seekable:
            return None, 'The resource is not seekable'
        pos = max(0, self._player.time_pos - offset)
        return self.seek(pos)

    @action
    def forward(self, offset=30.0):
        """Forward by (default: 30) seconds"""
        if not self._player:
            return None, 'No mpv instance is running'
        if not self._player.seekable:
            return None, 'The resource is not seekable'
        pos = min(
            self._player.time_pos + self._player.time_remaining,
            self._player.time_pos + offset,
        )
        return self.seek(pos)

    @action
    def next(self):
        """Play the next item in the queue"""
        if not self._player:
            return None, 'No mpv instance is running'
        self._player.playlist_next()

    @action
    def prev(self):
        """Play the previous item in the queue"""
        if not self._player:
            return None, 'No mpv instance is running'
        self._player.playlist_prev()

    @action
    def toggle_subtitles(self, visible=None):
        """Toggle the subtitles visibility"""
        return self.toggle_property('sub_visibility')

    @action
    def add_subtitles(self, filename):
        """Add a subtitles file"""
        return self._player.sub_add(filename)

    @action
    def toggle_fullscreen(self):
        """Toggle the fullscreen mode"""
        return self.toggle_property('fullscreen')

    # noinspection PyShadowingBuiltins
    @action
    def toggle_property(self, property):
        """
        Toggle or sets the value of an mpv property (e.g. fullscreen,
        sub_visibility etc.). See ``man mpv`` for a full list of properties

        :param property: Property to toggle
        """
        if not self._player:
            return None, 'No mpv instance is running'

        if not hasattr(self._player, property):
            self.logger.warning('No such mpv property: {}'.format(property))

        value = not getattr(self._player, property)
        setattr(self._player, property, value)
        return {property: value}

    # noinspection PyShadowingBuiltins
    @action
    def get_property(self, property):
        """
        Get a player property (e.g. pause, fullscreen etc.). See
        ``man mpv`` for a full list of the available properties
        """
        if not self._player:
            return None, 'No mpv instance is running'
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
            return None, 'No mpv instance is running'

        for k, v in props.items():
            setattr(self._player, k, v)
        return props

    @action
    def set_subtitles(self, filename, *args, **kwargs):
        """Sets media subtitles from filename"""
        # noinspection PyTypeChecker
        return self.set_property(subfile=filename, sub_visibility=True)

    @action
    def remove_subtitles(self, sub_id=None):
        """Removes (hides) the subtitles"""
        if not self._player:
            return None, 'No mpv instance is running'
        if sub_id:
            return self._player.sub_remove(sub_id)
        self._player.sub_visibility = False

    @action
    def is_playing(self):
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
    def mute(self):
        """Toggle mute state"""
        if not self._player:
            return None, 'No mpv instance is running'
        mute = not self._player.mute
        self._player.mute = mute
        return {'muted': mute}

    @action
    def set_position(self, position):
        """
        Seek backward/forward to the specified absolute position (same as ``seek``)
        """
        return self.seek(position)

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example::

            output = {
                "filename": "filename or stream URL",
                "state": "play"  # or "stop" or "pause"
            }
        """
        if not self._player or not hasattr(self._player, 'pause'):
            return {'state': PlayerState.STOP.value}

        return {
            'audio_channels': getattr(self._player, 'audio_channels', None),
            'audio_codec': getattr(self._player, 'audio_codec_name', None),
            'delay': getattr(self._player, 'delay', None),
            'duration': getattr(self._player, 'playback_time', 0)
            + getattr(self._player, 'playtime_remaining', 0)
            if getattr(self._player, 'playtime_remaining', None)
            else None,
            'filename': getattr(self._player, 'filename', None),
            'file_size': getattr(self._player, 'file_size', None),
            'fullscreen': getattr(self._player, 'fs', None),
            'mute': getattr(self._player, 'mute', None),
            'name': getattr(self._player, 'name', None),
            'pause': getattr(self._player, 'pause', None),
            'percent_pos': getattr(self._player, 'percent_pos', None),
            'position': getattr(self._player, 'playback_time', None),
            'seekable': getattr(self._player, 'seekable', None),
            'state': (
                PlayerState.PAUSE.value
                if self._player.pause
                else PlayerState.PLAY.value
            ),
            'title': getattr(self._player, 'media_title', None)
            or getattr(self._player, 'filename', None),
            'url': self._get_current_resource(),
            'video_codec': getattr(self._player, 'video_codec', None),
            'video_format': getattr(self._player, 'video_format', None),
            'volume': getattr(self._player, 'volume', None),
            'volume_max': getattr(self._player, 'volume_max', None),
            'width': getattr(self._player, 'width', None),
        }

    def on_stop(self, callback):
        self._on_stop_callbacks.append(callback)

    def _get_current_resource(self):
        if not self._player or not self._player.stream_path:
            return

        return (
            'file://' if os.path.isfile(self._player.stream_path) else ''
        ) + self._player.stream_path

    def _get_resource(self, resource):
        if self._is_youtube_resource(resource):
            return resource  # mpv can handle YouTube streaming natively

        return super()._get_resource(resource)


# vim:sw=4:ts=4:et:
