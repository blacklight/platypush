import time
from typing import Optional, List

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
            api_key=self.api_key,
            api_secret=self.api_secret,
            username=self.username,
            password_hash=pylast.md5(self.password),
        )

    @action
    def scrobble(self, artist, title, album=None):
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
            artist=artist,
            title=title,
            album=album,
            timestamp=int(time.time()),
        )

    @action
    def update_now_playing(self, artist, title, album=None):
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
            artist=artist,
            title=title,
            album=album,
        )

    @action
    def get_recent_tracks(
        self,
        username: Optional[str] = None,
        limit: int = 10,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
    ) -> List[dict]:
        """
        Get a list of recently played tracks.

        :param username: Target username (default: the one registered to this
            plugin).
        :param limit: Maximum number of tracks to be returned (default: 10).
        :param time_from: Return tracks starting from this time
            (as a UNIX timestamp).
        :param time_to: Return tracks starting up to this time
            (as a UNIX timestamp).
        :return: Example:

            .. code-block:: json

                [
                    {
                        "artist": "Led Zeppelin",
                        "title": "Stairway to Heaven",
                        "album": "IV",
                        "timestamp": 1654196137
                    }
                ]

        """

        return [
            {
                'title': track.track.title,
                'album': track.album,
                'timestamp': int(track.timestamp or 0),
                **(
                    {'artist': track.track.artist.name}
                    if track.track.artist
                    else {'artist': None}
                ),
            }
            for track in self.lastfm.get_user(
                username or self.username
            ).get_recent_tracks(
                limit=limit,
                time_from=time_from,
                time_to=time_to,
            )
        ]

    @action
    def get_track(self, artist: str, title: str) -> Optional[dict]:
        """
        Get the information about a track.

        :param artist: Track artist.
        :param title: Track title.
        :return: The retrieved track, with the title corrected if required, if
            it exists on Last.FM. Example:

                .. code-block:: json

                    {
                        "artist": "Led Zeppelin",
                        "title": "Stairway to Heaven",
                        "tags": ["rock", "hard rock", "70s"]
                    }

        """
        track = self.lastfm.get_track(artist, title)
        return {
            'title': track.get_correction(),
            'tags': track.get_tags(),
            **({'artist': track.artist.name} if track.artist else {'artist': None}),
        }

    @action
    def get_similar_tracks(
        self, artist: str, title: str, limit: Optional[int] = None
    ) -> List[dict]:
        """
        Get the tracks that are similar to a specific track.

        :param artist: Track artist.
        :param title: Track title.
        :param limit: Maximum number of suggested tracks to be returned
            (default: None).
        :return: A list of similar tracks, each with a ``match`` score between
            0 and 1. Example:

                .. code-block:: json

                    [
                      {
                        "artist": "Led Zeppelin",
                        "title": "Black Dog",
                        "score": 1.0
                      },
                      {
                        "artist": "Led Zeppelin",
                        "title": "Rock and Roll",
                        "score": 0.89
                      },
                      {
                        "artist": "Eagles",
                        "title": "Hotel California",
                        "score": 0.471
                      },
                      {
                        "artist": "Deep Purple",
                        "title": "Smoke on the Water",
                        "score": 0.393
                      }
                    ]

        """
        track = self.lastfm.get_track(artist, title)
        if not track:
            return []

        return [
            {
                'artist': t.item.artist.name,
                'title': t.item.title,
                'score': t.match,
            }
            for t in track.get_similar(limit=limit)
        ]


# vim:sw=4:ts=4:et:
