from platypush.message.event import Event


class LatLongUpdateEvent(Event):
    """
    Event triggered upon GPS location update
    """

    def __init__(self, latitude, longitude, altitude=None, *args, **kwargs):
        """
        :param latitude: GPS latitude
        :type latitude: float

        :param longitude: GPS longitude
        :type longitude: float

        :param altitude: GPS altitude
        :type altitude: float
        """

        super().__init__(*args, latitude=latitude, longitude=longitude, altitude=altitude, **kwargs)


# vim:sw=4:ts=4:et:
