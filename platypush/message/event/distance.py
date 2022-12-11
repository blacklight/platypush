import logging

from platypush.message.event import Event


class DistanceSensorEvent(Event):
    """
    Event triggered when a new value is processed by a distance sensor.
    """

    def __init__(self, distance: float, unit: str = 'mm', *args, **kwargs):
        super().__init__(
            *args,
            distance=distance,
            unit=unit,
            logging_level=logging.DEBUG,
            disable_web_clients_notification=True,
            **kwargs
        )


# vim:sw=4:ts=4:et:
