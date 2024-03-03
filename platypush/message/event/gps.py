from abc import ABC
from datetime import datetime
from typing import Optional

from platypush.message.event import Event


class GPSEvent(Event, ABC):
    """
    Generic class for GPS events.
    """


class GPSDeviceEvent(GPSEvent):
    """
    Event triggered when a new GPS device is connected or reconfigured.
    """

    def __init__(
        self,
        path: str,
        *args,
        activated: Optional[datetime] = None,
        native: bool = False,
        baudrate: Optional[int] = None,
        parity: Optional[str] = None,
        stopbits: Optional[int] = None,
        cycle: Optional[float] = None,
        driver: Optional[str] = None,
        subtype: Optional[str] = None,
        **kwargs
    ):
        """
        :param path: Device path.
        :param activated: Device activation timestamp.
        :param native: Device native status.
        :param baudrate: Device baudrate.
        :param parity: Device parity.
        :param stopbits: Device stopbits.
        :param cycle: Device cycle.
        :param driver: Device driver.
        :param subtype: Device subtype.
        """
        super().__init__(
            *args,
            path=path,
            activated=activated,
            native=native,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            cycle=cycle,
            driver=driver,
            subtype=subtype,
            **kwargs
        )


class GPSLocationUpdateEvent(GPSEvent):
    """
    Event triggered upon GPS status update.
    """

    def __init__(
        self,
        *args,
        device=None,
        latitude=None,
        longitude=None,
        altitude=None,
        mode=None,
        **kwargs
    ):
        super().__init__(
            *args,
            device=device,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            mode=mode,
            **kwargs
        )


class GPSEnabledEvent(GPSEvent):
    """
    Event triggered when the GPS polling is enabled.
    """


class GPSDisabledEvent(GPSEvent):
    """
    Event triggered when the GPS polling is disabled.
    """


# vim:sw=4:ts=4:et:
