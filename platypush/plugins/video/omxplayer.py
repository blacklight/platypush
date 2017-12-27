import json
import logging
import re
import subprocess

from dbus.exceptions import DBusException
from omxplayer import OMXPlayer

from platypush.message.response import Response

from .. import Plugin

class VideoOmxplayerPlugin(Plugin):
    def __init__(self, args=[], *argv, **kwargs):
        self.args = args
        self.player = None

    def play(self, resource):
        if resource.startswith('youtube:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            resource = self._get_youtube_content(resource)

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

    @classmethod
    def _get_youtube_content(cls, url):
        m = re.match('youtube:video:(.*)', url)
        if m: url = 'https://www.youtube.com/watch?v={}'.format(m.group(1))

        proc = subprocess.Popen(['youtube-dl','-f','best', '-g', url],
                                stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8", "strict")[:-1]


# vim:sw=4:ts=4:et:

