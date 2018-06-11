import time

from platypush.backend import Backend
from platypush.message.event.sensor import SensorDataChangeEvent, \
    SensorDataAboveThresholdEvent, SensorDataBelowThresholdEvent


class SensorBackend(Backend):
    def __init__(self, thresholds=None, poll_seconds=None, *args, **kwargs):
        """
        Params:
            -- thresholds: Thresholds can be either a scalr value or a dictionary.

            If set, SensorDataAboveThresholdEvent and SensorDataBelowThresholdEvent
            events will be triggered whenever the measurement goes above or
            below that value.

            Set it as a scalar if your get_measurement() code returns a scalar,
            as a dictionary if it returns a dictionary of values.

            For instance, if your sensor code returns both humidity and
            temperature in a format like {'humidity':60.0, 'temperature': 25.0},
            you'll want to set up a threshold on temperature with a syntax like
            {'temperature':20.0}

            -- poll_seconds: If set, the thread will wait for the specificed
                number of seconds between a read and the next one.
        """

        super().__init__(**kwargs)

        self.data = None
        self.thresholds = thresholds
        self.poll_seconds = poll_seconds

    def get_measurement(self):
        raise NotImplementedError('To be implemented in a derived class')

    def run(self):
        super().run()
        self.logger.info('Initialized {} sensor backend'.format(self.__class__.__name__))

        while not self.should_stop():
            new_data = self.get_measurement()
            if self.data is None or self.data != new_data:
                self.bus.post(SensorDataChangeEvent(data=new_data))

            if self.thresholds:
                if isinstance(self.thresholds, dict) and isinstance(new_data, dict):
                    for (measure, threshold) in self.thresholds.items():
                        if measure not in new_data:
                            continue

                        if new_data[measure] > threshold and (self.data is None or (
                                measure in self.data and self.data[measure] <= threshold)):
                            self.bus.post(SensorDataAboveThresholdEvent(data=new_data))
                        elif new_data[measure] < threshold and (self.data is None or (
                                measure in self.data and self.data[measure] >= threshold)):
                            self.bus.post(SensorDataBelowThresholdEvent(data=new_data))
                else:
                    if new_data > threshold and (self.data is None or self.data <= threshold):
                        self.bus.post(SensorDataAboveThresholdEvent(data=new_data))
                    elif new_data < threshold and (self.data is None or self.data >= threshold):
                        self.bus.post(SensorDataBelowThresholdEvent(data=new_data))

            self.data = new_data

            if self.poll_seconds:
                time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

