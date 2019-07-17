from platypush.message.event import Event

class GoogleDeviceEvent(Event):
    """
    Base class for Google device events, see `managing traits and handlers <https://developers.google.com/assistant/sdk/guides/service/python/extend/add-trait-and-handler>`_.
    """

    def __init__(self, device_id, device_model_id=None, *args, **kwargs):
        super().__init__(*args, device_id=device_id, device_model_id=device_model_id, **kwargs)


class GoogleDeviceOnOffEvent(GoogleDeviceEvent):
    """
    Event triggered when a device receives an on/off command
    """

    def __init__(self, on, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on = on


# vim:sw=4:ts=4:et:
