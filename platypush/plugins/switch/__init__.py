from .. import Plugin

class SwitchPlugin(Plugin):
    def on(self, args):
        raise NotImplementedError()

    def off(self, args):
        raise NotImplementedError()

    def toggle(self, args):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

