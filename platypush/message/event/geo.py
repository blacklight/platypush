from platypush.message.event import Event


class LatLongUpdateEvent(Event):
    def __init__(self, latitude, longitude, *args, **kwargs):
        super().__init__(latitude=latitude, longitude=longitude, *args, **kwargs)


# vim:sw=4:ts=4:et:

