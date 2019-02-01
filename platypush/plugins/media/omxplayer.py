import os
import re
import subprocess

import urllib.request
import urllib.parse

from platypush.context import get_backend, get_plugin
from platypush.plugins.media import MediaPlugin, PlayerState
from platypush.message.event.video import VideoPlayEvent, VideoPauseEvent, \
    VideoStopEvent, NewPlayingVideoEvent

from platypush.plugins import action


class MediaOmxplayerPlugin(MediaPlugin):
    """
    Plugin to control video and media playback using OMXPlayer.

    Requires:

        * **omxplayer** installed on your system (see your distro instructions)
        * **omxplayer-wrapper** (``pip install omxplayer-wrapper``)
    """

    def __init__(self, args=[], *argv, **kwargs):
        """
        :param args: Arguments that will be passed to the OMXPlayer constructor
            (e.g. subtitles, volume, start position, window size etc.) see
            https://github.com/popcornmix/omxplayer#synopsis and
            http://python-omxplayer-wrapper.readthedocs.io/en/latest/omxplayer/#omxplayer.player.OMXPlayer
        :type args: list
        """

        super().__init__(*argv, **kwargs)

        self.args = args
        self._player = None

    @action
    def play(self, resource):
        """
        Play a resource.

        :param resource: Resource to play. Supported types:

            * Local files (format: ``file://<path>/<file>``)
            * Remote videos (format: ``https://<url>/<resource>``)
            * YouTube videos (format: ``https://www.youtube.com/watch?v=<id>``)
            * Torrents (format: Magnet links, Torrent URLs or local Torrent files)
        """

        resource = self._get_resource(resource)
        if self._player:
            try:
                self._player.stop()
                self._player = None
            except Exception as e:
                self.logger.exception(e)
                self.logger.warning('Unable to stop a previously running instance ' +
                                'of OMXPlayer, trying to play anyway')

        try:
            from omxplayer import OMXPlayer
            self._player = OMXPlayer(resource, args=self.args)
            self._init_player_handlers()
        except DBusException as e:
            self.logger.warning('DBus connection failed: you will probably not ' +
                            'be able to control the media')
            self.logger.exception(e)

        return self.status()

    @action
    def pause(self):
        """ Pause the playback """
        if self._player: self._player.play_pause()

    @action
    def stop(self):
        """ Stop the playback """
        if self._player:
            self._player.stop()
            self._player.quit()
            self._player = None

        return {'status':'stop'}

    @action
    def voldown(self):
        """ Volume down by 10% """
        if self._player:
            self._player.set_volume(max(-6000, self._player.volume()-1000))
        return self.status()

    @action
    def volup(self):
        """ Volume up by 10% """
        if self._player:
            self._player.set_volume(min(0, self._player.volume()+1000))
        return self.status()

    @action
    def back(self, offset=60):
        """ Back by (default: 60) seconds """
        if self._player:
            self._player.seek(-offset)
        return self.status()

    @action
    def forward(self, offset=60):
        """ Forward by (default: 60) seconds """
        if self._player:
            self._player.seek(+offset)
        return self.status()

    @action
    def next(self):
        """ Play the next track/video """
        if self._player:
            self._player.stop()

        if self.videos_queue:
            video = self.videos_queue.pop(0)
            return self.play(video)

    @action
    def hide_subtitles(self):
        """ Hide the subtitles """
        if self._player: self._player.hide_subtitles()
        return self.status()

    @action
    def hide_video(self):
        """ Hide the video """
        if self._player: self._player.hide_video()
        return self.status()

    @action
    def is_playing(self):
        """
        :returns: True if it's playing, False otherwise
        """

        if self._player: return self._player.is_playing()
        else: return False

    @action
    def load(self, resource, pause=False):
        """
        Load a resource/video in the player.

        :param pause: If set, load the video in paused mode (default: False)
        :type pause: bool
        """

        if self._player: self._player.load(resource, pause)
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
        if self._player: self._player.mute()
        return self.status()

    @action
    def unmute(self):
        """ Unmute the player """
        if self._player: self._player.unmute()
        return self.status()

    @action
    def seek(self, relative_position):
        """
        Seek backward/forward by the specified number of seconds

        :param relative_position: Number of seconds relative to the current cursor
        :type relative_position: int
        """

        if self._player: self._player.seek(relative_position)
        return self.status()

    @action
    def set_position(self, position):
        """
        Seek backward/forward to the specified absolute position

        :param position: Number of seconds from the start
        :type position: int
        """

        if self._player: self._player.set_seek(position)
        return self.status()

    @action
    def set_volume(self, volume):
        """
        Set the volume

        :param volume: Volume value between 0 and 100
        :type volume: int
        """

        # Transform a [0,100] value to an OMXPlayer volume in [-6000,0]
        volume = 60.0*volume - 6000
        if self._player: self._player.set_volume(volume)
        return self.status()

    @action
    def status(self):
        """
        Get the current player state.

        :returns: A dictionary containing the current state.

        Example::

            output = {
                "source": "https://www.youtube.com/watch?v=7L9KkZoNZkA",
                "state": "play",
                "volume": 80,
                "elapsed": 123,
                "duration": 300,
                "width": 800,
                "height": 600
            }
        """

        state = PlayerState.STOP.value

        if self._player:
            state = self._player.playback_status().lower()
            if state == 'playing': state = PlayerState.PLAY.value
            elif state == 'stopped': state = PlayerState.STOP.value
            elif state == 'paused': state = PlayerState.PAUSE.value

            return {
                'source': self._player.get_source(),
                'state': state,
                'volume': self._player.volume(),
                'elapsed': self._player.position(),
                'duration': self._player.duration(),
                'width': self._player.width(),
                'height': self._player.height(),
            }
        else:
            return {
                'state': PlayerState.STOP.value
            }

    @action
    def send_message(self, msg):
        try:
            redis = get_backend('redis')
            if not redis:
                raise KeyError()
        except KeyError:
            self.logger.warning("Backend {} does not implement send_message " +
                                "and the fallback Redis backend isn't configured")
            return

        redis.send_message(msg)

    def on_play(self):
        def _f(player):
            self.send_message(VideoPlayEvent(video=self._player.get_source()))
        return _f

    def on_pause(self):
        def _f(player):
            self.send_message(VideoPauseEvent(video=self._player.get_source()))
        return _f

    def on_stop(self):
        def _f(player):
            self.send_message(VideoStopEvent())
        return _f


    def _init_player_handlers(self):
        if not self._player:
            return

        self._player.playEvent += self.on_play()
        self._player.pauseEvent += self.on_pause()
        self._player.stopEvent += self.on_stop()


# vim:sw=4:ts=4:et:
