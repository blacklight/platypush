import datetime
import os
import time
import threading

from typing import Optional, Union, Dict, Any, List

import croniter
import enum

from platypush.backend import Backend
from platypush.context import get_bus, get_plugin
from platypush.message.event.alarm import AlarmStartedEvent, AlarmDismissedEvent, AlarmSnoozedEvent
from platypush.plugins.media import MediaPlugin, PlayerState
from platypush.procedure import Procedure


class AlarmState(enum.IntEnum):
    WAITING = 1
    RUNNING = 2
    DISMISSED = 3
    SNOOZED = 4
    SHUTDOWN = 5


class Alarm:
    _alarms_count = 0
    _id_lock = threading.RLock()

    def __init__(self, when: str, actions: Optional[list] = None, name: Optional[str] = None,
                 audio_file: Optional[str] = None, audio_plugin: Optional[str] = None,
                 audio_volume: Optional[Union[int, float]] = None,
                 snooze_interval: float = 300.0, enabled: bool = True):
        with self._id_lock:
            self._alarms_count += 1
            self.id = self._alarms_count

        self.when = when
        self.name = name or 'Alarm_{}'.format(self.id)
        self.audio_file = None

        if audio_file:
            self.audio_file = os.path.abspath(os.path.expanduser(audio_file))
            assert os.path.isfile(self.audio_file), 'No such audio file: {}'.format(self.audio_file)

        self.audio_plugin = audio_plugin
        self.audio_volume = audio_volume
        self.snooze_interval = snooze_interval
        self.state: Optional[AlarmState] = None
        self.timer: Optional[threading.Timer] = None
        self.actions = Procedure.build(name=name, _async=False, requests=actions or [], id=self.id)

        self._enabled = enabled
        self._runtime_snooze_interval = snooze_interval

    def get_next(self) -> float:
        now = time.time()

        try:
            cron = croniter.croniter(self.when, now)
            return cron.get_next()
        except (AttributeError, croniter.CroniterBadCronError):
            try:
                timestamp = datetime.datetime.fromisoformat(self.when).timestamp()
            except (TypeError, ValueError):
                timestamp = (datetime.datetime.now() + datetime.timedelta(seconds=int(self.when))).timestamp()

            return timestamp if timestamp >= now else None

    def is_enabled(self):
        return self._enabled

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    def dismiss(self):
        self.state = AlarmState.DISMISSED
        self.stop_audio()
        get_bus().post(AlarmDismissedEvent(name=self.name))

    def snooze(self, interval: Optional[float] = None):
        self._runtime_snooze_interval = interval or self.snooze_interval
        self.state = AlarmState.SNOOZED
        self.stop_audio()
        get_bus().post(AlarmSnoozedEvent(name=self.name, interval=self._runtime_snooze_interval))

    def start(self):
        if self.timer:
            self.timer.cancel()

        if self.get_next() is None:
            return

        interval = self.get_next() - time.time()
        self.timer = threading.Timer(interval, self.callback())
        self.timer.start()
        self.state = AlarmState.WAITING

    def stop(self):
        self.state = AlarmState.SHUTDOWN
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _get_audio_plugin(self) -> MediaPlugin:
        return get_plugin(self.audio_plugin)

    def play_audio(self):
        def thread():
            self._get_audio_plugin().play(self.audio_file)
            if self.audio_volume is not None:
                self._get_audio_plugin().set_volume(self.audio_volume)

        self.state = AlarmState.RUNNING
        audio_thread = threading.Thread(target=thread)
        audio_thread.start()

    def stop_audio(self):
        self._get_audio_plugin().stop()

    def callback(self):
        def _callback():
            while True:
                if self.state == AlarmState.SHUTDOWN:
                    break

                if self.is_enabled():
                    get_bus().post(AlarmStartedEvent(name=self.name))
                    if self.audio_plugin and self.audio_file:
                        self.play_audio()

                    self.actions.execute()

                time.sleep(10)
                sleep_time = None
                if self.state == AlarmState.RUNNING:
                    while True:
                        state = self._get_audio_plugin().status().output.get('state')
                        if state == PlayerState.STOP.value:
                            if self.state == AlarmState.SNOOZED:
                                sleep_time = self._runtime_snooze_interval
                            else:
                                self.state = AlarmState.WAITING

                            break
                        else:
                            time.sleep(10)

                if self.state == AlarmState.SNOOZED:
                    sleep_time = self._runtime_snooze_interval
                elif self.get_next() is None:
                    self.state = AlarmState.SHUTDOWN
                    break

                if not sleep_time:
                    sleep_time = self.get_next() - time.time() if self.get_next() else 10

                time.sleep(sleep_time)

        return _callback

    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'when': self.when,
            'next_run': self.get_next(),
            'enabled': self.is_enabled(),
            'state': self.state.name,
        }


class AlarmBackend(Backend):
    """
    Backend to handle user-configured alarms.

    Triggers:

        * :class:`platypush.message.event.alarm.AlarmStartedEvent` when an alarm starts.
        * :class:`platypush.message.event.alarm.AlarmSnoozedEvent` when an alarm is snoozed.
        * :class:`platypush.message.event.alarm.AlarmTimeoutEvent` when an alarm times out.
        * :class:`platypush.message.event.alarm.AlarmDismissedEvent` when an alarm is dismissed.

    """

    def __init__(self, alarms: Optional[Union[list, Dict[str, Any]]] = None, audio_plugin: str = 'media.mplayer',
                 *args, **kwargs):
        """
        :param alarms: List or name->value dict with the configured alarms. Example:

        .. code-block:: yaml

            morning_alarm:
                when: '0 7 * * 1-5'   # Cron expression format: run every weekday at 7 AM
                audio_file: ~/path/your_ringtone.mp3
                audio_plugin: media.mplayer
                audio_volume: 10       # 10%
                snooze_interval: 300   # 5 minutes snooze
                actions:
                    - action: tts.say
                      args:
                          text: Good morning

                    - action: light.hue.bri
                      args:
                          value: 1

                    - action: light.hue.bri
                      args:
                          value: 140
                          transitiontime: 150

            one_shot_alarm:
                when: '2020-02-18T07:00:00.000000'   # One-shot execution, with timestamp in ISO format
                audio_file: ~/path/your_ringtone.mp3
                actions:
                    - action: light.hue.on

        :param audio_plugin: Media plugin (instance of :class:`platypush.plugins.media.MediaPlugin`) that will be
            used to play the alarm audio (default: ``media.mplayer``).
        """
        super().__init__(*args, **kwargs)
        alarms = alarms or []
        if isinstance(alarms, dict):
            alarms = [{'name': name, **alarm} for name, alarm in alarms.items()]

        self.audio_plugin = audio_plugin
        alarms = [Alarm(**{'audio_plugin': self.audio_plugin, **alarm}) for alarm in alarms]
        self.alarms: Dict[str, Alarm] = {alarm.name: alarm for alarm in alarms}

    def add_alarm(self, when: str, actions: list, name: Optional[str] = None, audio_file: Optional[str] = None,
                  audio_volume: Optional[Union[int, float]] = None, enabled: bool = True) -> Alarm:
        alarm = Alarm(when=when, actions=actions, name=name, enabled=enabled, audio_file=audio_file,
                      audio_plugin=self.audio_plugin, audio_volume=audio_volume)

        if alarm.name in self.alarms:
            self.logger.info('Overwriting existing alarm {}'.format(alarm.name))
            self.alarms[alarm.name].stop()

        self.alarms[alarm.name] = alarm
        self.alarms[alarm.name].start()
        return self.alarms[alarm.name]

    def _get_alarm(self, name) -> Alarm:
        assert name in self.alarms, 'Alarm {} does not exist'.format(name)
        return self.alarms[name]

    def enable_alarm(self, name: str):
        self._get_alarm(name).enable()

    def disable_alarm(self, name: str):
        self._get_alarm(name).disable()

    def dismiss_alarm(self):
        alarm = self.get_running_alarm()
        if not alarm:
            self.logger.info('No alarm is running')
            return

        alarm.dismiss()

    def snooze_alarm(self, interval: Optional[str] = None):
        alarm = self.get_running_alarm()
        if not alarm:
            self.logger.info('No alarm is running')
            return

        alarm.snooze(interval=interval)

    def get_alarms(self) -> List[Alarm]:
        return sorted([alarm for alarm in self.alarms.values()], key=lambda alarm: alarm.get_next())

    def get_running_alarm(self) -> Optional[Alarm]:
        running_alarms = [alarm for alarm in self.alarms.values() if alarm.state == AlarmState.RUNNING]
        return running_alarms[0] if running_alarms else None

    def __enter__(self):
        for alarm in self.alarms.values():
            alarm.stop()
            alarm.start()

        self.logger.info('Initialized alarm backend with {} alarms'.format(len(self.alarms)))

    def __exit__(self, exc_type, exc_val, exc_tb):
        for alarm in self.alarms.values():
            alarm.stop()

        self.logger.info('Alarm backend terminated')

    def loop(self):
        for name, alarm in self.alarms.copy().items():
            if not alarm.timer or (not alarm.timer.is_alive() and alarm.state == AlarmState.SHUTDOWN):
                del self.alarms[name]

        time.sleep(10)


# vim:sw=4:ts=4:et:
