from platypush.message.event import Event


class GPSEvent(Event):
    """
    Generic class for GPS events
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GPSVersionEvent(GPSEvent):
    """
    Event usually triggered on startup or reconnection, when the GPS device advertises its version parameters
    """

    def __init__(self, release=None, rev=None, proto_major=None, proto_minor=None, *args, **kwargs):
        super().__init__(release=release, rev=rev, proto_major=proto_major, proto_minor=proto_minor, *args, **kwargs)


class GPSDeviceEvent(GPSEvent):
    """
    Event triggered when a new GPS device is connected or reconfigured
    """

    def __init__(self, path, activated=None, native=False, bps=None, parity=None, stopbits=None,
                 cycle=None, driver=None, *args, **kwargs):
        super().__init__(*args, path=path, activated=activated, native=native, bps=bps, parity=parity,
                         stopbits=stopbits, cycle=cycle, driver=driver, **kwargs)


class GPSUpdateEvent(GPSEvent):
    """
    Event triggered upon GPS status update
    """

    def __init__(self, device=None, latitude=None, longitude=None, altitude=None, mode=None, epv=None, eph=None,
                 sep=None, *args, **kwargs):
        super().__init__(*args, device=device, latitude=latitude, longitude=longitude, altitude=altitude,
                         mode=mode, epv=epv, eph=eph, sep=sep, **kwargs)


# vim:sw=4:ts=4:et:
