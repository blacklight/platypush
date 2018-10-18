import re

from platypush.plugins import Plugin, action


class MediaKodiPlugin(Plugin):
    """
    Plugin to interact with a Kodi media player instance

    Requires:

        * **kodi-json** (``pip install kodi-rtmidi``)
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

    @action
    def get_movies(self, *args, **kwargs):
        """
        Get the list of movies on the Kodi server
        """

        return self._get_kodi().VideoLibrary.GetMovies()

    @action
    def play_pause(self, *args, **kwargs):
        """
        Play/pause the current media
        """

        return self._get_kodi().Player.PlayPause()

    @action
    def stop(self, *args, **kwargs):
        """
        Stop the current media
        """

        return self._get_kodi().Player.Stop()

    @action
    def notify(self, title, message, *args, **kwargs):
        """
        Send a notification to the Kodi UI
        """

        return self._get_kodi().GUI.ShowNotification(title=title, message=message)

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

        return self._get_kodi().Player.Open(item={'file': resource})

    @action
    def left(self, *args, **kwargs):
        """
        Simulate a left input event
        """

        return self._get_kodi().Input.Left()

    @action
    def right(self, *args, **kwargs):
        """
        Simulate a right input event
        """

        return self._get_kodi().Input.Right()

    @action
    def up(self, *args, **kwargs):
        """
        Simulate an up input event
        """

        return self._get_kodi().Input.Up()

    @action
    def down(self, *args, **kwargs):
        """
        Simulate a down input event
        """

        return self._get_kodi().Input.Down()

    @action
    def back(self, *args, **kwargs):
        """
        Simulate a back input event
        """

        return self._get_kodi().Input.Back()

    @action
    def select(self, *args, **kwargs):
        """
        Simulate a select input event
        """

        return self._get_kodi().Input.Select()

    @action
    def send_text(self, text, *args, **kwargs):
        """
        Simulate a send_text input event

        :param text: Text to send
        :type text: str
        """

        return self._get_kodi().Input.SendText(text=text)

    @action
    def volume(self, volume, *args, **kwargs):
        """
        Set the application volume

        :param volume: Volume to set
        :type volume: int
        """

        return self._get_kodi().Application.SetVolume(volume=volume)

    @action
    def mute(self, *args, **kwargs):
        """
        Mute the application
        """

        return self._get_kodi().Application.SetMute(mute=True)

    @action
    def unmute(self, *args, **kwargs):
        """
        Unmute the application
        """

        return self._get_kodi().Application.SetMute(mute=False)

    @action
    def scan_video_library(self, *args, **kwargs):
        """
        Scan the video library
        """

        return self._get_kodi().VideoLibrary.Scan()

    @action
    def scan_audio_library(self, *args, **kwargs):
        """
        Scan the audio library
        """

        return self._get_kodi().AudioLibrary.Scan()

    @action
    def clean_video_library(self, *args, **kwargs):
        """
        Clean the video library
        """

        return self._get_kodi().VideoLibrary.Clean()

    @action
    def clean_audio_library(self, *args, **kwargs):
        """
        Clean the audio library
        """

        return self._get_kodi().AudioLibrary.Clean()

    @action
    def quit(self, *args, **kwargs):
        """
        Quit the application
        """

        return self._get_kodi().Application.Quit()

    @action
    def get_songs(self, *args, **kwargs):
        """
        Get the list of songs in the audio library
        """

        return self._get_kodi().Application.GetSongs()

    @action
    def get_artists(self, *args, **kwargs):
        """
        Get the list of artists in the audio library
        """

        return self._get_kodi().Application.GetArtists()

    @action
    def get_albums(self, *args, **kwargs):
        """
        Get the list of albums in the audio library
        """

        return self._get_kodi().Application.GetAlbums()

    @action
    def set_fullscreen(self, fullscreen, *args, **kwargs):
        """
        Set/unset fullscreen mode
        """

        return self._get_kodi().GUI.SetFullscreen()

    @action
    def seek(self, position, *args, **kwargs):
        """
        Move the cursor to the specified position in seconds
        """

        return self._get_kodi().Player.Seek(position)


# vim:sw=4:ts=4:et:

