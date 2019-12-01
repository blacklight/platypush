import time

from platypush.plugins import Plugin, action

class LastfmPlugin(Plugin):
    """
    Plugin to interact with your Last.FM (https://last.fm) account, update your
    current track and your scrobbles.

    Requires:

        * **pylast** (``pip install pylast``)
    """

    def __init__(self, api_key, api_secret, username, password):
        """
        :param api_key: Last.FM API key, see https://www.last.fm/api
        :type api_key: str

        :param api_secret: Last.FM API secret, see https://www.last.fm/api
        :type api_key: str

        :param username: Last.FM username
        :type api_key: str

        :param password: Last.FM password, used to sign the requests
        :type api_key: str
        """

        import pylast
        super().__init__()

        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.password = password

        self.lastfm = pylast.LastFMNetwork(
            api_key = self.api_key,
            api_secret = self.api_secret,
            username = self.username,
            password_hash = pylast.md5(self.password))


    @action
    def scrobble(self, artist, title, album=None, **kwargs):
        """
        Scrobble a track to Last.FM

        :param artist: Artist
        :type artist: str
        :param title: Title
        :type title: str
        :param album: Album (optional)
        :type album: str
        """

        self.lastfm.scrobble(
            artist = artist,
            title = title,
            album = album,
            timestamp = int(time.time()),
        )


    @action
    def update_now_playing(self, artist, title, album=None, **kwargs):
        """
        Update the currently playing track

        :param artist: Artist
        :type artist: str
        :param title: Title
        :type title: str
        :param album: Album (optional)
        :type album: str
        """

        self.lastfm.update_now_playing(
            artist = artist,
            title = title,
            album = album,
        )


# vim:sw=4:ts=4:et:

