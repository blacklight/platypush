import mpd

from .. import MusicPlugin

class MusicMpdPlugin(MusicPlugin):
    def _init(self):
        self.client = mpd.MPDClient(use_unicode=True)
        self.client.connect(self.config['host'], self.config['port'])

    def play(self):
        self.client.play()

    def pause(self):
        self.client.pause()

    def stop(self):
        self.client.stop()

    def next(self):
        self.client.next()

    def previous(self):
        self.client.previous()

    def setvol(self, vol):
        self.client.setvol(vol)

    def add(self, content):
        self.client.add(content)

    def playlistadd(self, playlist):
        self.client.playlistadd(playlist)

    def clear(self):
        self.client.clear()

    def status(self):
        return self.client.status()

# vim:sw=4:ts=4:et:

