import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.music import (
    MusicPlayEvent,
    MusicPauseEvent,
    MusicStopEvent,
    NewPlayingTrackEvent,
    PlaylistChangeEvent,
    VolumeChangeEvent,
    PlaybackConsumeModeChangeEvent,
    PlaybackSingleModeChangeEvent,
    PlaybackRepeatModeChangeEvent,
    PlaybackRandomModeChangeEvent,
)


class MusicMpdBackend(Backend):
    """
    This backend listens for events on a MPD/Mopidy music server.

    Requires:

        * :class:`platypush.plugins.music.mpd.MusicMpdPlugin` configured

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

        while not self.should_stop():
            success = False
            state = None
            status = None
            playlist = None
            track = None

            while not success:
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
                    if not state:
                        state = last_state
                    if not playlist:
                        playlist = last_playlist
                    if not track:
                        track = last_track
                finally:
                    time.sleep(self.poll_seconds)

            if state != last_state:
                if state == 'stop':
                    self.bus.post(
                        MusicStopEvent(
                            status=status, track=track, plugin_name='music.mpd'
                        )
                    )
                elif state == 'pause':
                    self.bus.post(
                        MusicPauseEvent(
                            status=status, track=track, plugin_name='music.mpd'
                        )
                    )
                elif state == 'play':
                    self.bus.post(
                        MusicPlayEvent(
                            status=status, track=track, plugin_name='music.mpd'
                        )
                    )

            if playlist != last_playlist:
                if last_playlist:
                    # XXX plchanges can become heavy with big playlists,
                    # PlaylistChangeEvent temporarily disabled
                    # changes = plugin.plchanges(last_playlist).output
                    # self.bus.post(PlaylistChangeEvent(changes=changes))
                    self.bus.post(PlaylistChangeEvent(plugin_name='music.mpd'))
                last_playlist = playlist

            if state == 'play' and track != last_track:
                self.bus.post(
                    NewPlayingTrackEvent(
                        status=status, track=track, plugin_name='music.mpd'
                    )
                )

            if last_status.get('volume') != status['volume']:
                self.bus.post(
                    VolumeChangeEvent(
                        volume=int(status['volume']),
                        status=status,
                        track=track,
                        plugin_name='music.mpd',
                    )
                )

            if last_status.get('random') != status['random']:
                self.bus.post(
                    PlaybackRandomModeChangeEvent(
                        state=bool(int(status['random'])),
                        status=status,
                        track=track,
                        plugin_name='music.mpd',
                    )
                )

            if last_status.get('repeat') != status['repeat']:
                self.bus.post(
                    PlaybackRepeatModeChangeEvent(
                        state=bool(int(status['repeat'])),
                        status=status,
                        track=track,
                        plugin_name='music.mpd',
                    )
                )

            if last_status.get('consume') != status['consume']:
                self.bus.post(
                    PlaybackConsumeModeChangeEvent(
                        state=bool(int(status['consume'])),
                        status=status,
                        track=track,
                        plugin_name='music.mpd',
                    )
                )

            if last_status.get('single') != status['single']:
                self.bus.post(
                    PlaybackSingleModeChangeEvent(
                        state=bool(int(status['single'])),
                        status=status,
                        track=track,
                        plugin_name='music.mpd',
                    )
                )

            last_status = status
            last_state = state
            last_track = track
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
