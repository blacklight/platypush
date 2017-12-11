from .. import Plugin

class LightPlugin(Plugin):
    def on(self):
        raise NotImplementedError()

    def off(self):
        raise NotImplementedError()

    def toggle(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

