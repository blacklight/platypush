from typing import Optional

from platypush.message.event import Event


class AlarmEvent(Event):
    """
    Base class for alarm events.
    """

    def __init__(self, *args, name: Optional[str] = None, **kwargs):
        super().__init__(*args, name=name, **kwargs)


class AlarmEnabledEvent(AlarmEvent):
    """
    Triggered when an alarm is enabled.
    """


class AlarmDisabledEvent(AlarmEvent):
    """
    Triggered when an alarm is disabled.
    """


class AlarmStartedEvent(AlarmEvent):
    """
    Triggered when an alarm starts.
    """


class AlarmEndedEvent(AlarmEvent):
    """
    Triggered when an alarm stops.
    """


class AlarmDismissedEvent(AlarmEndedEvent):
    """
    Triggered when an alarm is dismissed.
    """


class AlarmSnoozedEvent(AlarmEvent):
    """
    Triggered when an alarm is snoozed.
    """


class AlarmTimeoutEvent(AlarmEndedEvent):
    """
    Triggered when an alarm times out.
    """


# vim:sw=4:ts=4:et:
