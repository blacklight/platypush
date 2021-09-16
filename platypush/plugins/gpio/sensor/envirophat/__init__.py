from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorEnvirophatPlugin(GpioSensorPlugin):
    """
    Plugin to interact with a `Pimoroni enviropHAT <https://shop.pimoroni.com/products/enviro-phat>`_ device.
    You can use an enviropHAT device to read e.g. temperature, pressure, altitude, accelerometer, magnetometer and
    luminosity data, plus control the status of its RGB LEDs.

    Requires:

        * ``envirophat`` (``pip install envirophat``)
    """

    @action
    def get_measurement(self, qnh=1020.0):
        """
        :param: qnh: Local value for atmospheric pressure adjusted to sea level (default: 1020)
        :type qnh: float

        :returns: dict. Example:

        .. code-block:: python

           output = {
               "temperature": 21.0,   # Celsius
               "pressure": 101555.08, # pascals
               "altitude": 10,        # meters
               "luminosity": 426,     # lumens

               # Measurements from the custom analog channels
               "analog": [0.513, 0.519, 0.531, 0.528],

               "accelerometer": {
                   "x": -0.000915,
                   "y": 0.0760,
                   "z": 1.026733
               },
               "magnetometer": {
                   "x": -2297,
                   "y": 1226,
                   "z": -7023
               },
           }

        """

        import envirophat

        ret = {}
        weather = envirophat.weather
        light = envirophat.light
        accelerometer = envirophat.motion.accelerometer()
        magnetometer = envirophat.motion.magnetometer()
        leds = envirophat.leds
        analog = envirophat.analog

        weather.update()

        ret['temperature'] = weather.temperature()
        ret['pressure'] = weather.pressure()
        ret['altitude'] = weather.altitude(qnh=qnh)
        ret['luminosity'] = light.light()
        ret['accelerometer'] = {v: getattr(accelerometer, v) for v in ['x', 'y', 'z']}
        ret['magnetometer'] = {v: getattr(magnetometer, v) for v in ['x', 'y', 'z']}
        ret['analog'] = list(analog.read_all())
        ret['leds'] = leds.is_on()

        return ret


# vim:sw=4:ts=4:et:
