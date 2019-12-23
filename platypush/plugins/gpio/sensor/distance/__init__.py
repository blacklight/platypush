import threading
import time

from typing import Optional

from platypush.context import get_bus
from platypush.message.event.distance import DistanceSensorEvent
from platypush.plugins import action
from platypush.plugins.gpio import GpioPlugin
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDistancePlugin(GpioPlugin, GpioSensorPlugin):
    """
    You can use this plugin to interact with a distance sensor on your Raspberry
    Pi (tested with a HC-SR04 ultrasound sensor).

    Requires:

        * ``RPi.GPIO`` (``pip install RPi.GPIO``)

    Triggers:

        * :class:`platypush.message.event.distance.DistanceSensorEvent` when a new distance measurement is available

    """

    def __init__(self, trigger_pin: int, echo_pin: int, measurement_interval: float = 0.15,
                 timeout: float = 2.0, warmup_time: float = 2.0, *args, **kwargs):
        """
        :param trigger_pin: GPIO PIN where you connected your sensor trigger PIN (the one that triggers the
            sensor to perform a measurement).

        :param echo_pin: GPIO PIN where you connected your sensor echo PIN (the one that will listen for the
            signal to bounce back and therefore trigger the distance calculation).

        :param measurement_interval: When running in continuous mode (see
            :func:`platypush.plugins.gpio.sensor.distance.GpioSensorDistancePlugin.start_measurement`) this parameter
            indicates how long should be waited between two measurements (default: 0.15 seconds)
        :param timeout: The echo-wait will terminate and the plugin will return null if no echo has been
            received after this time (default: 1 second).

        :param warmup_time: Number of seconds that should be waited on plugin instantiation
            for the sensor to be ready (default: 2 seconds).
        """

        GpioPlugin.__init__(self, pins={'trigger': trigger_pin, 'echo': echo_pin, }, *args, **kwargs)

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.measurement_interval = measurement_interval
        self.timeout = timeout
        self.warmup_time = warmup_time
        self._measurement_thread = None
        self._measurement_thread_lock = threading.RLock()
        self._measurement_thread_can_run = False
        self._init_board()

    def _init_board(self):
        import RPi.GPIO as GPIO

        with self._init_lock:
            if self._initialized:
                return

            GpioPlugin._init_board(self)
            self._initialized = False

            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trigger_pin, GPIO.LOW)

            self.logger.info('Waiting {} seconds for the sensor to be ready'.format(self.warmup_time))
            time.sleep(self.warmup_time)
            self.logger.info('Sensor ready')
            self._initialized = True

    def _get_data(self):
        import RPi.GPIO as GPIO

        pulse_start = pulse_on = time.time()

        self._init_board()
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)  # 1 us pulse to trigger echo measurement
        GPIO.output(self.trigger_pin, GPIO.LOW)

        while GPIO.input(self.echo_pin) == 0:
            pulse_on = time.time()
            if pulse_on - pulse_start > self.timeout:
                raise TimeoutError('Distance sensor echo timeout after {} seconds: 0'.
                                   format(self.timeout))

        pulse_start = pulse_on
        pulse_end = pulse_off = time.time()

        while GPIO.input(self.echo_pin) == 1:
            pulse_off = time.time()
            if pulse_off - pulse_end > self.timeout:
                raise TimeoutError('Distance sensor echo timeout after {} seconds: 1'.
                                   format(self.timeout))

        pulse_end = pulse_off
        pulse_duration = pulse_end - pulse_start

        # s = vt where v = 1/2 * avg speed of sound in mm/s
        return round(pulse_duration * 171500.0, 2)

    @action
    def get_measurement(self):
        """
        Extends :func:`.GpioSensorPlugin.get_measurement`

        :returns: Distance measurement as a scalar (in mm):
        """

        try:
            distance = self._get_data()
            bus = get_bus()
            bus.post(DistanceSensorEvent(distance=distance, unit='mm'))
            return distance
        except TimeoutError as e:
            self.logger.warning(str(e))
            return
        except Exception as e:
            self.close()
            raise e

    @action
    def close(self):
        return self.cleanup()

    def __enter__(self):
        self._init_board()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_measurement_thread(self, duration: float):
        def _thread():
            with self:
                self.logger.info('Started distance measurement thread')
                start_time = time.time()

                try:
                    while self._measurement_thread_can_run and (
                            not duration or time.time() - start_time <= duration):
                        self.get_measurement()
                        if self.measurement_interval:
                            time.sleep(self.measurement_interval)
                finally:
                    self._measurement_thread = None

        return _thread

    def _is_measurement_thread_running(self):
        with self._measurement_thread_lock:
            return self._measurement_thread is not None

    @action
    def start_measurement(self, duration: Optional[float] = None):
        """
        Start the measurement thread. It will trigger :class:`platypush.message.event.distance.DistanceSensorEvent`
        events when new measurements are available.

        :param duration: If set, then the thread will run for the specified amount of seconds (default: None)
        """
        with self._measurement_thread_lock:
            if self._is_measurement_thread_running():
                self.logger.warning('A measurement thread is already running')
                return

            thread_func = self._get_measurement_thread(duration=duration)
            self._measurement_thread = threading.Thread(target=thread_func)
            self._measurement_thread_can_run = True
            self._measurement_thread.start()

    @action
    def stop_measurement(self):
        """
        Stop the running measurement thread.
        """
        with self._measurement_thread_lock:
            if not self._is_measurement_thread_running():
                self.logger.warning('No measurement thread is running')
                return

            self._measurement_thread_can_run = False
            self.logger.info('Waiting for the measurement thread to end')

            if self._measurement_thread:
                self._measurement_thread.join(timeout=self.timeout)

            self.logger.info('Measurement thread terminated')


# vim:sw=4:ts=4:et:
