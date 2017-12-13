import mpd

from platypush.message.response import Response

from .. import MusicPlugin

class MusicMpdPlugin(MusicPlugin):
    def _init(self):
        self.client = mpd.MPDClient(use_unicode=True)
        self.client.connect(self.config['host'], self.config['port'])

    def _exec(self, method, *args, **kwargs):
        getattr(self.client, method)(*args, **kwargs)
        return self.status()

    def play(self):
        return self._exec('play')

    def pause(self):
        return self._exec('pause')

    def stop(self):
        return self._exec('stop')

    def next(self):
        return self._exec('next')

    def previous(self):
        return self._exec('previous')

    def setvol(self, vol):
        return self._exec('setvol', vol)

    def add(self, content):
        return self._exec('add', content)

    def playlistadd(self, playlist):
        return self._exec('playlistadd', playlist)

    def clear(self):
        return self._exec('clear')

    def status(self):
        return Response(output=self.client.status())

# vim:sw=4:ts=4:et:

