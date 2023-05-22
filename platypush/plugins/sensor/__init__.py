from abc import ABC, abstractmethod
from typing import Collection, Iterable, List, Mapping, Optional, Tuple, Type, Union
from typing_extensions import override

from platypush.common.sensors import Numeric, SensorDataType
from platypush.context import get_bus
from platypush.entities import Entity
from platypush.entities.managers.sensors import SensorEntityManager
from platypush.message.event.sensor import (
    SensorDataAboveThresholdEvent,
    SensorDataBelowThresholdEvent,
    SensorDataChangeEvent,
    SensorDataEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.utils import get_plugin_name_by_class

NoneType = type(None)
ThresholdType = Union[Numeric, Tuple[Numeric, Numeric]]
ThresholdConfiguration = Union[ThresholdType, Mapping[str, ThresholdType]]


class SensorPlugin(RunnablePlugin, SensorEntityManager, ABC):
    """
    Sensor abstract plugin. Any plugin that interacts with sensors
    should implement this class.

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    _max_retry_secs = 60.0
    """
    In case of failure, we apply an exponential back-off retry algorithm. This
    is the maximum number of seconds that we should wait during these retries.
    """

    def __init__(
        self,
        thresholds: Optional[ThresholdConfiguration] = None,
        tolerance: SensorDataType = 0,
        enabled_sensors: Optional[Iterable[str]] = None,
        **kwargs,
    ):
        """
        :param thresholds: A number, numeric pair or mapping of ``str`` to
            number/numeric pair representing the thresholds for the sensor.

            Examples:

                .. code-block:: yaml

                    # Any value below 25 from any sensor will trigger a
                    # SensorDataBelowThresholdEvent, if the previous value was
                    # equal or above, and any value above 25 will trigger a
                    # SensorDataAboveThresholdEvent, if the previous value was
                    # equal or below
                    thresholds: 25.0

                    # Same as above, but the threshold is only applied to
                    # ``temperature`` readings
                    thresholds:
                        temperature: 25.0

                    # Any value below 20 from any sensor will trigger a
                    # SensorDataBelowThresholdEvent, if the previous value was
                    # equal or above, and any value above 25 will trigger a
                    # SensorDataAboveThresholdEvent, if the previous value was
                    # equal or below (hysteresis configuration with double
                    # threshold)
                    thresholds:
                        - 20.0
                        - 25.0

                    # Same as above, but the threshold is only applied to
                    # ``temperature`` readings
                    thresholds:
                        temperature:
                            - 20.0
                            - 25.0

        :param tolerance: If set, then the sensor change events will be
            triggered only if the difference between the new value and the
            previous value is higher than the specified tolerance. For example,
            if the sensor data is mapped to a dictionary::

                {
                    "temperature": 0.01,  # Tolerance on the 2nd decimal digit
                    "humidity": 0.1       # Tolerance on the 1st decimal digit
                }

            Or, if it's a raw scalar number::

                0.1  # Tolerance on the 1st decimal digit

            Or, if it's a list of values::

                [
                    0.01,   # Tolerance on the 2nd decimal digit for the first value
                    0.1     # Tolerance on the 1st decimal digit for the second value
                ]

        :param enabled_sensors: If :meth:`.get_measurement` returns a key-value
            mapping, and ``enabled_sensors`` is set, then only the reported
            sensor keys will be returned.
        """
        super().__init__(**kwargs)
        self._tolerance = tolerance
        self._thresholds = thresholds
        self._enabled_sensors = set(enabled_sensors or [])
        self._last_measurement: Optional[SensorDataType] = None
        """ Latest measurement from the sensor. """

    def _has_changes_scalar(
        self,
        old_data: Union[int, float],
        new_data: Union[int, float],
        attr: Optional[str] = None,
        index: Optional[int] = None,
    ) -> bool:
        """
        Returns ``True`` if the new data has changes compared to the old data -
        limited to numeric scalar values.
        """
        if isinstance(self._tolerance, (int, float)):
            tolerance = self._tolerance
        elif isinstance(self._tolerance, dict) and attr:
            tolerance = self._tolerance.get(attr, 0)  # type: ignore
        elif isinstance(self._tolerance, (list, tuple)) and index:
            tolerance = self._tolerance[index]
        else:
            tolerance = 0

        return abs(old_data - new_data) > tolerance

    def _has_changes(
        self,
        old_data: Optional[SensorDataType],
        new_data: Optional[SensorDataType],
        attr: Optional[str] = None,
        index: Optional[int] = None,
    ) -> bool:
        """
        Returns ``True`` if the new data has changes compared to the old data.
        It also applies the configured tolerance thresholds.
        """
        # If there is no previous data, then the new data will always be a change
        if old_data is None:
            return True

        # If the new data is missing, then we have no new changes
        if new_data is None:
            return False

        # If the data is scalar, then run the comparison logic
        if isinstance(old_data, (int, float)) and isinstance(new_data, (int, float)):
            return self._has_changes_scalar(old_data, new_data, attr, index)

        # If the data is dict-like, recursively call _has_changes on its attributes
        if isinstance(old_data, dict) and isinstance(new_data, dict):
            return any(
                self._has_changes(old_data.get(attr), value, attr=attr)  # type: ignore
                for attr, value in new_data.items()
            )

        # If the data is list-like, recursively call _has_changes on its values
        if isinstance(old_data, (list, tuple)) and isinstance(new_data, (list, tuple)):
            return any(
                self._has_changes(old_data[i], value, index=i)
                for i, value in enumerate(new_data)
            )

        return old_data != new_data

    def _process_scalar_threshold_events(
        self,
        old_data: Optional[Numeric],
        new_data: Numeric,
        attr: Optional[str] = None,
    ) -> List[SensorDataEvent]:
        """
        Inner scalar processing for sensor above/below threshold events.
        """
        event_types: List[Type[SensorDataEvent]] = []
        event_args = {
            'source': get_plugin_name_by_class(self.__class__),
        }

        # If we're mapping against a dict attribute, extract its thresholds,
        # otherwise use the default configured thresholds
        thresholds = (
            self._thresholds.get(attr)
            if attr and isinstance(self._thresholds, dict)
            else self._thresholds
        )

        # Normalize low/high thresholds
        low_t, high_t = (
            sorted(thresholds[:2])
            if isinstance(thresholds, (list, tuple))
            else (thresholds, thresholds)
        )

        if low_t is None or high_t is None:
            return []

        assert isinstance(low_t, (int, float)) and isinstance(
            high_t, (int, float)
        ), f'Non-numeric thresholds detected: "{low_t}" and "{high_t}"'

        # Above threshold case
        if (old_data is None or old_data <= high_t) and new_data > high_t:
            event_types.append(SensorDataAboveThresholdEvent)
        # Below threshold case
        elif (old_data is None or old_data >= low_t) and new_data < low_t:
            event_types.append(SensorDataBelowThresholdEvent)

        return [
            event_type(
                data={attr: new_data} if attr else new_data,
                **event_args,
            )
            for event_type in event_types
        ]

    def _process_threshold_events(
        self,
        old_data: Optional[SensorDataType],
        new_data: SensorDataType,
        attr: Optional[str] = None,
    ) -> List[SensorDataEvent]:
        """
        Processes sensor above/below threshold events.
        """
        events: List[SensorDataEvent] = []

        # If there are no configured thresholds, there's nothing to do
        if self._thresholds in (None, {}, (), []):
            return events

        # Scalar case
        if isinstance(old_data, (int, float, NoneType)) and isinstance(
            new_data, (int, float)
        ):
            return self._process_scalar_threshold_events(
                old_data, new_data, attr  # type: ignore
            )

        # From here on, threshold comparison only applies if both the old and
        # new data is a str -> number mapping
        if not (isinstance(old_data, (dict, NoneType)) and isinstance(new_data, dict)):
            return events

        # Recursively call _process_threshold_events on the data attributes
        for attr, value in new_data.items():  # type: ignore
            events.extend(
                self._process_threshold_events(
                    old_data=(
                        old_data.get(attr)  # type: ignore
                        if isinstance(old_data, dict)
                        else old_data
                    ),
                    new_data=value,
                    attr=str(attr),
                )
            )

        return events

    def _process_sensor_events(
        self, old_data: Optional[SensorDataType], new_data: Optional[SensorDataType]
    ) -> bool:
        """
        Given the previous and new measurement, it runs the comparison logic
        against the configured tolerance values and thresholds, and it
        processes the required sensor data change and above/below threshold
        events.

        :return: ``True`` if some events were processed for the new data,
            ``False`` otherwise.
        """
        # If the new data is missing or there are no changes, there are no
        # events to process
        if new_data is None or not self._has_changes(old_data, new_data):
            return False

        events = [
            SensorDataChangeEvent(
                data=new_data,  # type: ignore
                source=get_plugin_name_by_class(self.__class__),
            ),
            *self._process_threshold_events(old_data, new_data),
        ]

        for event in events:
            get_bus().post(event)

        self.publish_entities(new_data)
        return True

    def _update_last_measurement(self, new_data: SensorDataType):
        """
        Update the ``_last_measurement`` attribute with the newly acquired data.
        """
        # If there is no last measurement, or either the new or old
        # measurements are not dictionaries, then overwrite the previous data
        # with the new data
        if not (
            isinstance(self._last_measurement, dict) and isinstance(new_data, dict)
        ):
            self._last_measurement = new_data

        # Otherwise, merge the old data with the new
        self._last_measurement.update(new_data)  # type: ignore

    def _filter_enabled_sensors(self, data: SensorDataType) -> SensorDataType:
        """
        If ``data`` is a sensor mapping, and ``enabled_sensors`` is set, filter
        out only the requested keys.
        """
        if not (isinstance(data, dict) and self._enabled_sensors):
            return data

        return {k: v for k, v in data.items() if k in self._enabled_sensors}

    @override
    @abstractmethod
    def transform_entities(self, entities: SensorDataType) -> Collection[Entity]:
        raise NotImplementedError()

    @override
    def publish_entities(
        self, entities: SensorDataType, *args, **kwargs
    ) -> Collection[Entity]:
        # Skip empty data
        if (
            entities is None
            or (isinstance(entities, dict) and not entities)
            or (isinstance(entities, (list, tuple)) and not entities)
        ):
            return []

        return super().publish_entities(entities, *args, **kwargs)  # type: ignore

    @abstractmethod
    @action
    def get_measurement(self, *args, **kwargs) -> SensorDataType:
        """
        Implemented by the subclasses.

        :returns: Either a raw scalar::

            output = 273.16

        or a name-value dictionary with the values that have been read::

            output = {
                "temperature": 21.5,
                "humidity": 41.0
            }

        or a list of values::

            output = [
                0.01,
                0.34,
                0.53,
                ...
            ]

        """
        raise NotImplementedError()

    @action
    def get_data(self, *args, **kwargs):
        """
        (Deprecated) alias for :meth:`.get_measurement`
        """
        return self.get_measurement(*args, **kwargs)

    @action
    def status(self, *_, **__) -> Optional[SensorDataType]:
        """
        Returns the latest read values and publishes the
        :class:`platypush.message.event.entities.EntityUpdateEvent` events if
        required.
        """
        if self._last_measurement is not None:
            self.publish_entities(self._last_measurement)
        return self._last_measurement

    @override
    def main(self):
        sleep_retry_secs = 1  # Exponential back-off

        while not self.should_stop():
            try:
                new_data: SensorDataType = self.get_measurement().output  # type: ignore
                # Reset the exponential back-off retry counter in case of success
                sleep_retry_secs = 1
            except Exception as e:
                self.logger.warning(
                    'Could not update the status: %s. Next retry in %d seconds',
                    e,
                    sleep_retry_secs,
                )
                self.logger.exception(e)
                self.wait_stop(sleep_retry_secs)
                sleep_retry_secs = min(
                    sleep_retry_secs * 2,
                    self._max_retry_secs,
                )
                continue

            new_data = self._filter_enabled_sensors(new_data)
            is_event_processed = self._process_sensor_events(
                self._last_measurement, new_data
            )
            if is_event_processed:
                self._update_last_measurement(new_data)
            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
