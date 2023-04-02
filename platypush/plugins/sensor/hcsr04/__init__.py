from collections.abc import Collection
import time

from typing import List, Optional, Union
from typing_extensions import override
import warnings

from platypush.context import get_bus
from platypush.entities.distance import DistanceSensor
from platypush.message.event.distance import DistanceSensorEvent
from platypush.plugins import action
from platypush.plugins.gpio import GpioPlugin
from platypush.plugins.sensor import SensorPlugin


class SensorHcsr04Plugin(GpioPlugin, SensorPlugin):
    """
    You can use this plugin to interact with a distance sensor on your
    Raspberry Pi. It's been tested with a `HC-SR04 ultrasound sensor
    <https://www.sparkfun.com/products/15569>`_, but it should be compatible
    with any GPIO-compatible sensor that relies on the same trigger-and-echo
    principle.

    Requires:

        * ``RPi.GPIO`` (``pip install RPi.GPIO``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`
        * :class:`platypush.message.event.distance.DistanceSensorEvent` when a
          new distance measurement is available (legacy event)

    """

    def __init__(
        self,
        trigger_pin: int,
        echo_pin: int,
        poll_interval: float = 0.25,
        timeout: float = 2.0,
        warmup_time: float = 2.0,
        *args,
        **kwargs,
    ):
        """
        :param trigger_pin: GPIO PIN where you connected your sensor trigger
            PIN (the one that triggers the sensor to perform a measurement).
        :param echo_pin: GPIO PIN where you connected your sensor echo PIN (the
            one that will listen for the signal to bounce back and therefore
            trigger the distance calculation).
        :param timeout: The echo-wait will terminate and the plugin will return
            null if no echo has been received after this time (default: 1
            second).
        :param warmup_time: Number of seconds that should be waited on plugin
            instantiation for the sensor to be ready (default: 2 seconds).
        """

        measurement_interval = kwargs.pop('measurement_interval', None)
        if measurement_interval is not None:
            warnings.warn(
                'measurement_interval is deprecated, use poll_interval instead',
                DeprecationWarning,
                stacklevel=2,
            )
            poll_interval = measurement_interval

        SensorPlugin.__init__(self, poll_interval=poll_interval, *args, **kwargs)
        GpioPlugin.__init__(
            self,
            pins={
                'trigger': trigger_pin,
                'echo': echo_pin,
            },
            *args,
            **kwargs,
        )

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.timeout = timeout
        self.warmup_time = warmup_time
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

            self.logger.info(
                'Waiting {} seconds for the sensor to be ready'.format(self.warmup_time)
            )
            self.wait_stop(self.warmup_time)
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
                raise TimeoutError(
                    'Distance sensor echo timeout after {} seconds: 0'.format(
                        self.timeout
                    )
                )

        pulse_start = pulse_on
        pulse_end = pulse_off = time.time()

        while GPIO.input(self.echo_pin) == 1:
            pulse_off = time.time()
            if pulse_off - pulse_end > self.timeout:
                raise TimeoutError(
                    'Distance sensor echo timeout after {} seconds: 1'.format(
                        self.timeout
                    )
                )

        pulse_end = pulse_off
        pulse_duration = pulse_end - pulse_start

        # s = vt where v = 1/2 * avg speed of sound in mm/s
        return round(pulse_duration * 171500.0, 2)

    @override
    @action
    def get_measurement(self, *_, **__) -> Optional[float]:
        """
        :returns: Distance measurement as a scalar (in mm):
        """

        try:
            distance = self._get_data()
            bus = get_bus()
            bus.post(DistanceSensorEvent(distance=distance, unit='mm'))
            return distance
        except TimeoutError as e:
            self.logger.warning(f'Read timeout: {e}')
            return None
        except Exception as e:
            self.cleanup()
            raise e

    @override
    def transform_entities(
        self, entities: Union[Optional[float], Collection[Optional[float]]]
    ) -> List[DistanceSensor]:
        value = (
            entities[0]
            if isinstance(entities, (list, tuple)) and len(entities)
            else entities
        )

        if value is None:
            return []

        return [
            DistanceSensor(
                id='hcsr04',
                name='HC-SR04 Distance Sensor',
                value=value,
                unit='mm',
            )
        ]

    @action
    def stop(self):
        super().stop()
        self.cleanup()


# vim:sw=4:ts=4:et:
