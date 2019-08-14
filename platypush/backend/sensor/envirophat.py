from platypush.backend.sensor import SensorBackend


class SensorEnvirophatBackend(SensorBackend):
    """
    Backend to poll analog sensor values from an enviroPHAT sensor pHAT
    (https://shop.pimoroni.com/products/enviro-phat)

    Requires:

        * ``envirophat`` (``pip install envirophat``)
    """

    def __init__(self, temperature=True, pressure=True, altitude=True, luminosity=True,
                 analog=True, accelerometer=True, magnetometer=True, qnh=1020, **kwargs):
        """
        :param temperature: Enable temperature sensor polling
        :param pressure: Enable pressure sensor polling
        :param altitude: Enable altitude sensor polling
        :param luminosity: Enable luminosity sensor polling
        :param analog: Enable analog sensors polling
        :param accelerometer: Enable accelerometer polling
        :param magnetometer: Enable magnetometer polling
        :param qnh: Base reference for your sea level pressure (for altitude sensor)
        """

        enabled_sensors = {
            'temperature': temperature,
            'pressure': pressure,
            'altitude': altitude,
            'luminosity': luminosity,
            'analog': analog,
            'accelerometer': accelerometer,
            'magnetometer': magnetometer,
        }

        super().__init__(plugin='gpio.sensor.envirophat',
                         plugin_args={'qnh': qnh},
                         enabled_sensors=enabled_sensors, **kwargs)


# vim:sw=4:ts=4:et:
