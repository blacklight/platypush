import urllib3
import urllib.request

from platypush.message.response import Response

from .. import Plugin

class VideoTorrentcastPlugin(Plugin):
    def __init__(self, server='localhost', port=9090, *args, **kwargs):
        self.server = server
        self.port = port

    def play(self, url):
        request = urllib.request.urlopen(
            'http://{}:{}/play/'.format(self.server, self.port),
            data=urllib.parse.urlencode({
                'url': resource
            })
        )

        return Response(output=request.read())

    def pause(self):
        http = urllib3.PoolManager()
        request = http.request('POST',
            'http://{}:{}/pause/'.format(self.server, self.port))

        return Response(output=request.read())

    def stop(self):
        http = urllib3.PoolManager()
        request = http.request('POST',
            'http://{}:{}/stop/'.format(self.server, self.port))

        return Response(output=request.read())

    def voldown(self): return Response(output='Unsupported method')
    def volup(self): return Response(output='Unsupported method')
    def back(self): return Response(output='Unsupported method')
    def forward(self): return Response(output='Unsupported method')


# vim:sw=4:ts=4:et:

