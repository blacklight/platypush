from .. import Plugin

class MusicPlugin(Plugin):
    def run(self, args):
        if 'play' in args and self.status()['state'] != 'play':
            self.play()
        elif 'pause' in args and self.status()['state'] != 'pause':
            self.pause()
        elif 'stop' in args:
            self.stop()

        return self.status()

    def play(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

