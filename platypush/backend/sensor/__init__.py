import time

from platypush.backend import Backend
from platypush.message.event.sensor import SensorDataChangeEvent, \
    SensorDataAboveThresholdEvent, SensorDataBelowThresholdEvent


class SensorBackend(Backend):
    """
    Abstract backend for polling sensors.

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have gone below a configured threshold
    """

    def __init__(self, thresholds=None, poll_seconds=None, *args, **kwargs):
        """
        :param thresholds: Thresholds can be either a scalar value or a dictionary (e.g. ``{"temperature": 20.0}``). Sensor threshold events will be fired when measurements get above or below these values.  Set it as a scalar if your get_measurement() code returns a scalar, as a dictionary if it returns a dictionary of values.

        For instance, if your sensor code returns both humidity and
        temperature in a format like ``{'humidity':60.0, 'temperature': 25.0}``,
        you'll want to set up a threshold on temperature with a syntax like
        ``{'temperature':20.0}`` to trigger events when the temperature goes
        above/below 20 degrees.

        :param poll_seconds: If set, the thread will wait for the specificed number of seconds between a read and the next one.
        :type poll_seconds: float
        """

        super().__init__(**kwargs)

        self.data = None
        self.thresholds = thresholds
        self.poll_seconds = poll_seconds

    def get_measurement(self):
        """ To be implemented in the derived classes """
        raise NotImplementedError('To be implemented in a derived class')

    def run(self):
        super().run()
        self.logger.info('Initialized {} sensor backend'.format(self.__class__.__name__))

        while not self.should_stop():
            new_data = self.get_measurement()
            if self.data is None or self.data != new_data:
                self.bus.post(SensorDataChangeEvent(data=new_data))

            data_below_threshold = {}
            data_above_threshold = {}

            if self.thresholds:
                if isinstance(self.thresholds, dict) and isinstance(new_data, dict):
                    for (measure, threshold) in self.thresholds.items():
                        if measure not in new_data:
                            continue

                        if new_data[measure] > threshold and (self.data is None or (
                                measure in self.data and self.data[measure] <= threshold)):
                            data_above_threshold[measure] = new_data[measure]
                        elif new_data[measure] < threshold and (self.data is None or (
                                measure in self.data and self.data[measure] >= threshold)):
                            data_below_threshold[measure] = new_data[measure]

            if data_below_threshold:
                self.bus.post(SensorDataBelowThresholdEvent(data=data_below_threshold))

            if data_above_threshold:
                self.bus.post(SensorDataAboveThresholdEvent(data=data_above_threshold))


            self.data = new_data

            if self.poll_seconds:
                time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

