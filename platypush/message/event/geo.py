from datetime import datetime
from typing import Optional, Union

from dateutil.parser import isoparse

from platypush.message.event import Event


class LatLongUpdateEvent(Event):
    """
    Event triggered upon GPS location update
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        *,
        altitude: Optional[float] = None,
        address: Optional[str] = None,
        locality: Optional[str] = None,
        country: Optional[str] = None,
        description: Optional[str] = None,
        timestamp: Optional[Union[float, datetime, str]] = None,
        **kwargs,
    ):
        """
        :param latitude: GPS latitude.
        :param longitude: GPS longitude.
        :param altitude: GPS altitude.
        :param address: Human-readable address.
        :param locality: Locality.
        :param country: Country or city.
        :param description: Description.
        :param timestamp: Timestamp of the event (default: now).
        """
        t = timestamp or datetime.now()
        if isinstance(t, str):
            t = isoparse(t)
        elif isinstance(t, datetime):
            t = t.timestamp()

        super().__init__(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            address=address,
            locality=locality,
            country=country,
            description=description,
            timestamp=timestamp,
            **kwargs,
        )


# vim:sw=4:ts=4:et:
