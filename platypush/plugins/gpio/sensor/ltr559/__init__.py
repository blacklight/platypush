from platypush.plugins import action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class GpioSensorLtr559Plugin(GpioSensorPlugin):
    """
    Plugin to interact with an `LTR559 <https://shop.pimoroni.com/products/ltr-559-light-proximity-sensor-breakout>`_
    light and proximity sensor

    Requires:

        * ``ltr559`` (``pip install ltr559``)
    """

    def __init__(self, **kwargs):
        import ltr559
        super().__init__(**kwargs)
        self.ltr = ltr559.LTR559()

    # noinspection PyUnresolvedReferences
    @action
    def get_measurement(self):
        """
        :returns: dict. Example:

          .. code-block:: python

             output = {
                 "light": 109.3543,     # Lux
                 "proximity": 103       # The higher the value, the nearest the object, within a ~5cm range
             }

        """
        self.ltr.update_sensor()
        return {
            'light': self.ltr.get_lux(),
            'proximity': self.ltr.get_proximity(),
        }


# vim:sw=4:ts=4:et:
