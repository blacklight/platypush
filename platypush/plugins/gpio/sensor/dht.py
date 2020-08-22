from typing import Optional, Dict

from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorDhtPlugin(GpioSensorPlugin):
    """
    Plugin to interact with a DHT11/DHT22/AM2302 temperature/humidity sensor through GPIO.

    Requires:

        * ``Adafruit_Python_DHT`` (``pip install git+https://github.com/adafruit/Adafruit_Python_DHT.git``)

    """

    def __init__(self, sensor_type: str, pin: int, retries: int = 5,
                 retry_seconds: int = 2, **kwargs):
        """
        :param sensor_type: Type of sensor to be used (supported types: DHT11, DHT22, AM2302).
        :param pin: GPIO PIN where the sensor is connected.
        :param retries: Number of retries in case of failed read (default: 5).
        :param retry_seconds: Number of seconds to wait between retries (default: 2).
        """
        super().__init__(**kwargs)
        self.sensor_type = self._get_sensor_type(sensor_type)
        self.pin = pin
        self.retries = retries
        self.retry_seconds = retry_seconds

    @staticmethod
    def _get_sensor_type(sensor_type: str) -> int:
        import Adafruit_DHT
        sensor_type = sensor_type.upper()
        assert hasattr(Adafruit_DHT, sensor_type), \
            'Unknown sensor type: {}. Supported types: DHT11, DHT22, AM2302'.format(sensor_type)

        return getattr(Adafruit_DHT, sensor_type)

    @action
    def read(self, sensor_type: Optional[str] = None, pin: Optional[int] = None,
             retries: Optional[int] = None, retry_seconds: Optional[int] = None,
             **kwargs) -> Dict[str, float]:
        """
        Read data from the sensor.

        :param sensor_type: Default ``sensor_type`` override.
        :param pin: Default ``pin`` override.
        :param retries: Default ``retries`` override.
        :param retry_seconds: Default ``retry_seconds`` override.
        :return: A mapping with the measured temperature and humidity. Example:

            .. code-block:: json

                {
                    "humidity": 30.0,
                    "temperature": 25.5
                }

        """
        import Adafruit_DHT
        sensor_type = self._get_sensor_type(sensor_type) if sensor_type else self.sensor_type
        pin = pin or self.pin
        retries = retries or self.retries
        retry_seconds = retry_seconds or self.retry_seconds
        humidity, temperature = Adafruit_DHT.read_retry(sensor=sensor_type,
            pin=pin, retries=retries, delay_seconds=retry_seconds)

        return {
            'humidity': humidity,
            'temperature': temperature,
        }

    @action
    def get_measurement(self) -> Dict[str, float]:
        """
        Get data from the sensor.

        :return: A mapping with the measured temperature and humidity. Example:

            .. code-block:: json

                {
                    "humidity": 30.0,
                    "temperature": 25.5
                }

        """
        return self.read()



# vim:sw=4:ts=4:et:
