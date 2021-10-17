import enum
import threading
import urllib.parse

from platypush.context import get_bus
from platypush.plugins.media import MediaPlugin, PlayerState
from platypush.message.event.media import MediaPlayEvent, MediaPauseEvent, MediaStopEvent, MediaSeekEvent, MediaPlayRequestEvent

from platypush.plugins import action


class PlayerEvent(enum.Enum):
    STOP = 'stop'
    PLAY = 'play'
    PAUSE = 'pause'


class MediaOmxplayerPlugin(MediaPlugin):
    """
    Plugin to control video and media playback using OMXPlayer.

    Requires:

        * **omxplayer** installed on your system (see your distro instructions)
        * **omxplayer-wrapper** (``pip install omxplayer-wrapper``)
    """

    def __init__(self, args=None, *argv, timeout: float = 20., **kwargs):
        """
        :param args: Arguments that will be passed to the OMXPlayer constructor
            (e.g. subtitles, volume, start position, window size etc.) see
            https://github.com/popcornmix/omxplayer#synopsis and
            https://python-omxplayer-wrapper.readthedocs.io/en/latest/omxplayer/#omxplayer.player.OMXPlayer
        :type args: list
        :param timeout: How long the plugin should wait for a video to start upon play request (default: 20 seconds).
        """

        super().__init__(*argv, **kwargs)

        if args is None:
            args = []

        self.args = args
        self.timeout = timeout
        self._player = None
        self._handlers = {e.value: [] for e in PlayerEvent}
        self._play_started = threading.Event()

    @action
    def play(self, resource=None, subtitles=None, *args, **kwargs):
        """
        Play or resume playing a resource.

        :param resource: Resource to play. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * YouTube videos (format: ``https://www.youtube.com/watch?v=<id>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)

        :param subtitles: Subtitles file
        """
        if not resource:
            if not self._player:
                self.logger.warning('No OMXPlayer instances running')
            else:
                self._player.play()

            return self.status()
        else:
            self._play_started.clear()

        self._post_event(MediaPlayRequestEvent, resource=resource)

        if subtitles:
            args += ('--subtitles', subtitles)

        resource = self._get_resource(resource)
        if self._player:
            try:
                self._player.stop()
                self._player = None
            except Exception as e:
                self.logger.exception(e)
                self.logger.warning('Unable to stop a previously running instance ' +
                                    'of OMXPlayer, trying to play anyway')

        from dbus import DBusException

        try:
            from omxplayer import OMXPlayer
            self._player = OMXPlayer(resource, args=self.args)
        except DBusException as e:
            self.logger.warning('DBus connection failed: you will probably not ' +
                                'be able to control the media')
            self.logger.exception(e)

        self._post_event(MediaPlayEvent, resource=resource)
        self._init_player_handlers()
        if not self._play_started.wait(timeout=self.timeout):
            self.logger.warning(f'The player has not sent a play started event within {self.timeout}')
        return self.status()

    @action
    def pause(self):
        """ Pause the playback """
        if self._player:
            self._player.play_pause()
        return self.status()

    @action
    def stop(self):
        """ Stop the playback (same as quit) """
        return self.quit()

    @action
    def quit(self):
        """ Quit the player """
        from omxplayer.player import OMXPlayerDeadError

        if self._player:
            try:
                try:
                    self._player.stop()
                except Exception as e:
                    self.logger.warning(f'Could not stop player: {str(e)}')

                self._player.quit()
            except OMXPlayerDeadError:
                pass
            finally:
                self._player = None

        return {'status': 'stop'}

    def get_volume(self) -> float:
        """
        :return: The player volume in percentage [0, 100].
        """
        if self._player:
            return self._player.volume()*100

    @action
    def voldown(self, step=10.0):
        """
        Decrease the volume.

        :param step: Volume decrease step between 0 and 100 (default: 10%).
        :type step: float
        """
        if self._player:
            self.set_volume(max(0, self.get_volume()-step))
        return self.status()

    @action
    def volup(self, step=10.0):
        """
        Increase the volume.

        :param step: Volume increase step between 0 and 100 (default: 10%).
        :type step: float
        """
        if self._player:
            self.set_volume(min(100, self.get_volume()+step))
        return self.status()

    @action
    def back(self, offset=30):
        """ Back by (default: 30) seconds """
        if self._player:
            self._player.seek(-offset)
        return self.status()

    @action
    def forward(self, offset=30):
        """ Forward by (default: 30) seconds """
        if self._player:
            self._player.seek(offset)
        return self.status()

    @action
    def next(self):
        """ Play the next track/video """
        if self._player:
            self._player.stop()

        if self._videos_queue:
            video = self._videos_queue.pop(0)
            self.play(video)

        return self.status()

    @action
    def hide_subtitles(self):
        """ Hide the subtitles """
        if self._player:
            self._player.hide_subtitles()
        return self.status()

    @action
    def hide_video(self):
        """ Hide the video """
        if self._player:
            self._player.hide_video()
        return self.status()

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """

        return self._player.is_playing()

    @action
    def load(self, resource, pause=False, **kwargs):
        """
        Load a resource/video in the player.

        :param resource: URL or filename to load
        :type resource: str

        :param pause: If set, load the video in paused mode (default: False)
        :type pause: bool
        """

        if self._player:
            self._player.load(resource, pause=pause)
        return self.status()

    @action
    def metadata(self):
        """ Get the metadata of the current video """
        if self._player:
            return self._player.metadata()
        return self.status()

    @action
    def mute(self):
        """ Mute the player """
        if self._player:
            self._player.mute()
        return self.status()

    @action
    def unmute(self):
        """ Unmute the player """
        if self._player:
            self._player.unmute()
        return self.status()

    @action
    def seek(self, position):
        """
        Seek to the specified number of seconds from the start.

        :param position: Number of seconds from the start
        :type position: float
        """
        if self._player:
            self._player.set_position(position)
        return self.status()

    @action
    def set_position(self, position):
        """
        Seek to the specified number of seconds from the start (same as :meth:`.seek`).

        :param position: Number of seconds from the start
        :type position: float
        """
        return self.seek(position)


    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: float
        """

        if self._player:
            self._player.set_volume(volume/100)
        return self.status()

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Format::

            output = {
                "duration": Duration in seconds,
                "filename": Media filename,
                "fullscreen": true or false,
                "mute": true or false,
                "path": Media path
                "pause": true or false,
                "position": Position in seconds
                "seekable": true or false
                "state": play, pause or stop
                "title": Media title
                "url": Media url
                "volume": Volume between 0 and 100
                "volume_max": 100,
            }
        """

        from omxplayer.player import OMXPlayerDeadError
        from dbus import DBusException

        if not self._player:
            return {
                'state': PlayerState.STOP.value
            }

        try:
            state = self._player.playback_status().lower()
        except (OMXPlayerDeadError, DBusException) as e:
            self.logger.warning(f'Could not retrieve player status: {e}')
            if isinstance(e, OMXPlayerDeadError):
                self._player = None

            return {
                'state': PlayerState.STOP.value
            }

        if state == 'playing':
            state = PlayerState.PLAY.value
        elif state == 'stopped':
            state = PlayerState.STOP.value
        elif state == 'paused':
            state = PlayerState.PAUSE.value

        return {
            'duration': self._player.duration(),
            'filename': urllib.parse.unquote(self._player.get_source()).split('/')[-1] if self._player.get_source().startswith('file://') else None,
            'fullscreen': self._player.fullscreen(),
            'mute': self._player._is_muted,
            'path': self._player.get_source(),
            'pause': state == PlayerState.PAUSE.value,
            'position': max(0, self._player.position()),
            'seekable': self._player.can_seek(),
            'state': state,
            'title': urllib.parse.unquote(self._player.get_source()).split('/')[-1] if self._player.get_source().startswith('file://') else None,
            'url': self._player.get_source(),
            'volume': self.get_volume(),
            'volume_max': 100,
        }

    def add_handler(self, event_type, callback):
        if event_type not in self._handlers.keys():
            raise AttributeError('{} is not a valid PlayerEvent type'.
                                 format(event_type))

        self._handlers[event_type].append(callback)

    @staticmethod
    def _post_event(evt_type, **evt):
        bus = get_bus()
        bus.post(evt_type(player='local', plugin='media.omxplayer', **evt))

    def on_play(self):
        def _f(player):
            if self.volume and not self._play_started.is_set():
                self.set_volume(self.volume)
            self._play_started.set()

            resource = player.get_source()
            self._post_event(MediaPlayEvent, resource=resource)
            for callback in self._handlers[PlayerEvent.PLAY.value]:
                callback(resource)

        return _f

    def on_pause(self):
        def _f(player):
            resource = player.get_source()
            self._post_event(MediaPauseEvent, resource=resource)
            for callback in self._handlers[PlayerEvent.PAUSE.value]:
                callback(resource)

        return _f

    def on_stop(self):
        def _f(*_, **__):
            self._post_event(MediaStopEvent)
            for callback in self._handlers[PlayerEvent.STOP.value]:
                callback()
        return _f

    def on_seek(self):
        def _f(player, *_, **__):
            self._post_event(MediaSeekEvent, position=player.position())
        return _f

    def _init_player_handlers(self):
        if not self._player:
            return

        self._player.playEvent += self.on_play()
        self._player.pauseEvent += self.on_pause()
        self._player.stopEvent += self.on_stop()
        self._player.exitEvent += self.on_stop()
        self._player.positionEvent += self.on_seek()
        self._player.seekEvent += self.on_seek()

    def toggle_subtitles(self, *args, **kwargs):
        raise NotImplementedError

    def set_subtitles(self, filename, *args, **kwargs):
        raise NotImplementedError

    def remove_subtitles(self, *args, **kwargs):
        raise NotImplementedError


# vim:sw=4:ts=4:et:
