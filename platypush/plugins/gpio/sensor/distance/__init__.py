import time

from platypush.plugins import action
from platypush.plugins.gpio import GpioPlugin
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDistancePlugin(GpioPlugin, GpioSensorPlugin):
    """
    You can use this plugin to interact with a distance sensor on your Raspberry
    Pi (tested with a HC-SR04 ultrasound sensor).

    Requires:

        * ``RPi.GPIO`` (``pip install RPi.GPIO``)
    """

    def __init__(self, trigger_pin: int, echo_pin: int,
                 timeout: float = 1.0, warmup_time: float = 2.0, *args, **kwargs):
        """
        :param trigger_pin: GPIO PIN where you connected your sensor trigger PIN (the one that triggers the
            sensor to perform a measurement).

        :param echo_pin: GPIO PIN where you connected your sensor echo PIN (the one that will listen for the
            signal to bounce back and therefore trigger the distance calculation).

        :param timeout: The echo-wait will terminate and the plugin will return null if no echo has been
            received after this time (default: 1 second).

        :param warmup_time: Number of seconds that should be waited on plugin instantiation
            for the sensor to be ready (default: 2 seconds).
        """

        GpioPlugin.__init__(self, *args, **kwargs)
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.timeout = timeout
        self.warmup_time = warmup_time
        self._initialized = False
        self._init_gpio()

    def _init_gpio(self):
        if self._initialized:
            return

        import RPi.GPIO as GPIO
        GPIO.setmode(self.mode)
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

        self._init_gpio()
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
            return self._get_data()
        except TimeoutError as e:
            self.logger.warning(str(e))
            return
        except Exception as e:
            self.close()
            raise e

    @action
    def close(self):
        import RPi.GPIO as GPIO
        if self._initialized:
            GPIO.cleanup()
            self._initialized = False

    def __enter__(self):
        self._init_gpio()

    def __exit__(self):
        self.close()


# vim:sw=4:ts=4:et:
