from typing import Optional, Dict, Any, List, Union

from platypush.backend.alarm import AlarmBackend
from platypush.context import get_backend
from platypush.plugins import Plugin, action


class AlarmPlugin(Plugin):
    """
    Alarm/timer plugin.

    Requires:

        - The :class:`platypush.backend.alarm.AlarmBackend` backend configured and enabled.

    """

    @staticmethod
    def _get_backend() -> AlarmBackend:
        return get_backend('alarm')

    @action
    def add(self, when: str, actions: Optional[list] = None, name: Optional[str] = None,
            audio_file: Optional[str] = None, audio_volume: Optional[Union[int, float]] = None,
            enabled: bool = True) -> str:
        """
        Add a new alarm. NOTE: alarms that aren't configured in the :class:`platypush.backend.alarm.AlarmBackend`
        will only run in the current session. If you want an alarm to be permanently stored, you should configure
        it in the alarm backend configuration. You may want to add an alarm dynamically if it's a one-time alarm instead

        :param when: When the alarm should be executed. It can be either a cron expression (for recurrent alarms), or
            a datetime string in ISO format (for one-shot alarms/timers), or an integer representing the number of
            seconds before the alarm goes on (e.g. 300 for 5 minutes).
        :param actions: List of actions to be executed.
        :param name: Alarm name.
        :param audio_file: Path of the audio file to be played.
        :param audio_volume: Volume of the audio.
        :param enabled: Whether the new alarm should be enabled (default: True).
        :return: The alarm name.
        """
        alarm = self._get_backend().add_alarm(when=when, audio_file=audio_file, actions=actions or [],
                                              name=name, enabled=enabled, audio_volume=audio_volume)
        return alarm.name

    @action
    def enable(self, name: str):
        """
        Enable an alarm.

        :param name: Alarm name.
        """
        self._get_backend().enable_alarm(name)

    @action
    def disable(self, name: str):
        """
        Disable an alarm. This will prevent the alarm from executing until re-enabled or until the application
        is restarted.

        :param name: Alarm name.
        """
        self._get_backend().disable_alarm(name)

    @action
    def dismiss(self):
        """
        Dismiss the alarm that is currently running.
        """
        self._get_backend().dismiss_alarm()

    @action
    def snooze(self, interval: Optional[float] = 300.0):
        """
        Snooze the alarm that is currently running for the specified number of seconds.
        The alarm will stop and resume again later.

        :param interval: Snooze seconds before playing the alarm again (default: 300).
        """
        self._get_backend().snooze_alarm(interval=interval)

    @action
    def get_alarms(self) -> List[Dict[str, Any]]:
        """
        Get the list of configured alarms.

        :return: List of the alarms, sorted by next scheduled run.
        """
        return [alarm.to_dict() for alarm in self._get_backend().get_alarms()]


# vim:sw=4:ts=4:et:
