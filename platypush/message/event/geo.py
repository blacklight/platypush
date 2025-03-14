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

    @property
    def latitude(self) -> float:
        return self.args["latitude"]

    @property
    def longitude(self) -> float:
        return self.args["longitude"]

    @property
    def altitude(self) -> Optional[float]:
        return self.args.get("altitude")

    @property
    def address(self) -> Optional[str]:
        return self.args.get("address")

    @property
    def locality(self) -> Optional[str]:
        return self.args.get("locality")

    @property
    def country(self) -> Optional[str]:
        return self.args.get("country")

    @property
    def description(self) -> Optional[str]:
        return self.args.get("description")

    @property
    def timestamp(self) -> Optional[float]:
        return self.args.get("timestamp")


# vim:sw=4:ts=4:et:
