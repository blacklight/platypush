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

    def play(self, resource=None):
        if resource:
            self.clear()
            self.add(resource)
        return self._exec('play')

    def play_pos(self, pos):
        return self._exec('play', pos)

    def pause(self):
        status = self.status().output['state']
        if status == 'play': return self._exec('pause')
        else: return self._exec('play')

    def stop(self):
        return self._exec('stop')

    def play_or_stop(self):
        status = self.status().output['state']
        if status == 'play': return self._exec('stop')
        else: return self._exec('play')

    def playid(self, track_id):
        return self._exec('playid', track_id)

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

    def random(self, value=None):
        if value is None:
            value = int(self.status().output['random'])
            value = 1 if value == 0 else 0
        return self._exec('random', value)

    def repeat(self, value=None):
        if value is None:
            value = int(self.status().output['repeat'])
            value = 1 if value == 0 else 0
        return self._exec('repeat', value)

    def add(self, resource):
        return self._exec('add', resource)

    def load(self, playlist):
        self._exec('load', playlist)
        return self.play()

    def clear(self):
        return self._exec('clear')

    def seekcur(self, value):
        return self._exec('seekcur', value)

    def forward(self):
        return self._exec('seekcur', '+15')

    def back(self):
        return self._exec('seekcur', '-15')

    def status(self):
        return Response(output=self.client.status())

    def currentsong(self):
        return Response(output=self.client.currentsong())

    def playlistinfo(self):
        return Response(output=self.client.playlistinfo())

    def listplaylists(self):
        return Response(output=sorted(self.client.listplaylists(),
                                      key=lambda p: p['playlist']))

    def lsinfo(self, uri=None):
        output = self.client.lsinfo(uri) if uri else self.client.lsinfo()
        return Response(output=output)

    def plchanges(self, version):
        return Response(output=self.client.plchanges(version))


# vim:sw=4:ts=4:et:

