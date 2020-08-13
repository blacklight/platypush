import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.sensor import SensorDataChangeEvent, \
    SensorDataAboveThresholdEvent, SensorDataBelowThresholdEvent


class SensorBackend(Backend):
    """
    Abstract backend for polling sensors.

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataChangeEvent` if the measurements of a sensor have changed
        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent` if the measurements of a sensor have
            gone above a configured threshold
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent` if the measurements of a sensor have
            gone below a configured threshold
    """

    default_tolerance = 1e-7

    def __init__(self, plugin=None, plugin_args=None, thresholds=None, tolerance=default_tolerance, poll_seconds=None,
                 enabled_sensors=None, **kwargs):
        """
        :param plugin: If set, then this plugin instance, referenced by plugin id, will be polled
            through ``get_plugin()``. Example: ``'gpio.sensor.bme280'`` or ``'gpio.sensor.envirophat'``.
        :type plugin: str

        :param plugin_args: If plugin is set and its ``get_measurement()`` method accepts optional arguments, then you
            can pass those arguments through ``plugin_args``.
        :type plugin_args: dict

        :param thresholds: Thresholds can be either a scalar value or a dictionary (e.g. ``{"temperature": 20.0}``).
            Sensor threshold events will be fired when measurements get above or below these values.
            Set it as a scalar if your get_measurement() code returns a scalar, as a dictionary if it returns a
            dictionary of values.  For instance, if your sensor code returns both humidity and temperature in a format
            like ``{'humidity':60.0, 'temperature': 25.0}``, you'll want to set up a threshold on temperature with a
            syntax like ``{'temperature':20.0}`` to trigger events when the temperature goes above/below 20 degrees.

        :param tolerance: If set, then the sensor change events will be triggered only if the difference between
            the new value and the previous value is higher than the specified tolerance. Example::

                {
                    "temperature": 0.01,  # Tolerance on the 2nd decimal digit
                    "humidity": 0.1       # Tolerance on the 1st decimal digit
                }

        :type tolerance: dict or float

        :param poll_seconds: If set, the thread will wait for the specified number of seconds between a read and the
            next one.
        :type poll_seconds: float

        :param enabled_sensors: If ``get_measurement()`` returns data in dict form, then ``enabled_sensors`` selects
            which keys should be taken into account when monitoring for new events (e.g. "temperature" or "humidity").
        :type enabled_sensors: dict (in the form ``name -> [True/False]``), set or list
        """

        super().__init__(**kwargs)

        self.data = None
        self.plugin = plugin
        self.plugin_args = plugin_args or {}
        self.thresholds = thresholds
        self.tolerance = tolerance
        self.poll_seconds = poll_seconds

        if isinstance(enabled_sensors, list):
            enabled_sensors = set(enabled_sensors)
        if isinstance(enabled_sensors, set):
            enabled_sensors = {k: True for k in enabled_sensors}

        self.enabled_sensors = enabled_sensors or {}

    def get_measurement(self):
        """
        Wrapper around ``plugin.get_measurement()`` that can filter events on specified enabled sensors data or on
        specified tolerance values. It can be overridden by derived classes.
        """
        if not self.plugin:
            raise NotImplementedError('No plugin specified')

        reload = False
        success = False
        data = None

        while not success:
            try:
                plugin = get_plugin(self.plugin, reload=reload)
                data = plugin.get_data(**self.plugin_args).output
                if reload:
                    self.logger.info('Backend successfully restored')

                success = True
            except Exception as e:
                self.logger.warning('Unexpected exception while getting data: {}'.format(str(e)))
                self.logger.exception(e)
                reload = True
                time.sleep(5)

            if self.enabled_sensors and data is not None:
                data = {
                    sensor: data[sensor]
                    for sensor, enabled in self.enabled_sensors.items()
                    if enabled and sensor in data
                }

        return data

    @staticmethod
    def _get_value(value):
        if isinstance(value, float) or isinstance(value, int) or isinstance(value, bool):
            return value
        return float(value)

    def get_new_data(self, new_data):
        if self.data is None or new_data is None:
            return new_data

        # noinspection PyBroadException
        try:
            # Scalar data case
            new_data = self._get_value(new_data)
            return new_data if abs(new_data - self.data) >= self.tolerance else None
        except:
            # If it's not a scalar then it should be a dict
            assert isinstance(new_data, dict), 'Invalid type {} received for sensor data'.format(type(new_data))

        ret = {}
        for k, v in new_data.items():
            if (v is None and self.data.get(k) is not None) \
                    or k not in self.data \
                    or self.tolerance is None:
                ret[k] = v
                continue

            if v is None:
                continue

            tolerance = None
            is_nan = False
            old_v = None

            try:
                v = self._get_value(v)
                old_v = self._get_value(self.data.get(k))
            except (TypeError, ValueError):
                is_nan = True

            if not is_nan:
                if isinstance(self.tolerance, dict):
                    tolerance = float(self.tolerance.get(k, self.default_tolerance))
                else:
                    try:
                        tolerance = float(self.tolerance)
                    except (TypeError, ValueError):
                        pass

                if tolerance is None or abs(v - old_v) >= tolerance:
                    ret[k] = v
            elif k not in self.data or self.data[k] != v:
                ret[k] = v

        return ret

    def on_stop(self):
        super().on_stop()
        if not self.plugin:
            return

        plugin = get_plugin(self.plugin)
        if plugin and hasattr(plugin, 'close'):
            plugin.close()

    def process_data(self, data, new_data):
        if new_data:
            self.bus.post(SensorDataChangeEvent(data=new_data, source=self.plugin or self.__class__.__name__))

    def run(self):
        super().run()
        self.logger.info('Initialized {} sensor backend'.format(self.__class__.__name__))

        while not self.should_stop():
            try:
                data = self.get_measurement()
                new_data = self.get_new_data(data)
                self.process_data(data, new_data)

                data_below_threshold = {}
                data_above_threshold = {}

                if self.thresholds:
                    if isinstance(self.thresholds, dict) and isinstance(data, dict):
                        for (measure, thresholds) in self.thresholds.items():
                            if measure not in data:
                                continue

                            if not isinstance(thresholds, list):
                                thresholds = [thresholds]

                            for threshold in thresholds:
                                if data[measure] > threshold and (self.data is None or (
                                        measure in self.data and self.data[measure] <= threshold)):
                                    data_above_threshold[measure] = data[measure]
                                elif data[measure] < threshold and (self.data is None or (
                                        measure in self.data and self.data[measure] >= threshold)):
                                    data_below_threshold[measure] = data[measure]

                if data_below_threshold:
                    self.bus.post(SensorDataBelowThresholdEvent(data=data_below_threshold))

                if data_above_threshold:
                    self.bus.post(SensorDataAboveThresholdEvent(data=data_above_threshold))

                self.data = data

                if new_data:
                    if isinstance(new_data, dict):
                        for k, v in new_data.items():
                            self.data[k] = v
                    else:
                        self.data = new_data
            except Exception as e:
                self.logger.exception(e)

            if self.poll_seconds:
                time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:
