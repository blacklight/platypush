import json
import urllib3
import urllib.request
import urllib.parse

from platypush.plugins import Plugin, action
from platypush.plugins.media import PlayerState

class VideoTorrentcastPlugin(Plugin):
    def __init__(self, server='localhost', port=9090, *args, **kwargs):
        self.server = server
        self.port = port
        self.state = PlayerState.STOP.value

    @action
    def play(self, url):
        request = urllib.request.urlopen(
            'http://{}:{}/play/'.format(self.server, self.port),
            data=urllib.parse.urlencode({
                'url': url
            }).encode()
        )

        self.state = PlayerState.PLAY.value
        return request.read()

    @action
    def pause(self):
        http = urllib3.PoolManager()
        request = http.request('POST',
            'http://{}:{}/pause/'.format(self.server, self.port))

        self.state = PlayerState.PAUSE.value
        return request.read()

    @action
    def stop(self):
        http = urllib3.PoolManager()
        request = http.request('POST',
            'http://{}:{}/stop/'.format(self.server, self.port))

        self.state = PlayerState.STOP.value
        return request.read()

    @action
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
        return results

    @action
    def search_and_play(self, query):
        response = self.search(query)
        if not response.output['MovieList']:
            self.logger.info('No torrent results found for {}'.format(query))

        item = response.output['MovieList'][0]
        magnet = item['items'][0]['torrent_magnet']
        self.logger.info('Playing torrent "{}" from {}'
                     .format(item['title'], magnet))

        return self.play(magnet)

    @action
    def voldown(self): raise NotImplementedError()

    @action
    def volup(self): raise NotImplementedError()

    @action
    def back(self): raise NotImplementedError()

    @action
    def forward(self): raise NotImplementedError()

    @action
    def status(self): return { 'state': self.state }


# vim:sw=4:ts=4:et:

