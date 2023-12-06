import sys
from typing import Optional, Dict, Any, List, Union
from platypush.context import get_plugin

from platypush.plugins import RunnablePlugin, action
from platypush.plugins.media import MediaPlugin
from platypush.utils import get_plugin_name_by_class
from platypush.utils.media import get_default_media_plugin

from ._model import Alarm, AlarmState


class AlarmPlugin(RunnablePlugin):
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
        alarms: Optional[Union[list, Dict[str, Any]]] = None,
        media_plugin: Optional[str] = None,
        poll_interval: Optional[float] = 5.0,
        **kwargs,
    ):
        """
        :param alarms: List or name->value dict with the configured alarms. Example:
        :param media_plugin: Media plugin (instance of
            :class:`platypush.plugins.media.MediaPlugin`) that will be used to
            play the alarm audio. It needs to be a supported local media
            plugin, e.g. ``media.mplayer``, ``media.vlc``, ``media.mpv``,
            ``media.gstreamer`` etc. If not specified, the first available
            configured local media plugin will be used. This only applies to
            alarms that are configured to play an audio resource.
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
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

        alarms = [
            Alarm(
                stop_event=self._should_stop,
                **{'media_plugin': self.media_plugin, **alarm},
            )
            for alarm in alarms
        ]

        self.alarms: Dict[str, Alarm] = {alarm.name: alarm for alarm in alarms}

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
                if alarm.state == AlarmState.RUNNING
            ),
            None,
        )

    def _enable(self, name: str):
        self._get_alarm(name).enable()

    def _disable(self, name: str):
        self._get_alarm(name).disable()

    def _add(
        self,
        when: Union[str, int, float],
        actions: list,
        name: Optional[str] = None,
        media: Optional[str] = None,
        audio_file: Optional[str] = None,
        audio_volume: Optional[Union[int, float]] = None,
        enabled: bool = True,
    ) -> Alarm:
        alarm = Alarm(
            when=when,
            actions=actions,
            name=name,
            enabled=enabled,
            media=media or audio_file,
            media_plugin=self.media_plugin,
            audio_volume=audio_volume,
            stop_event=self._should_stop,
        )

        if alarm.name in self.alarms:
            self.logger.info('Overwriting existing alarm: %s', alarm.name)
            self.alarms[alarm.name].stop()

        self.alarms[alarm.name] = alarm
        self.alarms[alarm.name].start()
        return self.alarms[alarm.name]

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

        alarm.snooze(interval=interval)

    @action
    def add(
        self,
        when: Union[str, int, float],
        actions: Optional[list] = None,
        name: Optional[str] = None,
        media: Optional[str] = None,
        audio_file: Optional[str] = None,
        audio_volume: Optional[Union[int, float]] = None,
        enabled: bool = True,
    ) -> str:
        """
        Add a new alarm. NOTE: alarms that aren't statically defined in the
        plugin configuration will only run in the current session. If you want
        an alarm to be permanently stored, you should configure it in the alarm
        backend configuration. You may want to add an alarm dynamically if it's
        a one-time alarm instead.

        :param when: When the alarm should be executed. It can be either a cron
            expression (for recurrent alarms), or a datetime string in ISO
            format (for one-shot alarms/timers), or an integer/float
            representing the number of seconds before the alarm goes on (e.g.
            300 for 5 minutes).
        :param actions: List of actions to be executed.
        :param name: Alarm name.
        :param media: Path of the audio file to be played.
        :param audio_volume: Volume of the audio.
        :param enabled: Whether the new alarm should be enabled (default: True).
        :return: The alarm name.
        """
        if audio_file:
            self.logger.warning(
                'The audio_file parameter is deprecated. Use media instead'
            )

        alarm = self._add(
            when=when,
            media=media,
            audio_file=audio_file,
            actions=actions or [],
            name=name,
            enabled=enabled,
            audio_volume=audio_volume,
        )
        return alarm.name

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
    def dismiss(self):
        """
        Dismiss the alarm that is currently running.
        """
        self._dismiss()

    @action
    def snooze(self, interval: Optional[float] = 300.0):
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
    def status(self) -> List[Dict[str, Any]]:
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
                        "state": "RUNNING"
                    }
                ]

        """
        return [alarm.to_dict() for alarm in self._get_alarms()]

    def main(self):
        for alarm in self.alarms.values():
            alarm.start()

        while not self.should_stop():
            for name, alarm in self.alarms.copy().items():
                if not alarm.timer or (
                    not alarm.timer.is_alive() and alarm.state == AlarmState.SHUTDOWN
                ):
                    del self.alarms[name]

            self.wait_stop(self.poll_interval)

    def stop(self):
        for alarm in self.alarms.values():
            alarm.stop()

        super().stop()


# vim:sw=4:ts=4:et:
