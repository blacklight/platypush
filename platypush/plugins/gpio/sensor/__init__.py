from platypush.plugins import Plugin


class GpioSensorPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_measurement(self, *args, **kwargs):
        raise NotImplementedError('get_measurement should be implemented in a derived class')


# vim:sw=4:ts=4:et:

