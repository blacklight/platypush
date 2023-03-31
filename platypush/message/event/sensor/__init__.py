from abc import ABC
from typing import Optional

from platypush.common.sensors import SensorDataType
from platypush.message.event import Event


class SensorDataEvent(Event, ABC):
    """
    Sensor events base class.
    """

    def __init__(
        self, *args, data: SensorDataType, source: Optional[str] = None, **kwargs
    ):
        """
        :param data: Sensor data.
        :param source: Sensor source - usually the plugin qualified name.
        """
        super().__init__(data=data, source=source, *args, **kwargs)


class SensorDataChangeEvent(SensorDataEvent):
    """
    Event triggered when a sensor has new data
    """


class SensorDataAboveThresholdEvent(SensorDataEvent):
    """
    Event triggered when a sensor's read goes above a configured threshold
    """


class SensorDataBelowThresholdEvent(SensorDataEvent):
    """
    Event triggered when a sensor's read goes below a configured threshold
    """


# vim:sw=4:ts=4:et:
