from dataclasses import dataclass, field
from threading import Thread
from typing import Optional

from platypush.context import get_bus
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
from platypush.plugins.music import MusicPlugin


@dataclass
class MpdStatus:
    """
    Data class for the MPD status.
    """

    state: Optional[str] = None
    playlist: Optional[int] = None
    volume: Optional[int] = None
    random: Optional[bool] = None
    repeat: Optional[bool] = None
    consume: Optional[bool] = None
    single: Optional[bool] = None
    track: dict = field(default_factory=dict)


class MpdListener(Thread):
    """
    Thread that listens/polls for MPD events and posts them to the bus.
    """

    def __init__(self, plugin: MusicPlugin, *_, **__):
        from . import MusicMpdPlugin

        super().__init__(name='platypush:mpd:listener')
        assert isinstance(plugin, MusicMpdPlugin)
        self.plugin: MusicMpdPlugin = plugin
        self._status = MpdStatus()

    @property
    def logger(self):
        return self.plugin.logger

    @property
    def bus(self):
        return get_bus()

    def wait_stop(self, timeout=None):
        self.plugin.wait_stop(timeout=timeout)

    def _process_events(self, status: dict, track: Optional[dict] = None):
        state = status.get('state', '').lower()
        evt_args = {'status': status, 'track': track, 'plugin_name': 'music.mpd'}

        if state != self._status.state:
            if state == 'stop':
                self.bus.post(MusicStopEvent(**evt_args))
            elif state == 'pause':
                self.bus.post(MusicPauseEvent(**evt_args))
            elif state == 'play':
                self.bus.post(MusicPlayEvent(**evt_args))

        if status.get('playlist') != self._status.playlist and self._status.playlist:
            # XXX plchanges can become heavy with big playlists,
            # PlaylistChangeEvent temporarily disabled
            # changes = plugin.plchanges(last_playlist).output
            # self.bus.post(PlaylistChangeEvent(changes=changes))
            self.bus.post(PlaylistChangeEvent(plugin_name='music.mpd'))

        if state == 'play' and track != self._status.track:
            self.bus.post(NewPlayingTrackEvent(**evt_args))

        if (
            status.get('volume') is not None
            and status.get('volume') != self._status.volume
        ):
            self.bus.post(VolumeChangeEvent(volume=int(status['volume']), **evt_args))

        if (
            status.get('random') is not None
            and status.get('random') != self._status.random
        ):
            self.bus.post(
                PlaybackRandomModeChangeEvent(
                    state=bool(int(status['random'])), **evt_args
                )
            )

        if (
            status.get('repeat') is not None
            and status.get('repeat') != self._status.repeat
        ):
            self.bus.post(
                PlaybackRepeatModeChangeEvent(
                    state=bool(int(status['repeat'])), **evt_args
                )
            )

        if (
            status.get('consume') is not None
            and status.get('consume') != self._status.consume
        ):
            self.bus.post(
                PlaybackConsumeModeChangeEvent(
                    state=bool(int(status['consume'])), **evt_args
                )
            )

        if (
            status.get('single') is not None
            and status.get('single') != self._status.single
        ):
            self.bus.post(
                PlaybackSingleModeChangeEvent(
                    state=bool(int(status['single'])), **evt_args
                )
            )

    def _update_status(self, status: dict, track: Optional[dict] = None):
        self._status = MpdStatus(
            state=status.get('state', '').lower(),
            playlist=status.get('playlist'),
            volume=status.get('volume'),
            random=status.get('random'),
            repeat=status.get('repeat'),
            consume=status.get('consume'),
            single=status.get('single'),
            track=track or {},
        )

    def run(self):
        super().run()

        while not self.plugin.should_stop():
            try:
                status = self.plugin._status()  # pylint: disable=protected-access
                assert status and status.get('state'), 'No status returned'
                if not (status and status.get('state')):
                    self.wait_stop(self.plugin.poll_interval)
                    break

                track = self.plugin._current_track()  # pylint: disable=protected-access
                self._process_events(status, track)
                self._update_status(status, track)
            except Exception as e:
                self.logger.warning(
                    'Could not retrieve the latest status: %s', e, exc_info=True
                )
            finally:
                self.wait_stop(self.plugin.poll_interval)


# vim:sw=4:ts=4:et:
