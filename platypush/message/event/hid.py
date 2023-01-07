from platypush.message.event import Event


class HidBaseEvent(Event):
    """
    Base class for HID events.
    """

    def __init__(
        self,
        *args,
        path: str,
        serial_number: str,
        vendor_id: int,
        product_id: int,
        product_string: str,
        manufacturer_string: str,
        **kwargs
    ):
        super().__init__(
            *args,
            path=path,
            serial_number=serial_number,
            vendor_id=vendor_id,
            product_id=product_id,
            product_string=product_string,
            manufacturer_string=manufacturer_string,
            **kwargs
        )


class HidDeviceConnectedEvent(HidBaseEvent):
    """
    Event triggered when a device is discovered.
    """


class HidDeviceDisconnectedEvent(HidBaseEvent):
    """
    Event triggered when a device is disconnected.
    """


class HidDeviceDataEvent(HidBaseEvent):
    """
    Event triggered when a monitored device sends some data.
    """

    def __init__(self, *args, data: str, **kwargs):
        """
        :param data: Hex-encoded representation of the received data.
        """
        super().__init__(*args, data=data, **kwargs)


# vim:sw=4:ts=4:et:
