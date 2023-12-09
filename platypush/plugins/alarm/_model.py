import datetime
import enum
import os
import time
import threading
from typing import Callable, Optional, Union

import croniter
from dateutil.tz import gettz

from platypush.context import get_bus, get_plugin
from platypush.entities.alarm import Alarm as AlarmDb
from platypush.message.request import Request
from platypush.message.event.alarm import (
    AlarmDisabledEvent,
    AlarmDismissedEvent,
    AlarmEnabledEvent,
    AlarmSnoozedEvent,
    AlarmStartedEvent,
)
from platypush.plugins.media import MediaPlugin, PlayerState
from platypush.procedure import Procedure


class AlarmState(enum.IntEnum):
    """
    Alarm states.
    """

    WAITING = 1
    RUNNING = 2
    DISMISSED = 3
    SNOOZED = 4
    SHUTDOWN = 5
    UNKNOWN = -1


class Alarm:
    """
    Alarm model and controller.
    """

    _alarms_count = 0
    _id_lock = threading.RLock()

    def __init__(
        self,
        when: Union[str, int, float],
        actions: Optional[list] = None,
        name: Optional[str] = None,
        media: Optional[str] = None,
        media_plugin: Optional[str] = None,
        audio_volume: Optional[Union[int, float]] = None,
        snooze_interval: float = 300,
        poll_interval: float = 5,
        enabled: bool = True,
        static: bool = False,
        stop_event: Optional[threading.Event] = None,
        on_change: Optional[Callable[['Alarm'], None]] = None,
        **_,
    ):
        with self._id_lock:
            self._alarms_count += 1
            self.id = self._alarms_count

        self.when = when
        self.name = name or f'Alarm_{self.id}'
        self.media = self._get_media_resource(media)
        self.media_plugin = media_plugin
        self.audio_volume = audio_volume
        self.snooze_interval = snooze_interval
        self.state = AlarmState.UNKNOWN
        self.timer: Optional[threading.Timer] = None
        self.static = static
        self.actions = Procedure.build(
            name=name, _async=False, requests=actions or [], id=self.id
        )

        self._enabled = enabled
        self._runtime_snooze_interval = snooze_interval
        self.stop_event = stop_event or threading.Event()
        self.poll_interval = poll_interval
        self.on_change = on_change

    def _on_change(self):
        if self.on_change:
            self.on_change(self)

    @staticmethod
    def _get_media_resource(media: Optional[str]) -> Optional[str]:
        if not media:
            return None

        if media.startswith('file://'):
            media = media[len('file://') :]

        media_path = os.path.abspath(os.path.expanduser(media))
        if os.path.isfile(media_path):
            media = media_path

        return media

    def get_next(self) -> Optional[float]:
        now = time.time()
        t = 0

        try:
            # If when is a number, interpret it as number of seconds into the future
            delta = float(self.when)
            t = now + delta
            self.when = datetime.datetime.fromtimestamp(t).isoformat()
        except (TypeError, ValueError):
            assert isinstance(self.when, str), f'Invalid alarm time {self.when}'

            try:
                # If when is a cron expression, get the next run time
                t = croniter.croniter(
                    self.when,
                    datetime.datetime.fromtimestamp(now).replace(tzinfo=gettz()),
                ).get_next()
            except (AttributeError, croniter.CroniterBadCronError):
                try:
                    # If when is an ISO-8601 timestamp, parse it
                    t = datetime.datetime.fromisoformat(self.when).timestamp()
                except Exception as e:
                    raise AssertionError(f'Invalid alarm time {self.when}: {e}') from e

        return t if t >= now else None

    def is_enabled(self):
        return self._enabled

    def is_shut_down(self):
        return self.state in {
            AlarmState.SHUTDOWN,
            AlarmState.DISMISSED,
            AlarmState.UNKNOWN,
        }

    def is_expired(self):
        return (self.get_next() or 0) < time.time()

    def disable(self):
        self.set_enabled(False)

    def enable(self):
        self.set_enabled(True)

    def set_enabled(self, enabled: bool):
        if enabled == self._enabled:
            return

        self._enabled = enabled
        evt_type = AlarmEnabledEvent if enabled else AlarmDisabledEvent
        get_bus().post(evt_type(name=self.name))
        self._on_change()

    def dismiss(self):
        self.state = AlarmState.DISMISSED
        self.stop_audio()
        get_bus().post(AlarmDismissedEvent(name=self.name))
        self._on_change()

    def snooze(self, interval: Optional[float] = None):
        self._runtime_snooze_interval = interval or self.snooze_interval
        self.state = AlarmState.SNOOZED
        self.stop_audio()
        get_bus().post(
            AlarmSnoozedEvent(name=self.name, interval=self._runtime_snooze_interval)
        )
        self._on_change()

    def start(self):
        if self.timer:
            self.timer.cancel()

        next_run = self.get_next()
        if next_run is None:
            return

        interval = next_run - time.time()
        self.timer = threading.Timer(interval, self.alarm_callback)
        self.timer.start()
        self.state = AlarmState.WAITING
        self._on_change()

    def stop(self):
        self.state = AlarmState.SHUTDOWN
        if self.timer:
            self.timer.cancel()
            self.timer = None

        self._on_change()

    def _get_media_plugin(self) -> MediaPlugin:
        plugin = get_plugin(self.media_plugin)
        assert plugin and isinstance(plugin, MediaPlugin), (
            f'Invalid audio plugin {self.media_plugin}'
            if plugin
            else f'Missing audio plugin {self.media_plugin}'
        )

        return plugin

    def play_audio(self):
        def thread():
            self._get_media_plugin().play(self.media)
            if self.audio_volume is not None:
                self._get_media_plugin().set_volume(self.audio_volume)

        audio_thread = threading.Thread(target=thread)
        audio_thread.start()

    def stop_audio(self):
        self._get_media_plugin().stop()

    def alarm_callback(self):
        while not self.should_stop():
            if self.is_enabled():
                self.state = AlarmState.RUNNING
                get_bus().post(AlarmStartedEvent(name=self.name))
                self._on_change()
                if self.media_plugin and self.media:
                    self.play_audio()

                self.actions.execute()

            self.wait_stop(self.poll_interval)
            sleep_time = None
            if self.state == AlarmState.RUNNING:
                while not self.should_stop():
                    plugin_status = self._get_media_plugin().status().output
                    if not isinstance(plugin_status, dict):
                        self.wait_stop(self.poll_interval)
                        continue

                    state = plugin_status.get('state')
                    if state == PlayerState.STOP.value:
                        if self.state == AlarmState.SNOOZED:
                            sleep_time = self._runtime_snooze_interval
                        else:
                            self.state = AlarmState.WAITING
                            self._on_change()

                        break

                    self.wait_stop(self.poll_interval)

            if self.state == AlarmState.SNOOZED:
                sleep_time = self._runtime_snooze_interval
            elif self.get_next() is None:
                self.state = AlarmState.SHUTDOWN
                break

            if not sleep_time:
                next_run = self.get_next()
                sleep_time = (
                    next_run - time.time()
                    if next_run is not None
                    else self.poll_interval
                )

            self.stop_event.wait(sleep_time)

    def wait_stop(self, timeout: Optional[float] = None):
        self.stop_event.wait(timeout)

    def should_stop(self):
        return self.stop_event.is_set() or (self.is_expired() and self.is_shut_down())

    def to_dict(self) -> dict:
        return {
            'id': self.name,
            'name': self.name,
            'when': self.when,
            'next_run': self.get_next(),
            'enabled': self.is_enabled(),
            'state': self.state.name,
            'media': self.media,
            'media_plugin': self.media_plugin,
            'audio_volume': self.audio_volume,
            'snooze_interval': self.snooze_interval,
            'actions': self.actions.requests,
            'static': self.static,
        }

    @classmethod
    def from_db(cls, alarm: AlarmDb, **kwargs) -> 'Alarm':
        return cls(
            when=str(alarm.when),
            name=str(alarm.name),
            media=alarm.media,  # type: ignore
            media_plugin=kwargs.pop('media_plugin', alarm.media_plugin),  # type: ignore
            audio_volume=alarm.audio_volume,  # type: ignore
            actions=alarm.actions,  # type: ignore
            snooze_interval=alarm.snooze_interval,  # type: ignore
            enabled=bool(alarm.enabled),
            static=bool(alarm.static),
            state=getattr(AlarmState, str(alarm.state)),
            **kwargs,
        )

    def to_db(self) -> AlarmDb:
        return AlarmDb(
            id=self.name,
            name=self.name,
            when=self.when,
            state=self.state.name,
            next_run=self.get_next(),
            media=self.media,
            media_plugin=self.media_plugin,
            audio_volume=self.audio_volume,
            actions=[
                Request.to_dict(req) if isinstance(req, Request) else req
                for req in self.actions.requests
            ],
            snooze_interval=self.snooze_interval,
            enabled=self.is_enabled(),
            static=self.static,
        )


# vim:sw=4:ts=4:et:
