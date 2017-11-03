from .. import Plugin

class SwitchPlugin(Plugin):
    def run(self, args):
        if 'on' in args and args['on']:
            self.on(args)
        elif 'off' in args and args['off']:
            self.off(args)
        elif 'toggle' in args and args['toggle']:
            self.toggle(args)

        return self.status()

    def on(self, args):
        raise NotImplementedError()

    def off(self, args):
        raise NotImplementedError()

    def toggle(self, args):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

