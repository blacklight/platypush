import re
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.music import MusicPlayEvent, MusicPauseEvent, \
    MusicStopEvent, NewPlayingTrackEvent, PlaylistChangeEvent, VolumeChangeEvent, \
    PlaybackConsumeModeChangeEvent, PlaybackSingleModeChangeEvent, \
    PlaybackRepeatModeChangeEvent, PlaybackRandomModeChangeEvent


class MusicMpdBackend(Backend):
    """
    This backend listens for events on a MPD/Mopidy music server.

    Triggers:

        * :class:`platypush.message.event.music.MusicPlayEvent` if the playback state changed to play
        * :class:`platypush.message.event.music.MusicPauseEvent` if the playback state changed to pause
        * :class:`platypush.message.event.music.MusicStopEvent` if the playback state changed to stop
        * :class:`platypush.message.event.music.NewPlayingTrackEvent` if a new track is being played
        * :class:`platypush.message.event.music.PlaylistChangeEvent` if the main playlist has changed
        * :class:`platypush.message.event.music.VolumeChangeEvent` if the main volume has changed

    Requires:
        * **python-mpd2** (``pip install python-mpd2``)
        * The :mod:`platypush.plugins.music.mpd` plugin to be configured
    """

    def __init__(self, server='localhost', port=6600, poll_seconds=3, **kwargs):
        """
        :param poll_seconds: Interval between queries to the server (default: 3 seconds)
        :type poll_seconds: float
        """

        super().__init__(**kwargs)

        self.server = server
        self.port = port
        self.poll_seconds = poll_seconds


    def run(self):
        super().run()

        last_status = {}
        last_state = None
        last_track = None
        last_playlist = None
        plugin = None

        while not self.should_stop():
            success = False

            while not success:
                state = None
                playlist = None
                track = None

                try:
                    plugin = get_plugin('music.mpd')
                    if not plugin:
                        raise StopIteration

                    status = plugin.status().output
                    if not status or status.get('state') is None:
                        raise StopIteration

                    track = plugin.currentsong().output
                    state = status['state'].lower()
                    playlist = status['playlist']
                    success = True
                except Exception as e:
                    self.logger.debug(e)
                    get_plugin('music.mpd', reload=True)
                    if not state: state = last_state
                    if not playlist: playlist = last_playlist
                    if not track: track = last_track
                finally:
                    time.sleep(self.poll_seconds)

            if state != last_state:
                if state == 'stop':
                    self.bus.post(MusicStopEvent(status=status, track=track))
                elif state == 'pause':
                    self.bus.post(MusicPauseEvent(status=status, track=track))
                elif state == 'play':
                    self.bus.post(MusicPlayEvent(status=status, track=track))

            if playlist != last_playlist:
                if last_playlist:
                    # XXX plchanges can become heavy with big playlists,
                    # PlaylistChangeEvent temporarily disabled
                    # changes = plugin.plchanges(last_playlist).output
                    # self.bus.post(PlaylistChangeEvent(changes=changes))
                    self.bus.post(PlaylistChangeEvent())
                last_playlist = playlist

            if state == 'play' and track != last_track:
                self.bus.post(NewPlayingTrackEvent(status=status, track=track))

            if last_status.get('volume', None) != status['volume']:
                self.bus.post(VolumeChangeEvent(
                    volume=int(status['volume']), status=status, track=track))

            if last_status.get('random', None) != status['random']:
                self.bus.post(PlaybackRandomModeChangeEvent(
                    state=bool(int(status['random'])), status=status, track=track))

            if last_status.get('repeat', None) != status['repeat']:
                self.bus.post(PlaybackRepeatModeChangeEvent(
                    state=bool(int(status['repeat'])), status=status, track=track))

            if last_status.get('consume', None) != status['consume']:
                self.bus.post(PlaybackConsumeModeChangeEvent(
                    state=bool(int(status['consume'])), status=status, track=track))

            if last_status.get('single', None) != status['single']:
                self.bus.post(PlaybackSingleModeChangeEvent(
                    state=bool(int(status['single'])), status=status, track=track))

            last_status = status
            last_state = state
            last_track = track
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

