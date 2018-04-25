import logging
import json
import urllib3
import urllib.request
import urllib.parse

from platypush.plugins.media import PlayerState
from platypush.message.response import Response

from .. import Plugin

class VideoTorrentcastPlugin(Plugin):
    def __init__(self, server='localhost', port=9090, *args, **kwargs):
        self.server = server
        self.port = port
        self.state = PlayerState.STOP.value

    def play(self, url):
        request = urllib.request.urlopen(
            'http://{}:{}/play/'.format(self.server, self.port),
            data=urllib.parse.urlencode({
                'url': url
            }).encode()
        )

        self.state = PlayerState.PLAY.value
        return Response(output=request.read())

    def pause(self):
        http = urllib3.PoolManager()
        request = http.request('POST',
            'http://{}:{}/pause/'.format(self.server, self.port))

        self.state = PlayerState.PAUSE.value
        return Response(output=request.read())

    def stop(self):
        http = urllib3.PoolManager()
        request = http.request('POST',
            'http://{}:{}/stop/'.format(self.server, self.port))

        self.state = PlayerState.STOP.value
        return Response(output=request.read())

    def search(self, query):
        request = urllib.request.urlopen(urllib.request.Request(
            'https://api.apidomain.info/list?' + urllib.parse.urlencode({
                'sort': 'relevance',
                'quality': '720p,1080p,3d',
                'page': 1,
                'keywords': query,
            }),
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
                    '(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            })
        )

        results = json.loads(request.read())
        return Response(output=results)

    def search_and_play(self, query):
        response = self.search(query)
        if not response.output['MovieList']:
            logging.info('No torrent results found for {}'.format(query))
            return Response()

        item = response.output['MovieList'][0]
        magnet = item['items'][0]['torrent_magnet']
        logging.info('Playing torrent "{}" from {}'
                     .format(item['title'], magnet))

        return self.play(magnet)

    def voldown(self): return Response(output='Unsupported method')
    def volup(self): return Response(output='Unsupported method')
    def back(self): return Response(output='Unsupported method')
    def forward(self): return Response(output='Unsupported method')

    def status(self):
        return Response(output={ 'state': self.state })


# vim:sw=4:ts=4:et:

