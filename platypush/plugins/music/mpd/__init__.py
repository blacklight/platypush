import mpd

from platypush.message.response import Response

from .. import MusicPlugin

class MusicMpdPlugin(MusicPlugin):
    def __init__(self, host, port):
        """
        Constructor
        Params:
            host -- MPD host
            port -- MPD port
        """

        self.host = host
        self.port = port
        self.client = mpd.MPDClient(use_unicode=True)
        self.client.connect(self.host, self.port)

    def _exec(self, method, *args, **kwargs):
        getattr(self.client, method)(*args, **kwargs)
        return self.status()

    def play(self):
        return self._exec('play')

    def pause(self):
        status = self.status().output['state']
        if status == 'play': return self._exec('pause')
        else: return self._exec('play')

    def stop(self):
        return self._exec('stop')

    def next(self):
        return self._exec('next')

    def previous(self):
        return self._exec('previous')

    def setvol(self, vol):
        return self._exec('setvol', vol)

    def volup(self, delta=10):
        volume = int(self.status().output['volume'])
        new_volume = volume+delta
        if new_volume <= 100:
            self.setvol(str(new_volume))
        return self.status()

    def voldown(self, delta=10):
        volume = int(self.status().output['volume'])
        new_volume = volume-delta
        if new_volume >= 0:
            self.setvol(str(new_volume))
        return self.status()

    def add(self, content):
        return self._exec('add', content)

    def playlistadd(self, playlist):
        return self._exec('playlistadd', playlist)

    def clear(self):
        return self._exec('clear')

    def status(self):
        return Response(output=self.client.status())

# vim:sw=4:ts=4:et:

