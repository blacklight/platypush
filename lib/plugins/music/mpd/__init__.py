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

    def status(self):
        return self.client.status()

# vim:sw=4:ts=4:et:

