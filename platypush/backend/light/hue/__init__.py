import warnings

from platypush.backend import Backend


class LightHueBackend(Backend):
    """
    **DEPRECATED**

    The polling logic of this backend has been moved to the ``light.hue`` plugin itself.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            'The light.hue backend is deprecated. All of its logic '
            'has been moved to the light.hue plugin itself.'
        )

    def run(self):
        super().run()
        self.logger.info('Stopped Hue lights backend')


# vim:sw=4:ts=4:et:
