import json
import logging
import re
import time
from dataclasses import asdict
from queue import Empty
from threading import Event, RLock, Thread
from typing import Dict, Generator, List, Optional, Type

import websocket

from platypush.context import get_bus
from platypush.message.event.music import (
    MusicEvent,
    MusicPauseEvent,
    MusicPlayEvent,
    MusicStopEvent,
    MuteChangeEvent,
    NewPlayingTrackEvent,
    PlaybackConsumeModeChangeEvent,
    PlaybackRandomModeChangeEvent,
    PlaybackRepeatModeChangeEvent,
    PlaybackSingleModeChangeEvent,
    PlaylistChangeEvent,
    SeekChangeEvent,
    VolumeChangeEvent,
)
from platypush.plugins.media import PlayerState

from ._common import DEFAULT_TIMEOUT
from ._conf import MopidyConfig
from ._status import MopidyStatus
from ._sync import PlaylistSync
from ._task import MopidyTask
from ._track import MopidyTrack


class MopidyClient(Thread):
    """
    Thread that listens for Mopidy events and posts them to the bus.
    """

    def __init__(
        self,
        config: MopidyConfig,
        status: MopidyStatus,
        stop_event: Event,
        playlist_sync: PlaylistSync,
        tasks: Dict[int, MopidyTask],
        **_,
    ):
        super().__init__(name='platypush:mopidy:listener')

        self.logger = logging.getLogger('platypush:mopidy:listener')
        self.config = config
        self._status = status
        self._stop_event = stop_event
        self._playlist_sync = playlist_sync
        self._tasks = tasks
        self._refresh_in_progress = Event()
        self._refresh_lock = RLock()
        self._req_lock = RLock()
        self._close_lock = RLock()
        self._tracks: List[MopidyTrack] = []
        self._msg_id = 0
        self._ws = None
        self.connected_event = Event()
        self.closed_event = Event()

    @property
    def _bus(self):
        return get_bus()

    @property
    def status(self):
        return self._status

    @property
    def tracks(self):
        return self._tracks

    def should_stop(self):
        return self._stop_event.is_set()

    def wait_stop(self, timeout: Optional[float] = None):
        self._stop_event.wait(timeout=timeout)

    def make_task(self, method: str, **args: dict) -> MopidyTask:
        with self._req_lock:
            self._msg_id += 1
            task = MopidyTask(
                id=self._msg_id,
                method=method,
                args=args or {},
            )

        self._tasks[task.id] = task
        return task

    def send(self, *tasks: MopidyTask):
        """
        Send a list of tasks to the Mopidy server.
        """
        assert self._ws, 'Websocket not connected'

        for task in tasks:
            with self._req_lock:
                task.send(self._ws)

    def gather(
        self,
        *tasks: MopidyTask,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
    ) -> Generator:
        t_start = time.time()

        for task in tasks:
            remaining_timeout = (
                max(0, timeout - (time.time() - t_start)) if timeout else None
            )

            if not self._tasks.get(task.id):
                yield None

            try:
                ret = self._tasks[task.id].get_response(timeout=remaining_timeout)
                assert not isinstance(ret, Exception), ret
                self.logger.debug('Got response for %s: %s', task, ret)
                yield ret
            except Empty as e:
                t = self._tasks.get(task.id)
                err = 'Mopidy request timeout'
                if t:
                    err += f' - method: {t.method} args: {t.args}'

                raise TimeoutError(err) from e
            finally:
                self._tasks.pop(task.id, None)

    def exec(self, *msgs: dict, timeout: Optional[float] = DEFAULT_TIMEOUT) -> list:
        tasks = [self.make_task(**msg) for msg in msgs]
        for task in tasks:
            self.send(task)

        return list(self.gather(*tasks, timeout=timeout))

    def refresh_status(  # pylint: disable=too-many-branches
        self, timeout: Optional[float] = DEFAULT_TIMEOUT, with_tracks: bool = False
    ):
        if self._refresh_in_progress.is_set():
            return

        # Unless we are also retrieving the tracks, we don't need a high timeout here.
        # A high timeout may result in event lagging if some of the responses aren't received.
        # In this case, better to timeout early and retry.
        if not with_tracks:
            timeout = 5

        events = []

        try:
            with self._refresh_lock:
                self._refresh_in_progress.set()
                # Refresh the tracklist attributes
                opts = ('repeat', 'random', 'single', 'consume')
                ret = self.exec(
                    *[
                        *[{'method': f'core.tracklist.get_{opt}'} for opt in opts],
                        {'method': 'core.playback.get_current_tl_track'},
                        {'method': 'core.playback.get_state'},
                        {'method': 'core.mixer.get_volume'},
                        {'method': 'core.playback.get_time_position'},
                        *(
                            [{'method': 'core.tracklist.get_tl_tracks'}]
                            if with_tracks
                            else []
                        ),
                    ],
                    timeout=timeout,
                )

                for i, opt in enumerate(opts):
                    new_value = ret[i]
                    if opt == 'random' and self._status.random != new_value:
                        events.append(
                            (PlaybackRandomModeChangeEvent, {'state': new_value})
                        )
                    if opt == 'repeat' and self._status.repeat != new_value:
                        events.append(
                            (PlaybackRepeatModeChangeEvent, {'state': new_value})
                        )
                    if opt == 'single' and self._status.single != new_value:
                        events.append(
                            (PlaybackSingleModeChangeEvent, {'state': new_value})
                        )
                    if opt == 'consume' and self._status.consume != new_value:
                        events.append(
                            (PlaybackConsumeModeChangeEvent, {'state': new_value})
                        )

                    setattr(self._status, opt, new_value)

                # Get remaining info
                track = MopidyTrack.parse(ret[4])
                state, volume, t = ret[5:8]

                if track:
                    idx = self.exec(
                        {
                            'method': 'core.tracklist.index',
                            'tlid': track.track_id,
                        },
                        timeout=timeout,
                    )[0]

                    self._status.track = track
                    self._status.duration = track.time
                    if idx is not None:
                        self._status.playing_pos = self._status.track.playlist_pos = idx

                    if track != self._status.track and state != 'stopped':
                        events.append((NewPlayingTrackEvent, {}))

                if state != self._status.state:
                    if state == 'paused':
                        self._status.state = PlayerState.PAUSE
                        events.append((MusicPauseEvent, {}))
                    elif state == 'playing':
                        self._status.state = PlayerState.PLAY
                        events.append((MusicPlayEvent, {}))
                    elif state == 'stopped':
                        self._status.state = PlayerState.STOP
                        events.append((MusicStopEvent, {}))

                if volume != self._status.volume:
                    self._status.volume = volume
                    events.append((VolumeChangeEvent, {'volume': volume}))

                if t != self._status.time:
                    self._status.time = t / 1000
                    events.append((SeekChangeEvent, {'position': self._status.time}))

                if with_tracks:
                    self._tracks = [  # type: ignore
                        MopidyTrack.parse({**t, 'playlist_pos': i})
                        for i, t in enumerate(ret[8])
                    ]

            for evt in events:
                self._post_event(evt[0], **evt[1])
        finally:
            self._refresh_in_progress.clear()

    def _refresh_status(
        self, timeout: Optional[float] = DEFAULT_TIMEOUT, with_tracks: bool = False
    ):
        """
        Refresh the status from the Mopidy server.

        It runs in a separate thread because the status refresh logic runs in
        synchronous mode, and it would block the main thread preventing the
        listener from receiving new messages.

        Also, an event+reenrant lock mechanism is used to ensure that only one
        refresh task is running at a time.
        """
        if self._refresh_in_progress.is_set():
            return

        with self._refresh_lock:
            Thread(
                target=self.refresh_status,
                kwargs={'timeout': timeout, 'with_tracks': with_tracks},
                daemon=True,
            ).start()

    def _post_event(self, evt_cls: Type[MusicEvent], **kwargs):
        self._bus.post(
            evt_cls(
                status=asdict(self._status),
                track=asdict(self._status.track) if self._status.track else None,
                plugin_name='music.mopidy',
                **kwargs,
            )
        )

    def _handle_error(self, msg: dict):
        msg_id = msg.get('id')
        err = msg.get('error')
        if not err:
            return

        err_data = err.get('data', {})
        tb = err_data.get('traceback')
        self.logger.warning(
            'Mopidy error: %s: %s: %s',
            err.get('message'),
            err_data.get('type'),
            err_data.get('message'),
        )
        if tb:
            self.logger.warning(tb)

        if msg_id:
            task = self._tasks.get(msg_id)
            if task:
                task.put_response(
                    RuntimeError(err.get('message') + ': ' + err_data.get('message'))
                )

    def on_pause(self, *_, **__):
        self._status.state = PlayerState.PAUSE
        self._post_event(MusicPauseEvent)

    def on_resume(self, *_, **__):
        self._status.state = PlayerState.PLAY
        self._post_event(MusicPlayEvent)

    def on_start(self, *_, **__):
        self._refresh_status()

    def on_end(self, *_, **__):
        self._refresh_status()

    def on_state_change(self, msg: dict, *_, **__):
        state = msg.get('new_state')
        if state == 'playing':
            self._status.state = PlayerState.PLAY
            self._post_event(MusicPlayEvent)
        elif state == 'paused':
            self._status.state = PlayerState.PAUSE
            self._post_event(MusicPauseEvent)
        elif state == 'stopped':
            self._status.state = PlayerState.STOP
            self._post_event(MusicStopEvent)

    def on_title_change(self, msg: dict, *_, track: MopidyTrack, **__):
        title = msg.get('title', '')
        m = re.match(r'^\s*(.+?)\s+-\s+(.*)\s*$', title)
        if not m:
            return

        track.artist = m.group(1)
        track.title = m.group(2)
        self._post_event(NewPlayingTrackEvent)

    def on_volume_change(self, msg: dict, *_, **__):
        volume = msg.get('volume')
        if volume is None or volume == self._status.volume:
            return

        self._status.volume = volume
        self._post_event(VolumeChangeEvent, volume=volume)

    def on_mute_change(self, msg: dict, *_, **__):
        mute = msg.get('mute')
        if mute is None or mute == self._status.mute:
            return

        self._status.mute = mute
        self._post_event(MuteChangeEvent, mute=mute)

    def on_seek(self, msg: dict, *_, **__):
        position = msg.get('time_position')
        if position is None:
            return

        t = position / 1000
        if t == self._status.time:
            return

        self._status.time = t
        self._post_event(SeekChangeEvent, position=self._status.time)

    def on_tracklist_change(self, *_, **__):
        should_proceed = self._playlist_sync.wait_for_loading(timeout=2)
        if not should_proceed:
            return

        self.logger.debug('Tracklist changed, refreshing changes')
        self._refresh_status(with_tracks=True)
        self._post_event(PlaylistChangeEvent)

    def on_options_change(self, *_, **__):
        self._refresh_status()

    def _on_msg(self, *args):
        msg = args[1] if len(args) > 1 else args[0]
        msg = json.loads(msg)
        msg_id = msg.get('id')
        event = msg.get('event')
        track: Optional[MopidyTrack] = None
        self.logger.debug('Received Mopidy message: %s', msg)

        if msg.get('error'):
            self._handle_error(msg)
            return

        if msg_id:
            task = self._tasks.get(msg_id)
            if task:
                task.put_response(msg)
                return

        if not event:
            return

        if msg.get('tl_track'):
            track = MopidyTrack.parse(msg['tl_track'])
            is_new_track = track and track != self._status.track
            self._status.track = track
            if is_new_track:
                self._post_event(NewPlayingTrackEvent)

        hndl = self._msg_handlers.get(event)
        if not hndl:
            return

        hndl(self, msg, track=track)

    def _on_error(self, *args):
        error = args[1] if len(args) > 1 else args[0]
        ws = args[0] if len(args) > 1 else None
        self.logger.warning('Mopidy websocket error: %s', error)
        if ws:
            ws.close()

    def _on_close(self, *_):
        self.connected_event.clear()
        self.closed_event.set()

        if self._ws:
            try:
                self._ws.close()
            except Exception as e:
                self.logger.debug(e, exc_info=True)
            finally:
                self._ws = None

        self.logger.warning('Mopidy websocket connection closed')

    def _on_open(self, *_):
        self.connected_event.set()
        self.closed_event.clear()
        self.logger.info('Mopidy websocket connected')
        self._refresh_status(with_tracks=True)

    def _connect(self):
        if not self._ws:
            self._ws = websocket.WebSocketApp(
                self.config.url,
                on_open=self._on_open,
                on_message=self._on_msg,
                on_error=self._on_error,
                on_close=self._on_close,
            )

            self._ws.run_forever()

    def run(self):
        while not self.should_stop():
            try:
                self._connect()
            except Exception as e:
                self.logger.warning(
                    'Error on websocket connection: %s', e, exc_info=True
                )
            finally:
                self.connected_event.clear()
                self.closed_event.set()
                self.wait_stop(10)

    def stop(self):
        with self._close_lock:
            if self._ws:
                self._ws.close()
                self._ws = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()

    _msg_handlers = {
        'track_playback_paused': on_pause,
        'playback_state_changed': on_state_change,
        'track_playback_resumed': on_resume,
        'track_playback_ended': on_end,
        'track_playback_started': on_start,
        'stream_title_changed': on_title_change,
        'volume_changed': on_volume_change,
        'mute_changed': on_mute_change,
        'seeked': on_seek,
        'tracklist_changed': on_tracklist_change,
        'options_changed': on_options_change,
    }


# vim:sw=4:ts=4:et:
