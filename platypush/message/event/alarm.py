from typing import Optional

from platypush.message.event import Event


class AlarmEvent(Event):
    def __init__(self, name: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, name=name, **kwargs)


class AlarmStartedEvent(AlarmEvent):
    """
    Triggered when an alarm starts.
    """
    pass


class AlarmEndedEvent(AlarmEvent):
    """
    Triggered when an alarm stops.
    """
    pass


class AlarmDismissedEvent(AlarmEndedEvent):
    """
    Triggered when an alarm is dismissed.
    """
    pass


class AlarmSnoozedEvent(AlarmEvent):
    """
    Triggered when an alarm is snoozed.
    """
    pass


class AlarmTimeoutEvent(AlarmEndedEvent):
    """
    Triggered when an alarm times out.
    """
    pass


# vim:sw=4:ts=4:et:
