from .. import Plugin

class LightPlugin(Plugin):
    """
    Abstract plugin to interface your logic with lights/bulbs.
    """

    def on(self):
        """ Turn the light on """
        raise NotImplementedError()

    def off(self):
        """ Turn the light off """
        raise NotImplementedError()

    def toggle(self):
        """ Toggle the light status (on/off) """
        raise NotImplementedError()

    def status(self):
        """ Get the light status """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

