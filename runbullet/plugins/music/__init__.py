from .. import Plugin

class MusicPlugin(Plugin):
    def play(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def next(self):
        raise NotImplementedError()

    def previous(self):
        raise NotImplementedError()

    def setvol(self, vol):
        raise NotImplementedError()

    def add(self, content):
        raise NotImplementedError()

    def playlistadd(self, playlist):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

