import json
import logging
import re
import subprocess

import urllib.request
import urllib.parse

from bs4 import BeautifulSoup
from dbus.exceptions import DBusException
from omxplayer import OMXPlayer

from platypush.message.response import Response

from .. import Plugin

class VideoOmxplayerPlugin(Plugin):
    def __init__(self, args=[], *argv, **kwargs):
        self.args = args
        self.player = None
        self.videos_queue = []

    def play(self, resource):
        if resource.startswith('youtube:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            resource = self._get_youtube_content(resource)

        logging.info('Playing {}'.format(resource))

        try:
            self.player = OMXPlayer(resource, args=self.args)
        except DBusException as e:
            logging.warning('DBus connection failed: you will probably not ' +
                            'be able to control the media')
            logging.exception(e)

        return self.status()

    def pause(self):
        if self.player: self.player.play_pause()

    def stop(self):
        if self.player:
            self.player.stop()
            self.player.quit()
            self.player = None
        return self.status()

    def voldown(self):
        if self.player:
            self.player.set_volume(max(-6000, self.player.volume()-1000))
        return self.status()

    def volup(self):
        if self.player:
            self.player.set_volume(min(0, self.player.volume()+1000))
        return self.status()

    def back(self):
        if self.player:
            self.player.seek(-30)
        return self.status()

    def forward(self):
        if self.player:
            self.player.seek(+30)
        return self.status()

    def next(self):
        if self.player:
            self.player.stop()

        if self.videos_queue:
            video = self.videos_queue.pop(0)
            return self.play(video)

        return Response(output={'status': 'no media'}, errors = [])


    def status(self):
        if self.player:
            return Response(output=json.dumps({
                'source': self.player.get_source(),
                'status': self.player.playback_status(),
                'volume': self.player.volume(),
                'elapsed': self.player.position(),
            }))
        else:
            return Response(output=json.dumps({
                'status': 'Not initialized'
            }))

    def youtube_search_and_play(self, query):
        self.videos_queue = self.youtube_search(query)
        url = self.videos_queue.pop(0)
        logging.info('Playing {}'.format(url))
        return self.play(url)

    def youtube_search(self, query):
        query = urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'lxml')
        results = []

        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            if vid['href'].startswith('/watch?v='):
                results.append('https://www.youtube.com' + vid['href'])

        logging.info('{} YouTube video results for the search query "{}"'.format(query))
        return results


    @classmethod
    def _get_youtube_content(cls, url):
        m = re.match('youtube:video:(.*)', url)
        if m: url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

        proc = subprocess.Popen(['youtube-dl','-f','best', '-g', url],
                                stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8", "strict")[:-1]


# vim:sw=4:ts=4:et:

