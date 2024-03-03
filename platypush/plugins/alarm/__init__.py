from contextlib import contextmanager
import sys
from threading import RLock
from typing import Collection, Generator, Optional, Dict, Any, List, Union

from sqlalchemy.orm import Session

from platypush.context import get_plugin
from platypush.entities import EntityManager
from platypush.entities.alarm import Alarm as DbAlarm
from platypush.message.event.entities import EntityDeleteEvent
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.db import DbPlugin
from platypush.plugins.media import MediaPlugin
from platypush.procedure import Procedure
from platypush.utils import get_plugin_name_by_class
from platypush.utils.media import get_default_media_plugin

from ._model import Alarm, AlarmState


class AlarmPlugin(RunnablePlugin, EntityManager):
    """
    Alarm/timer plugin.

    It requires at least one enabled ``media`` plugin to be configured if you
    want to play audio resources.

    Example configuration:

    .. code-block:: yaml

        alarm:
            # Media plugin that will be used to play the alarm audio.
            # If not specified, the first available configured media plugin
            # will be used.
            media_plugin: media.vlc

            alarms:
                morning_alarm:
                    # Cron expression format: run every weekday at 7 AM
                    when: '0 7 * * 1-5'
                    media: ~/path/your_ringtone.mp3
                    audio_volume: 10       # 10%

                    # Repeat the played media resource until the alarm is
                    # snoozed/dismissed (default: true)
                    media_repeat: true

                    # Wait 5 minutes between a snooze and another run
                    snooze_interval: 300

                    # After 10 minutes with no manual snooze/dismiss,
                    # stop the alarm
                    dismiss_interval: 600

                    # Actions to be executed when the alarm goes on
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
                    # One-shot execution, with timestamp in ISO format
                    when: '2020-02-18T07:00:00.000000'
                    media: ~/path/your_ringtone.mp3
                    actions:
                        - action: light.hue.on

                timer:
                    # This alarm will execute the specified number of seconds
                    # after being initialized (5 minutes after the plugin has
                    # been initialized in this case)
                    when: 300
                    media: ~/path/your_ringtone.mp3
                    actions:
                        - action: light.hue.on

    """

    def __init__(
        self,
        alarms: Optional[Union[List[dict], Dict[str, dict]]] = None,
        media_plugin: Optional[str] = None,
        poll_interval: Optional[float] = 2.0,
        snooze_interval: float = 300.0,
        dismiss_interval: float = 300.0,
        **kwargs,
    ):
        """
        :param alarms: List or name->value dict with the configured alarms.
        :param media_plugin: Media plugin (instance of
            :class:`platypush.plugins.media.MediaPlugin`) that will be used to
            play the alarm audio. It needs to be a supported local media
            plugin, e.g. ``media.mplayer``, ``media.vlc``, ``media.mpv``,
            ``media.gstreamer``, ``sound``, etc. If not specified, the first
            available configured local media plugin will be used. This only
            applies to alarms that are configured to play an audio resource.
        :param poll_interval: (Internal) poll interval, in seconds (default: 2).
        :param snooze_interval: Default snooze interval in seconds. This
            specifies how long to wait between alarm runs when an alarm is
            dismissed (default: 300).
        :param dismiss_interval: Default dismiss interval in seconds. This
            specifies how long an alarm should run without being manually
            snoozed/dismissed before being automatically dismissed (default:
            300).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
        self.snooze_interval = snooze_interval
        self.dismiss_interval = dismiss_interval
        self._db_lock = RLock()
        alarms = alarms or []
        if isinstance(alarms, dict):
            alarms = [{'name': name, **alarm} for name, alarm in alarms.items()]

        if kwargs.get('audio_plugin'):
            self.logger.warning(
                'The audio_plugin parameter is deprecated. Use media_plugin instead'
            )
            media_plugin = media_plugin or kwargs.get('audio_plugin')

        try:
            plugin: Optional[MediaPlugin] = (
                get_plugin(media_plugin) if media_plugin else get_default_media_plugin()
            )
            assert plugin, 'No media/audio plugin configured'
            self.media_plugin = get_plugin_name_by_class(plugin.__class__)
        except AssertionError:
            self.media_plugin = None
            self.logger.warning(
                'No media plugin configured. Alarms that require audio playback will not work'
            )

        self.alarms = {
            alarm.name: alarm
            for alarm in [
                Alarm(
                    stop_event=self._should_stop,
                    static=True,
                    media_plugin=alarm.pop('media_plugin', self.media_plugin),
                    on_change=self._on_alarm_update,
                    **alarm,
                )
                for alarm in alarms
            ]
        }

        self._synced = False

    @property
    def _db(self) -> DbPlugin:
        db = get_plugin('db')
        assert db, 'No database plugin configured'
        return db

    @contextmanager
    def _get_session(self) -> Generator[Session, None, None]:
        with self._db_lock, self._db.get_session() as session:
            yield session

    def _merge_alarms(self, alarms: Dict[str, DbAlarm], session: Session):
        for name, alarm in alarms.items():
            if name in self.alarms:
                existing_alarm = self.alarms[name]

                # If the alarm is static, then we only want to override its
                # enabled state from the db record
                if existing_alarm.static:
                    existing_alarm.set_enabled(bool(alarm.enabled))
            else:
                # If the alarm record on the db is static, but the alarm is no
                # longer present in the configuration, then we want to delete it
                if alarm.static:
                    self._clear_alarm(alarm, session)
                else:
                    self.alarms[name] = Alarm.from_db(
                        alarm,
                        stop_event=self._should_stop,
                        media_plugin=alarm.media_plugin or self.media_plugin,
                        on_change=self._on_alarm_update,
                    )

        # Stop and remove alarms that are not statically configured no longer
        # present in the db
        for name, alarm in self.alarms.copy().items():
            if not alarm.static and name not in alarms:
                del self.alarms[name]
                alarm.stop()

    def _sync_alarms(self):
        with self._get_session() as session:
            db_alarms = {
                str(alarm.name): alarm for alarm in session.query(DbAlarm).all()
            }

            self._merge_alarms(db_alarms, session)
            self._clear_expired_alarms(session)
            for name, alarm in self.alarms.copy().items():
                if not (name in db_alarms or alarm.static):
                    self.alarms.pop(name, None)

        if not self._synced:
            self.publish_entities(self.alarms.values())
            self._synced = True

    def _clear_alarm(self, alarm: DbAlarm, session: Session):
        alarm_obj = self.alarms.pop(str(alarm.name), None)
        if alarm_obj:
            alarm_obj.stop()

        session.delete(alarm)
        self._bus.post(EntityDeleteEvent(entity=alarm))

    def _clear_expired_alarms(self, session: Session):
        expired_alarms = [
            alarm for alarm in self.alarms.values() if alarm.should_stop()
        ]

        if not expired_alarms:
            return

        expired_alarm_records = session.query(DbAlarm).filter(
            DbAlarm.name.in_([alarm.name for alarm in expired_alarms])
        )

        for alarm in expired_alarm_records:
            self._clear_alarm(alarm, session)

    def _get_alarms(self) -> List[Alarm]:
        return sorted(
            self.alarms.values(),
            key=lambda alarm: alarm.get_next() or sys.maxsize,
        )

    def _get_alarm(self, name: str) -> Alarm:
        assert name in self.alarms, f'The alarm {name} does not exist'
        return self.alarms[name]

    def _get_current_alarm(self) -> Optional[Alarm]:
        return next(
            iter(
                alarm
                for alarm in self.alarms.values()
                if alarm.state in {AlarmState.RUNNING, AlarmState.SNOOZED}
            ),
            None,
        )

    def _enable(self, name: str):
        self._get_alarm(name).enable()

    def _disable(self, name: str):
        self._get_alarm(name).disable()

    def _on_alarm_update(self, alarm: Alarm):
        with self._db_lock:
            if alarm.should_stop():
                return

            self.publish_entities([alarm])

    def _add(
        self,
        when: Union[str, int, float],
        actions: Union[list, Procedure],
        name: Optional[str] = None,
        media: Optional[str] = None,
        media_plugin: Optional[str] = None,
        media_repeat: bool = True,
        audio_file: Optional[str] = None,
        audio_volume: Optional[Union[int, float]] = None,
        enabled: bool = True,
        snooze_interval: Optional[float] = None,
        dismiss_interval: Optional[float] = None,
    ) -> Alarm:
        alarm = Alarm(
            when=when,
            actions=actions,
            name=name,
            enabled=enabled,
            media=media or audio_file,
            media_plugin=media_plugin or self.media_plugin,
            media_repeat=media_repeat,
            audio_volume=audio_volume,
            snooze_interval=snooze_interval or self.snooze_interval,
            dismiss_interval=dismiss_interval or self.dismiss_interval,
            stop_event=self._should_stop,
            on_change=self._on_alarm_update,
        )

        if alarm.name in self.alarms:
            assert not self.alarms[alarm.name].static, (
                f'Alarm {alarm.name} is statically defined in the configuration, '
                'cannot overwrite it programmatically'
            )

            self.logger.info('Overwriting existing alarm: %s', alarm.name)
            self.alarms[alarm.name].stop()

        self.alarms[alarm.name] = alarm
        alarm.start()
        self.publish_entities([alarm])
        return alarm

    def _dismiss(self):
        alarm = self._get_current_alarm()
        if not alarm:
            self.logger.info('No alarm is running')
            return

        alarm.dismiss()

    def _snooze(self, interval: Optional[float] = None):
        alarm = self._get_current_alarm()
        if not alarm:
            self.logger.info('No alarm is running')
            return

        interval = interval or alarm.snooze_interval or self.snooze_interval
        alarm.snooze(interval=interval)

    @action
    def add(
        self,
        when: Union[str, int, float],
        actions: Optional[list] = None,
        name: Optional[str] = None,
        media: Optional[str] = None,
        media_plugin: Optional[str] = None,
        media_repeat: bool = True,
        audio_file: Optional[str] = None,
        audio_volume: Optional[Union[int, float]] = None,
        enabled: bool = True,
        snooze_interval: Optional[float] = None,
        dismiss_interval: Optional[float] = None,
    ) -> dict:
        """
        Add a new alarm.

        :param when: When the alarm should be executed. It can be either a cron
            expression (for recurrent alarms), or a datetime string in ISO
            format (for one-shot alarms/timers), or an integer/float
            representing the number of seconds before the alarm goes on (e.g.
            300 for 5 minutes).
        :param actions: List of actions to be executed.
        :param name: Alarm name.
        :param media: Path of the audio file to be played.
        :param media_plugin: Override the default media plugin for this alarm.
        :param media_repeat: Repeat the played media resource until the alarm
            is snoozed/dismissed (default: True).
        :param audio_volume: Volume of the audio.
        :param enabled: Whether the new alarm should be enabled (default: True).
        :param snooze_interval: Snooze seconds before playing the alarm again.
        :param dismiss_interval: Dismiss seconds before stopping the alarm.
        :return: The newly created alarm.
        """
        if audio_file:
            self.logger.warning(
                'The audio_file parameter is deprecated. Use media instead'
            )

        return self._add(
            when=when,
            media=media,
            media_plugin=media_plugin,
            media_repeat=media_repeat,
            audio_file=audio_file,
            actions=actions or [],
            name=name,
            enabled=enabled,
            audio_volume=audio_volume,
            snooze_interval=snooze_interval,
            dismiss_interval=dismiss_interval,
        ).to_dict()

    @action
    def edit(
        self,
        name: str,
        new_name: Optional[str] = None,
        when: Optional[Union[str, int, float]] = None,
        actions: Optional[list] = None,
        media: Optional[str] = None,
        media_plugin: Optional[str] = None,
        media_repeat: Optional[bool] = None,
        audio_volume: Optional[Union[int, float]] = None,
        enabled: Optional[bool] = None,
        snooze_interval: Optional[float] = None,
        dismiss_interval: Optional[float] = None,
    ) -> dict:
        """
        Edit an existing alarm.

        Note that you can only edit the alarms that are not statically defined
        through the configuration.

        :param name: Alarm name.
        :param new_name: New alarm name.
        :param when: When the alarm should be executed. It can be either a cron
            expression (for recurrent alarms), or a datetime string in ISO
            format (for one-shot alarms/timers), or an integer/float
            representing the number of seconds before the alarm goes on (e.g.
            300 for 5 minutes).
        :param actions: List of actions to be executed.
        :param media: Path of the audio file to be played.
        :param media_plugin: Override the default media plugin for this alarm.
        :param media_repeat: Repeat the played media resource until the alarm
            is snoozed/dismissed (default: True).
        :param audio_volume: Volume of the audio.
        :param enabled: Whether the new alarm should be enabled.
        :param snooze_interval: Snooze seconds before playing the alarm again.
        :param dismiss_interval: Dismiss seconds before stopping the alarm.
        :return: The modified alarm.
        """
        alarm = self._get_alarm(name)
        assert not alarm.static, (
            f'Alarm {name} is statically defined in the configuration, '
            'cannot overwrite it programmatically'
        )

        if new_name and new_name != name:
            assert (
                new_name not in self.alarms
            ), f'An alarm with name {new_name} already exists'

        with self._db.get_session() as session:
            db_alarm = session.query(DbAlarm).filter_by(name=name).first()
            self._clear_alarm(db_alarm, session)
            return self._add(
                when=when or alarm.when,
                media=media or alarm.media,
                media_plugin=media_plugin or alarm.media_plugin or self.media_plugin,
                media_repeat=media_repeat
                if media_repeat is not None
                else alarm.media_repeat,
                actions=actions if actions is not None else (alarm.actions or []),
                name=new_name or name,
                enabled=enabled if enabled is not None else alarm.is_enabled(),
                audio_volume=audio_volume
                if audio_volume is not None
                else alarm.audio_volume,
                snooze_interval=snooze_interval or alarm.snooze_interval,
                dismiss_interval=dismiss_interval or alarm.dismiss_interval,
            ).to_dict()

    @action
    def delete(self, name: str):
        """
        Delete an alarm.

        :param name: Alarm name.
        """
        try:
            alarm = self._get_alarm(name)
        except AssertionError:
            self.logger.warning('Alarm %s does not exist', name)
            return

        assert not alarm.static, (
            f'Alarm {name} is statically defined in the configuration, '
            'cannot overwrite it programmatically'
        )

        alarm.stop()

        with self._db.get_session() as session:
            db_alarm = session.query(DbAlarm).filter_by(name=name).first()
            if not db_alarm:
                self.logger.warning('Alarm %s does not exist', name)
                return

            self._clear_alarm(db_alarm, session)

    @action
    def enable(self, name: str):
        """
        Enable an alarm.

        :param name: Alarm name.
        """
        self._enable(name)

    @action
    def disable(self, name: str):
        """
        Disable an alarm. This will prevent the alarm from executing until re-enabled or until the application
        is restarted.

        :param name: Alarm name.
        """
        self._disable(name)

    @action
    def set_enabled(self, name: str, enabled: bool):
        """
        Enable/disable an alarm.

        :param name: Alarm name.
        :param enabled: Whether the alarm should be enabled.
        """
        if enabled:
            self._enable(name)
        else:
            self._disable(name)

    @action
    def dismiss(self):
        """
        Dismiss the alarm that is currently running.
        """
        self._dismiss()

    @action
    def snooze(self, interval: Optional[float] = None):
        """
        Snooze the alarm that is currently running for the specified number of seconds.
        The alarm will stop and resume again later.

        :param interval: Snooze seconds before playing the alarm again (default: 300).
        """
        self._snooze(interval=interval)

    @action
    def get_alarms(self) -> List[Dict[str, Any]]:
        """
        Deprecated alias for :meth:`.status`.
        """
        self.logger.warning('get_alarms() is deprecated. Use status() instead')
        return self.status()  # type: ignore

    @action
    def status(self, *_, **__) -> List[Dict[str, Any]]:
        """
        Get the list of configured alarms and their status.

        :return: List of the alarms, sorted by next scheduled run. Example:

            .. code-block:: json

                [
                    {
                        "name": "Morning alarm",
                        "id": 1,
                        "when": "0 8 * * 1-5",
                        "next_run": "2023-12-06T08:00:00.000000",
                        "enabled": true,
                        "media": "/path/to/media.mp3",
                        "media_plugin": "media.vlc",
                        "media_repeat": true,
                        "audio_volume": 10,
                        "snooze_interval": 300,
                        "dismiss_interval": 300,
                        "actions": [
                            {
                                "action": "tts.say",
                                "args": {
                                    "text": "Good morning"
                                }
                            },
                            {
                                "action": "light.hue.on"
                            }
                        ],
                        "state": "RUNNING"
                    }
                ]

        """
        ret = [alarm.to_dict() for alarm in self._get_alarms()]
        self.publish_entities(self.alarms.values())
        return ret

    def transform_entities(self, entities: Collection[Alarm], **_) -> List[DbAlarm]:
        return [alarm.to_db() for alarm in entities]

    def main(self):
        self._sync_alarms()
        for alarm in self.alarms.values():
            alarm.start()

        while not self.should_stop():
            self._sync_alarms()
            self.wait_stop(self.poll_interval)

    def stop(self):
        for alarm in self.alarms.values():
            alarm.stop()

        super().stop()


# vim:sw=4:ts=4:et:
