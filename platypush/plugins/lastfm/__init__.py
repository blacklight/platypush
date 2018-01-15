import pylast
import time

from platypush.message.response import Response

from .. import Plugin

class LastfmPlugin(Plugin):
    def __init__(self, api_key, api_secret, username, password):
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.password = password

        self.lastfm = pylast.LastFMNetwork(
            api_key = self.api_key,
            api_secret = self.api_secret,
            username = self.username,
            password_hash = pylast.md5(self.password))


    def scrobble(self, artist, title, album=None, **kwargs):
        self.lastfm.scrobble(
            artist = artist,
            title = title,
            album = album,
            timestamp = int(time.time()),
        )

        return Response()


    def update_now_playing(self, artist, title, album=None, **kwargs):
        self.lastfm.update_now_playing(
            artist = artist,
            title = title,
            album = album,
        )

        return Response()


# vim:sw=4:ts=4:et:

