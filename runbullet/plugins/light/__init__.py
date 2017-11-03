from .. import Plugin

class LightPlugin(Plugin):
    def run(self, args):
        if 'on' in args and args['on']:
            self.on()
        elif 'off' in args and args['off']:
            self.off()
        elif 'toggle' in args and args['toggle']:
            self.toggle()

        return self.status()

    def on(self):
        raise NotImplementedError()

    def off(self):
        raise NotImplementedError()

    def toggle(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

