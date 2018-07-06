from platypush.plugins import Plugin, action


class GpioSensorPlugin(Plugin):
    """
    GPIO sensor abstract plugin. Any plugin that interacts with sensor via GPIO
    should implement this class (and the get_measurement() method)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def get_measurement(self, *args, **kwargs):
        """
        Implemented by the subclasses.

        :returns: Either a raw scalar:

            ``output = 273.16``

        or a name-value dictionary with the values that have been read::

            output = {
                "temperature": 21.5,
                "humidity": 41.0
            }
        """
        raise NotImplementedError('get_measurement should be implemented in a derived class')

    @action
    def get_data(self, *args, **kwargs):
        """
        Alias for ``get_measurement``
        """

        return self.get_measurement(*args, **kwargs).output

# vim:sw=4:ts=4:et:

