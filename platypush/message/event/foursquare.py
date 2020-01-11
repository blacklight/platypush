from typing import Dict, Any

from platypush.message.event import Event


class FoursquareCheckinEvent(Event):
    """
    Event triggered when a new check-in occurs.
    """
    def __init__(self, checkin: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, checkin=checkin, **kwargs)


# vim:sw=4:ts=4:et:
