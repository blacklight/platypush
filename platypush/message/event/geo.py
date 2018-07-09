from platypush.message.event import Event


class LatLongUpdateEvent(Event):
    """
    Event triggered upon GPS location update
    """

    def __init__(self, latitude, longitude, *args, **kwargs):
        """
        :param latitude: GPS latitude
        :type latitude: float

        :param longitude: GPS longitude
        :type longitude: float
        """

        super().__init__(latitude=latitude, longitude=longitude, *args, **kwargs)


# vim:sw=4:ts=4:et:

