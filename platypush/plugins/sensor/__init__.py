from platypush.plugins import Plugin, action


class SensorPlugin(Plugin):
    """
    Sensor abstract plugin. Any plugin that interacts with sensors
    should implement this class (and the get_measurement() method)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        or a list of values::

            [
                0.01,
                0.34,
                0.53,
                ...
            ]

        """
        raise NotImplementedError('get_measurement should be implemented in a derived class')

    @action
    def get_data(self, *args, **kwargs):
        """
        Alias for ``get_measurement``
        """

        return self.get_measurement(*args, **kwargs).output

    @action
    def close(self):
        pass


# vim:sw=4:ts=4:et:
