import os
import threading
import urllib.parse
from typing import Optional

from platypush.context import get_bus
from platypush.plugins.media import PlayerState, MediaPlugin
from platypush.message.event.media import MediaPlayEvent, MediaPlayRequestEvent, \
    MediaPauseEvent, MediaStopEvent, MediaSeekEvent, MediaVolumeChangedEvent, \
    MediaMuteChangedEvent, NewPlayingMediaEvent

from platypush.plugins import action


class MediaVlcPlugin(MediaPlugin):
    """
    Plugin to control vlc instances

    Requires:

        * **python-vlc** (``pip install python-vlc``)
        * **vlc** executable on your system
    """

    def __init__(self, args=None, fullscreen=False, volume=100, *argv, **kwargs):
        """
        Create the vlc wrapper.

        :param args: List of extra arguments to pass to the VLC executable (e.g.
            ``['--sub-language=en', '--snapshot-path=/mnt/snapshots']``)
        :type args: list[str]

        :param fullscreen: Set to True if you want media files to be opened in
            fullscreen by default (can be overridden by `.play()`) (default: False)
        :type fullscreen: bool

        :param volume: Default media volume (default: 100)
        :type volume: int
        """

        super().__init__(*argv, **kwargs)

        self._args = args or []
        self._instance = None
        self._player = None
        self._latest_seek = None
        self._default_fullscreen = fullscreen
        self._default_volume = volume
        self._on_stop_callbacks = []
        self._title = None
        self._filename = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._on_stop_event = threading.Event()
        self._stop_lock = threading.RLock()

    @classmethod
    def _watched_event_types(cls):
        import vlc
        return [getattr(vlc.EventType, evt) for evt in [
            'MediaPlayerLengthChanged', 'MediaPlayerMediaChanged',
            'MediaDurationChanged', 'MediaPlayerMuted',
            'MediaPlayerUnmuted', 'MediaPlayerOpening', 'MediaPlayerPaused',
            'MediaPlayerPlaying', 'MediaPlayerPositionChanged',
            'MediaPlayerStopped', 'MediaPlayerTimeChanged', 'MediaStateChanged',
            'MediaPlayerForward', 'MediaPlayerBackward',
            'MediaPlayerEndReached', 'MediaPlayerTitleChanged',
            'MediaPlayerAudioVolume',
        ] if hasattr(vlc.EventType, evt)]

    def _init_vlc(self, resource):
        import vlc

        if self._instance:
            self.logger.info('Another instance is running, waiting for it to terminate')
            self._on_stop_event.wait()

        self._reset_state()

        for k, v in self._env.items():
            os.environ[k] = v

        self._monitor_thread = threading.Thread(target=self._player_monitor)
        self._monitor_thread.start()
        self._instance = vlc.Instance(*self._args)
        self._player = self._instance.media_player_new(resource)

        for evt in self._watched_event_types():
            self._player.event_manager().event_attach(
                eventtype=evt, callback=self._event_callback())

    def _player_monitor(self):
        self._on_stop_event.wait()
        self.logger.info('VLC stream terminated')
        self._reset_state()

    def _reset_state(self):
        with self._stop_lock:
            self._latest_seek = None
            self._title = None
            self._filename = None
            self._on_stop_event.clear()

            if self._player:
                self.logger.info('Releasing VLC player resource')
                self._player.release()
                self._player = None

            if self._instance:
                self.logger.info('Releasing VLC instance resource')
                self._instance.release()
                self._instance = None

    @staticmethod
    def _post_event(evt_type, **evt):
        bus = get_bus()
        bus.post(evt_type(player='local', plugin='media.vlc', **evt))

    def _event_callback(self):
        def callback(event):
            from vlc import EventType
            self.logger.debug('Received vlc event: {}'.format(event))

            if event.type == EventType.MediaPlayerPlaying:
                self._post_event(MediaPlayEvent, resource=self._get_current_resource())
            elif event.type == EventType.MediaPlayerPaused:
                self._post_event(MediaPauseEvent)
            elif event.type == EventType.MediaPlayerStopped or \
                    event.type == EventType.MediaPlayerEndReached:
                self._on_stop_event.set()
                self._post_event(MediaStopEvent)
                for cbk in self._on_stop_callbacks:
                    cbk()
            elif (
                    event.type == EventType.MediaPlayerTitleChanged or
                    event.type == EventType.MediaPlayerMediaChanged
            ):
                self._title = self._player.get_title() or self._filename
                if event.type == EventType.MediaPlayerMediaChanged:
                    self._post_event(NewPlayingMediaEvent, resource=self._title)
            elif event.type == EventType.MediaPlayerLengthChanged:
                self._post_event(NewPlayingMediaEvent, resource=self._get_current_resource())
            elif event.type == EventType.MediaPlayerTimeChanged:
                pos = float(self._player.get_time()/1000)
                if self._latest_seek is None or \
                        abs(pos-self._latest_seek) > 5:
                    self._post_event(MediaSeekEvent, position=pos)
                self._latest_seek = pos
            elif event.type == EventType.MediaPlayerAudioVolume:
                self._post_event(MediaVolumeChangedEvent, volume=self._player.audio_get_volume())
            elif event.type == EventType.MediaPlayerMuted:
                self._post_event(MediaMuteChangedEvent, mute=True)
            elif event.type == EventType.MediaPlayerUnmuted:
                self._post_event(MediaMuteChangedEvent, mute=False)

        return callback

    @action
    def play(self, resource=None, subtitles=None, fullscreen=None, volume=None):
        """
        Play a resource.

        :param resource: Resource to play - can be a local file or a remote URL (default: None == toggle play).
        :type resource: str

        :param subtitles: Path to optional subtitle file
        :type subtitles: str

        :param fullscreen: Set to explicitly enable/disable fullscreen (default:
            `fullscreen` configured value or False)
        :type fullscreen: bool

        :param volume: Set to explicitly set the playback volume (default:
            `volume` configured value or 100)
        :type fullscreen: bool
        """

        if not resource:
            return self.pause()

        self._post_event(MediaPlayRequestEvent, resource=resource)
        resource = self._get_resource(resource)

        if resource.startswith('file://'):
            resource = resource[len('file://'):]

        self._filename = resource
        self._init_vlc(resource)
        if subtitles:
            if subtitles.startswith('file://'):
                subtitles = subtitles[len('file://'):]
            self._player.video_set_subtitle_file(subtitles)

        self._player.play()
        if self.volume:
            self.set_volume(volume=self.volume)

        if fullscreen or self._default_fullscreen:
            self.set_fullscreen(True)

        if volume is not None or self._default_volume is not None:
            self.set_volume(volume if volume is not None
                            else self._default_volume)

        return self.status()

    @action
    def pause(self):
        """ Toggle the paused state """
        if not self._player:
            return None, 'No vlc instance is running'
        if not self._player.can_pause():
            return None, 'The specified media type cannot be paused'

        self._player.pause()
        return self.status()

    @action
    def quit(self):
        """ Quit the player (same as `stop`) """
        with self._stop_lock:
            if not self._player:
                return None, 'No vlc instance is running'

            self._player.stop()
            self._on_stop_event.wait(timeout=5)
            self._reset_state()
            return self.status()

    @action
    def stop(self):
        """ Stop the application (same as `quit`) """
        return self.quit()

    @action
    def voldown(self, step=10.0):
        """ Volume down by (default: 10)% """
        if not self._player:
            return None, 'No vlc instance is running'
        return self.set_volume(int(max(0, self._player.audio_get_volume()-step)))

    @action
    def volup(self, step=10.0):
        """ Volume up by (default: 10)% """
        if not self._player:
            return None, 'No vlc instance is running'
        return self.set_volume(int(min(100, self._player.audio_get_volume()+step)))

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: float
        """
        if not self._player:
            return None, 'No vlc instance is running'

        volume = max(0, min([100, volume]))
        self._player.audio_set_volume(volume)
        status = self.status().output
        status['volume'] = volume
        return status

    @action
    def seek(self, position):
        """
        Seek backward/forward by the specified number of seconds

        :param position: Number of seconds relative to the current cursor
        :type position: int
        """
        if not self._player:
            return None, 'No vlc instance is running'
        if not self._player.is_seekable():
            return None, 'The resource is not seekable'

        media = self._player.get_media()
        if not media:
            return None, 'No media loaded'

        pos = min(media.get_duration()/1000, max(0, position))
        self._player.set_time(int(pos*1000))
        return self.status()

    @action
    def back(self, offset=30.0):
        """ Back by (default: 30) seconds """
        if not self._player:
            return None, 'No vlc instance is running'

        media = self._player.get_media()
        if not media:
            return None, 'No media loaded'

        pos = max(0, (self._player.get_time()/1000)-offset)
        return self.seek(pos)

    @action
    def forward(self, offset=30.0):
        """ Forward by (default: 30) seconds """
        if not self._player:
            return None, 'No vlc instance is running'

        media = self._player.get_media()
        if not media:
            return None, 'No media loaded'

        pos = min(media.get_duration()/1000, (self._player.get_time()/1000)+offset)
        return self.seek(pos)

    @action
    def toggle_subtitles(self, visibile=None):
        """ Toggle the subtitles visibility """
        if not self._player:
            return None, 'No vlc instance is running'

        if self._player.video_get_spu_count() == 0:
            return None, 'The media file has no subtitles set'

        if self._player.video_get_spu() is None or \
                self._player.video_get_spu() == -1:
            self._player.video_set_spu(0)
        else:
            self._player.video_set_spu(-1)

    @action
    def toggle_fullscreen(self):
        """ Toggle the fullscreen mode """
        if not self._player:
            return None, 'No vlc instance is running'
        self._player.toggle_fullscreen()

    @action
    def set_fullscreen(self, fullscreen=True):
        """ Set fullscreen mode """
        if not self._player:
            return None, 'No vlc instance is running'
        self._player.set_fullscreen(fullscreen)

    @action
    def set_subtitles(self, filename, **args):
        """ Sets media subtitles from filename """
        if not self._player:
            return None, 'No vlc instance is running'
        if filename.startswith('file://'):
            filename = filename[len('file://'):]

        self._player.video_set_subtitle_file(filename)

    @action
    def remove_subtitles(self):
        """ Removes (hides) the subtitles """
        if not self._player:
            return None, 'No vlc instance is running'
        self._player.video_set_spu(-1)

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """
        if not self._player:
            return False
        return self._player.is_playing()

    @action
    def load(self, resource, **args):
        """
        Load/queue a resource/video to the player
        """
        if not self._player:
            return self.play(resource, **args)
        self._player.set_media(resource)
        return self.status()

    @action
    def mute(self):
        """ Toggle mute state """
        if not self._player:
            return None, 'No vlc instance is running'
        self._player.audio_toggle_mute()

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
        import vlc

        with self._stop_lock:
            if not self._player:
                return {'state': PlayerState.STOP.value}

            status = {}
            vlc_state = self._player.get_state()

            if vlc_state == vlc.State.Playing:
                status['state'] = PlayerState.PLAY.value
            elif vlc_state == vlc.State.Paused:
                status['state'] = PlayerState.PAUSE.value
            else:
                status['state'] = PlayerState.STOP.value

            status['url'] = urllib.parse.unquote(self._player.get_media().get_mrl()) if self._player.get_media() else None
            status['position'] = float(self._player.get_time()/1000) if self._player.get_time() is not None else None

            media = self._player.get_media()
            status['duration'] = media.get_duration()/1000 if media and media.get_duration() is not None else None

            status['seekable'] = status['duration'] is not None
            status['fullscreen'] = self._player.get_fullscreen()
            status['mute'] = self._player.audio_get_mute()
            status['path'] = status['url']
            status['pause'] = status['state'] == PlayerState.PAUSE.value
            status['percent_pos'] = self._player.get_position()*100
            status['filename'] = self._filename
            status['title'] = self._title
            status['volume'] = self._player.audio_get_volume()
            status['volume_max'] = 100

            return status

    def on_stop(self, callback):
        self._on_stop_callbacks.append(callback)

    def _get_current_resource(self):
        if not self._player or not self._player.get_media():
            return
        return self._player.get_media().get_mrl()


# vim:sw=4:ts=4:et:
