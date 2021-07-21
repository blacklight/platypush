from datetime import datetime
from typing import Optional

from platypush.message.event import Event


class SunEvent(Event):
    """
    Base class for sun related events (sunrise and sunset).
    """
    def __init__(self, latitude: Optional[float] = None, longitude: Optional[float] = None,
                 time: Optional[datetime] = None, *args, **kwargs):
        """
        :param latitude: Latitude for the sun event.
        :param longitude: Longitude for the sun event.
        :param time: Event timestamp.
        """
        super().__init__(*args, latitude=latitude, longitude=longitude, time=time, **kwargs)
        self.latitude = latitude
        self.longitude = longitude
        self.time = time


class SunriseEvent(SunEvent):
    """
    Class for sunrise events.
    """


class SunsetEvent(SunEvent):
    """
    Class for sunset events.
    """


# vim:sw=4:ts=4:et:
