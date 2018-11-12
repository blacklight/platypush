import re

from platypush.plugins import Plugin, action


class MediaKodiPlugin(Plugin):
    """
    Plugin to interact with a Kodi media player instance

    Requires:

        * **kodi-json** (``pip install kodi-json``)
    """

    def __init__(self, url, username=None, password=None, *args, **kwargs):
        """
        :param url: URL for the JSON-RPC calls to the Kodi system (example: http://localhost:8080/jsonrpc)
        :type url: str

        :param username: Kodi username (optional)
        :type username: str

        :param password: Kodi password (optional)
        :type username: str
        """

        super().__init__(*args, **kwargs)

        self.url = url
        self.username = username
        self.password = password


    def _get_kodi(self):
        from kodijson import Kodi

        args = [self.url]
        if self.username:
            args += [self.username]
            if self.password: args += [self.password]

        return Kodi(*args)

    def _get_player_id(self):
        kodi = self._get_kodi()
        players = kodi.Player.GetActivePlayers().get('result', [])
        if not players:
            raise RuntimeError('No players found')

        return players.pop().get('playerid')

    @action
    def get_active_players(self):
        """
        Get the list of active players
        """

        result = self._get_kodi().Player.GetActivePlayers()
        return (result.get('result'), result.get('error'))

    @action
    def get_movies(self, *args, **kwargs):
        """
        Get the list of movies on the Kodi server
        """

        result = self._get_kodi().VideoLibrary.GetMovies()
        return (result.get('result'), result.get('error'))

    @action
    def play_pause(self, player_id=None, *args, **kwargs):
        """
        Play/pause the current media
        """

        if not player_id:
            player_id = self._get_player_id()

        result = self._get_kodi().Player.PlayPause(playerid=player_id)
        return (result.get('result'), result.get('error'))

    @action
    def stop(self, player_id=None, *args, **kwargs):
        """
        Stop the current media
        """

        if not player_id:
            player_id = self._get_player_id()

        result = self._get_kodi().Player.Stop(playerid=player_id)
        return (result.get('result'), result.get('error'))

    @action
    def notify(self, title, message, *args, **kwargs):
        """
        Send a notification to the Kodi UI
        """

        result = self._get_kodi().GUI.ShowNotification(title=title, message=message)
        return (result.get('result'), result.get('error'))

    @action
    def open(self, resource, *args, **kwargs):
        """
        Open and play the specified file or URL
        """

        if resource.startswith('youtube:video:') \
                or resource.startswith('https://www.youtube.com/watch?v='):
            m1 = re.match('youtube:video:([^:?&]+)', resource)
            m2 = re.match('https://www.youtube.com/watch?v=([^:?&#/]+)', resource)
            youtube_id = None

            if m1: youtube_id = m1.group(1)
            elif m2: youtube_id = m2.group(1)

            if youtube_id:
                resource = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + youtube_id

        result = self._get_kodi().Player.Open(item={'file': resource})
        return (result.get('result'), result.get('error'))

    @action
    def left(self, *args, **kwargs):
        """
        Simulate a left input event
        """

        result = self._get_kodi().Input.Left()
        return (result.get('result'), result.get('error'))

    @action
    def right(self, *args, **kwargs):
        """
        Simulate a right input event
        """

        result = self._get_kodi().Input.Right()
        return (result.get('result'), result.get('error'))

    @action
    def up(self, *args, **kwargs):
        """
        Simulate an up input event
        """

        result = self._get_kodi().Input.Up()
        return (result.get('result'), result.get('error'))

    @action
    def down(self, *args, **kwargs):
        """
        Simulate a down input event
        """

        result = self._get_kodi().Input.Down()
        return (result.get('result'), result.get('error'))

    @action
    def back_btn(self, *args, **kwargs):
        """
        Simulate a back input event
        """

        result = self._get_kodi().Input.Back()
        return (result.get('result'), result.get('error'))

    @action
    def select(self, *args, **kwargs):
        """
        Simulate a select input event
        """

        result = self._get_kodi().Input.Select()
        return (result.get('result'), result.get('error'))

    @action
    def send_text(self, text, *args, **kwargs):
        """
        Simulate a send_text input event

        :param text: Text to send
        :type text: str
        """

        result = self._get_kodi().Input.SendText(text=text)
        return (result.get('result'), result.get('error'))

    @action
    def get_volume(self, *args, **kwargs):
        result = self._get_kodi().Application.GetProperties(
            properties=['volume'])

        return (result.get('result'), result.get('error'))

    @action
    def volup(self, *args, **kwargs):
        """ Volume up by 10% """
        volume = self._get_kodi().Application.GetProperties(
            properties=['volume']).get('result', {}).get('volume')

        result = self._get_kodi().Application.SetVolume(volume=min(volume+10, 100))
        return (result.get('result'), result.get('error'))

    @action
    def voldown(self, *args, **kwargs):
        """ Volume down by 10% """
        volume = self._get_kodi().Application.GetProperties(
            properties=['volume']).get('result', {}).get('volume')

        result = self._get_kodi().Application.SetVolume(volume=max(volume-10, 0))
        return (result.get('result'), result.get('error'))

    @action
    def set_volume(self, volume, *args, **kwargs):
        """
        Set the application volume

        :param volume: Volume to set
        :type volume: int
        """

        result = self._get_kodi().Application.SetVolume(volume=volume)
        return (result.get('result'), result.get('error'))

    @action
    def toggle_mute(self, *args, **kwargs):
        """
        Mute/unmute the application
        """

        muted = self._get_kodi().Application.GetProperties(
            properties=['muted']).get('result', {}).get('muted')

        result = self._get_kodi().Application.SetMute(mute=(not muted))
        return (result.get('result'), result.get('error'))

    @action
    def is_muted(self, *args, **kwargs):
        """
        Return the muted status of the application
        """

        result = self._get_kodi().Application.GetProperties(properties=['muted'])
        return (result.get('result'), result.get('error'))

    @action
    def scan_video_library(self, *args, **kwargs):
        """
        Scan the video library
        """

        result = self._get_kodi().VideoLibrary.Scan()
        return (result.get('result'), result.get('error'))

    @action
    def scan_audio_library(self, *args, **kwargs):
        """
        Scan the audio library
        """

        result = self._get_kodi().AudioLibrary.Scan()
        return (result.get('result'), result.get('error'))

    @action
    def clean_video_library(self, *args, **kwargs):
        """
        Clean the video library
        """

        result = self._get_kodi().VideoLibrary.Clean()
        return (result.get('result'), result.get('error'))

    @action
    def clean_audio_library(self, *args, **kwargs):
        """
        Clean the audio library
        """

        result = self._get_kodi().AudioLibrary.Clean()
        return (result.get('result'), result.get('error'))

    @action
    def quit(self, *args, **kwargs):
        """
        Quit the application
        """

        result = self._get_kodi().Application.Quit()
        return (result.get('result'), result.get('error'))

    @action
    def get_songs(self, *args, **kwargs):
        """
        Get the list of songs in the audio library
        """

        result = self._get_kodi().Application.GetSongs()
        return (result.get('result'), result.get('error'))

    @action
    def get_artists(self, *args, **kwargs):
        """
        Get the list of artists in the audio library
        """

        result = self._get_kodi().Application.GetArtists()
        return (result.get('result'), result.get('error'))

    @action
    def get_albums(self, *args, **kwargs):
        """
        Get the list of albums in the audio library
        """

        result = self._get_kodi().Application.GetAlbums()
        return (result.get('result'), result.get('error'))

    @action
    def toggle_fullscreen(self, *args, **kwargs):
        """
        Set/unset fullscreen mode
        """

        fullscreen = self._get_kodi().GUI.GetProperties(
            properties=['fullscreen']).get('result', {}).get('fullscreen')

        result = self._get_kodi().GUI.SetFullscreen(fullscreen=(not fullscreen))
        return (result.get('result'), result.get('error'))

    @action
    def toggle_shuffle(self, player_id=None, shuffle=None, *args, **kwargs):
        """
        Set/unset shuffle mode
        """

        if not player_id:
            player_id = self._get_player_id()

        if shuffle is None:
            shuffle = self._get_kodi().Player.GetProperties(
                playerid=player_id,
                properties=['shuffled']).get('result', {}).get('shuffled')

        result = self._get_kodi().Player.SetShuffle(
           playerid=player_id,  shuffle=(not shuffle))
        return (result.get('result'), result.get('error'))

    @action
    def toggle_repeat(self, player_id=None, repeat=None, *args, **kwargs):
        """
        Set/unset repeat mode
        """

        if not player_id:
            player_id = self._get_player_id()

        if repeat is None:
            repeat = self._get_kodi().Player.GetProperties(
                playerid=player_id,
                properties=['repeat']).get('result', {}).get('repeat')

        result = self._get_kodi().Player.SetRepeat(
            playerid=player_id,
            repeat='off' if repeat in ('one','all') else 'off')

        return (result.get('result'), result.get('error'))

    @action
    def seek(self, position, player_id=None, *args, **kwargs):
        """
        Move the cursor to the specified position in seconds

        :param position: Seek time in seconds
        :type position: int
        """

        if not player_id:
            player_id = self._get_player_id()

        hours = int(position/3600)
        minutes = int((position - hours*3600)/60)
        seconds = position - hours*3600 - minutes*60

        position = {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'milliseconds': 0,
        }

        result = self._get_kodi().Player.Seek(playerid=player_id, value=position)
        return (result.get('result'), result.get('error'))

    @action
    def back(self, delta_seconds=60, player_id=None, *args, **kwargs):
        """
        Move the player execution backward by delta_seconds

        :param delta_seconds: Backward seek duration (default: 60 seconds)
        :type delta_seconds: int
        """

        if not player_id:
            player_id = self._get_player_id()

        position = self._get_kodi().Player.GetProperties(
            playerid=player_id, properties=['time']).get('result', {}).get('time', {})

        position = position.get('hours', 0)*3600 + \
            position.get('minutes', 0)*60 + position.get('seconds', 0) - delta_seconds

        return self.seek(player_id=player_id, position=position)

    @action
    def forward(self, delta_seconds=60, player_id=None, *args, **kwargs):
        """
        Move the player execution forward by delta_seconds

        :param delta_seconds: Forward seek duration (default: 60 seconds)
        :type delta_seconds: int
        """

        if not player_id:
            player_id = self._get_player_id()

        position = self._get_kodi().Player.GetProperties(
            playerid=player_id, properties=['time']).get('result', {}).get('time', {})

        position = position.get('hours', 0)*3600 + \
            position.get('minutes', 0)*60 + position.get('seconds', 0) + delta_seconds

        return self.seek(player_id=player_id, position=position)


# vim:sw=4:ts=4:et:

