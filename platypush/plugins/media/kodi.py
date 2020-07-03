import json
import re
import threading
import time

from platypush.context import get_bus
from platypush.plugins import action
from platypush.plugins.media import MediaPlugin, PlayerState
from platypush.message.event.media import MediaPlayEvent, MediaPauseEvent, MediaStopEvent, \
    MediaSeekEvent, MediaVolumeChangedEvent, NewPlayingMediaEvent


# noinspection PyUnusedLocal
class MediaKodiPlugin(MediaPlugin):
    """
    Plugin to interact with a Kodi media player instance

    Requires:

        * **kodi-json** (``pip install kodi-json``)
        * **websocket-client** (``pip install websocket-client``), optional, for player events support
    """

    def __init__(self, host, http_port=8080, websocket_port=9090, username=None, password=None, **kwargs):
        """
        :param host: Kodi host name or IP
        :type host: str

        :param http_port: Kodi JSON RPC web port. Remember to enable "Allow remote control via HTTP"
            in Kodi service settings -> advanced configuration and "Allow remote control from applications"
            on this system and, optionally, on other systems if the Kodi server is on another machine
        :type http_port: int

        :param websocket_port: Kodi JSON RPC websocket port, used to receive player events
        :type websocket_port: int

        :param username: Kodi username (optional)
        :type username: str

        :param password: Kodi password (optional)
        :type password: str
        """

        super().__init__(**kwargs)

        self.host = host
        self.http_port = http_port
        self.websocket_port = websocket_port
        self.url = 'http://{}:{}/jsonrpc'.format(host, http_port)
        self.websocket_url = 'ws://{}:{}/jsonrpc'.format(host, websocket_port)
        self.username = username
        self.password = password
        self._ws = None
        threading.Thread(target=self._websocket_thread()).start()

    def _get_kodi(self):
        from kodijson import Kodi

        args = [self.url]
        if self.username:
            args += [self.username]
            if self.password:
                args += [self.password]

        return Kodi(*args)

    def _get_player_id(self):
        kodi = self._get_kodi()
        players = kodi.Player.GetActivePlayers().get('result', [])
        if not players:
            return None

        return players.pop().get('playerid')

    def _websocket_thread(self):
        """
        Initialize the websocket JSON RPC interface, if available, to receive player notifications
        """

        def thread_hndl():
            try:
                import websocket
            except ImportError:
                self.logger.warning('websocket-client is not installed, Kodi events will be disabled')
                return

            if not self._ws:
                self._ws = websocket.WebSocketApp(self.websocket_url,
                                                  on_message=self._on_ws_msg(),
                                                  on_error=self._on_ws_error(),
                                                  on_close=self._on_ws_close())

                self.logger.info('Kodi websocket interface for events started')
                self._ws.run_forever()

        return thread_hndl

    def _post_event(self, evt_type, **evt):
        bus = get_bus()
        bus.post(evt_type(player=self.host, plugin='media.kodi', **evt))

    def _on_ws_msg(self):
        def hndl(ws, msg):
            self.logger.info("Received Kodi message: {}".format(msg))
            msg = json.loads(msg)
            method = msg.get('method')

            if method == 'Player.OnPlay':
                item = msg.get('params', {}).get('data', {}).get('item', {})
                player = msg.get('params', {}).get('data', {}).get('player', {})
                self._post_event(MediaPlayEvent, player_id=player.get('playerid'),
                                 title=item.get('title'), media_type=item.get('type'))
            elif method == 'Player.OnPause':
                item = msg.get('params', {}).get('data', {}).get('item', {})
                player = msg.get('params', {}).get('data', {}).get('player', {})
                self._post_event(MediaPauseEvent, player_id=player.get('playerid'),
                                 title=item.get('title'), media_type=item.get('type'))
            elif method == 'Player.OnStop':
                player = msg.get('params', {}).get('data', {}).get('player', {})
                self._post_event(MediaStopEvent, player_id=player.get('playerid'))
            elif method == 'Player.OnSeek':
                player = msg.get('params', {}).get('data', {}).get('player', {})
                position = self._time_obj_to_pos(player.get('seekoffset'))
                self._post_event(MediaSeekEvent, position=position, player_id=player.get('playerid'))
            elif method == 'Application.OnVolumeChanged':
                volume = msg.get('params', {}).get('data', {}).get('volume')
                self._post_event(MediaVolumeChangedEvent, volume=volume)

        return hndl

    def _on_ws_error(self):
        def hndl(ws, error):
            self.logger.warning("Kodi websocket connection error: {}".format(error))
        return hndl

    def _on_ws_close(self):
        def hndl(ws):
            self._ws = None
            self.logger.warning("Kodi websocket connection closed")
            time.sleep(5)
            self._websocket_thread()

        return hndl

    def _build_result(self, result):
        status = self.status().output
        status['result'] = result.get('result')
        return status, result.get('error')

    @action
    def play(self, resource, *args, **kwargs):
        """
        Open and play the specified file or URL

        :param resource: URL or path to the media to be played
        """

        youtube_id = self.get_youtube_id(resource)
        if youtube_id:
            try:
                resource = self.get_youtube_url('https://www.youtube.com/watch?v=' + youtube_id).output
            except Exception as e:
                self.logger.warning('youtube-dl error, falling back to Kodi YouTube plugin: {}'.format(str(e)))
                resource = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + youtube_id

        if resource.startswith('file://'):
            resource = resource[7:]

        result = self._get_kodi().Player.Open(item={'file': resource})
        if self.volume:
            self.set_volume(volume=int(self.volume))

        return self._build_result(result)

    @action
    def pause(self, player_id=None, *args, **kwargs):
        """
        Play/pause the current media
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        result = self._get_kodi().Player.PlayPause(playerid=player_id)
        return self._build_result(result)

    @action
    def get_active_players(self):
        """
        Get the list of active players
        """

        result = self._get_kodi().Player.GetActivePlayers()
        return result.get('result'), result.get('error')

    @action
    def get_movies(self, *args, **kwargs):
        """
        Get the list of movies on the Kodi server
        """

        result = self._get_kodi().VideoLibrary.GetMovies()
        return result.get('result'), result.get('error')

    @action
    def stop(self, player_id=None, *args, **kwargs):
        """
        Stop the current media
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        result = self._get_kodi().Player.Stop(playerid=player_id)
        return self._build_result(result)

    @action
    def notify(self, title, message, *args, **kwargs):
        """
        Send a notification to the Kodi UI
        """

        result = self._get_kodi().GUI.ShowNotification(title=title, message=message)
        return result.get('result'), result.get('error')

    @action
    def left(self, *args, **kwargs):
        """
        Simulate a left input event
        """

        result = self._get_kodi().Input.Left()
        return result.get('result'), result.get('error')

    @action
    def right(self, *args, **kwargs):
        """
        Simulate a right input event
        """

        result = self._get_kodi().Input.Right()
        return result.get('result'), result.get('error')

    @action
    def up(self, *args, **kwargs):
        """
        Simulate an up input event
        """

        result = self._get_kodi().Input.Up()
        return result.get('result'), result.get('error')

    @action
    def down(self, *args, **kwargs):
        """
        Simulate a down input event
        """

        result = self._get_kodi().Input.Down()
        return result.get('result'), result.get('error')

    @action
    def back_btn(self, *args, **kwargs):
        """
        Simulate a back input event
        """

        result = self._get_kodi().Input.Back()
        return result.get('result'), result.get('error')

    @action
    def select(self, *args, **kwargs):
        """
        Simulate a select input event
        """

        result = self._get_kodi().Input.Select()
        return result.get('result'), result.get('error')

    @action
    def send_text(self, text, *args, **kwargs):
        """
        Simulate a send_text input event

        :param text: Text to send
        :type text: str
        """

        result = self._get_kodi().Input.SendText(text=text)
        return result.get('result'), result.get('error')

    @action
    def get_volume(self, *args, **kwargs):
        result = self._get_kodi().Application.GetProperties(
            properties=['volume'])

        return result.get('result'), result.get('error')

    @action
    def volup(self, step=10.0, *args, **kwargs):
        """ Volume up (default: +10%) """
        volume = self._get_kodi().Application.GetProperties(
            properties=['volume']).get('result', {}).get('volume')

        result = self._get_kodi().Application.SetVolume(volume=int(min(volume+step, 100)))
        return self._build_result(result)

    @action
    def voldown(self, step=10.0, *args, **kwargs):
        """ Volume down (default: -10%) """
        volume = self._get_kodi().Application.GetProperties(
            properties=['volume']).get('result', {}).get('volume')

        result = self._get_kodi().Application.SetVolume(volume=int(max(volume-step, 0)))
        return self._build_result(result)

    @action
    def set_volume(self, volume, *args, **kwargs):
        """
        Set the application volume

        :param volume: Volume to set between 0 and 100
        :type volume: int
        """

        result = self._get_kodi().Application.SetVolume(volume=int(volume))
        return self._build_result(result)

    @action
    def mute(self, *args, **kwargs):
        """
        Mute/unmute the application
        """

        muted = self._get_kodi().Application.GetProperties(
            properties=['muted']).get('result', {}).get('muted')

        result = self._get_kodi().Application.SetMute(mute=(not muted))
        return self._build_result(result)

    @action
    def is_muted(self, *args, **kwargs):
        """
        Return the muted status of the application
        """

        result = self._get_kodi().Application.GetProperties(properties=['muted'])
        return result.get('result')

    @action
    def scan_video_library(self, *args, **kwargs):
        """
        Scan the video library
        """

        result = self._get_kodi().VideoLibrary.Scan()
        return result.get('result'), result.get('error')

    @action
    def scan_audio_library(self, *args, **kwargs):
        """
        Scan the audio library
        """

        result = self._get_kodi().AudioLibrary.Scan()
        return result.get('result'), result.get('error')

    @action
    def clean_video_library(self, *args, **kwargs):
        """
        Clean the video library
        """

        result = self._get_kodi().VideoLibrary.Clean()
        return result.get('result'), result.get('error')

    @action
    def clean_audio_library(self, *args, **kwargs):
        """
        Clean the audio library
        """

        result = self._get_kodi().AudioLibrary.Clean()
        return result.get('result'), result.get('error')

    @action
    def quit(self, *args, **kwargs):
        """
        Quit the application
        """

        result = self._get_kodi().Application.Quit()
        return result.get('result'), result.get('error')

    @action
    def get_songs(self, *args, **kwargs):
        """
        Get the list of songs in the audio library
        """

        result = self._get_kodi().Application.GetSongs()
        return result.get('result'), result.get('error')

    @action
    def get_artists(self, *args, **kwargs):
        """
        Get the list of artists in the audio library
        """

        result = self._get_kodi().Application.GetArtists()
        return result.get('result'), result.get('error')

    @action
    def get_albums(self, *args, **kwargs):
        """
        Get the list of albums in the audio library
        """

        result = self._get_kodi().Application.GetAlbums()
        return result.get('result'), result.get('error')

    @action
    def fullscreen(self, *args, **kwargs):
        """
        Set/unset fullscreen mode
        """

        fullscreen = self._get_kodi().GUI.GetProperties(
            properties=['fullscreen']).get('result', {}).get('fullscreen')

        result = self._get_kodi().GUI.SetFullscreen(fullscreen=(not fullscreen))
        return result.get('result'), result.get('error')

    @action
    def shuffle(self, player_id=None, shuffle=None, *args, **kwargs):
        """
        Set/unset shuffle mode
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        if shuffle is None:
            shuffle = self._get_kodi().Player.GetProperties(
                playerid=player_id,
                properties=['shuffled']).get('result', {}).get('shuffled')

        result = self._get_kodi().Player.SetShuffle(
           playerid=player_id,  shuffle=(not shuffle))
        return result.get('result'), result.get('error')

    @action
    def repeat(self, player_id=None, repeat=None, *args, **kwargs):
        """
        Set/unset repeat mode
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        if repeat is None:
            repeat = self._get_kodi().Player.GetProperties(
                playerid=player_id,
                properties=['repeat']).get('result', {}).get('repeat')

        result = self._get_kodi().Player.SetRepeat(
            playerid=player_id,
            repeat='off' if repeat in ('one','all') else 'off')

        return result.get('result'), result.get('error')

    @staticmethod
    def _time_pos_to_obj(t):
        hours = int(t/3600)
        minutes = int((t - hours*3600)/60)
        seconds = t - hours*3600 - minutes*60
        milliseconds = t - int(t)

        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'milliseconds': milliseconds,
        }

    @staticmethod
    def _time_obj_to_pos(t):
        return t.get('hours', 0) * 3600 + t.get('minutes', 0) * 60 + \
               t.get('seconds', 0) + t.get('milliseconds', 0)/1000

    @action
    def seek(self, position, player_id=None, *args, **kwargs):
        """
        Move to the specified time position in seconds

        :param position: Seek time in seconds
        :type position: float
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        position = self._time_pos_to_obj(position)
        result = self._get_kodi().Player.Seek(playerid=player_id, value=position)
        return self._build_result(result)

    @action
    def set_position(self, position, player_id=None, *args, **kwargs):
        """
        Move to the specified time position in seconds

        :param position:  Seek time in seconds
        :type position: float
        """
        return self.seek(position=position, player_id=player_id, *args, **kwargs)

    @action
    def back(self, offset=60, player_id=None, *args, **kwargs):
        """
        Move the player execution backward by delta_seconds

        :param offset: Backward seek duration (default: 60 seconds)
        :type offset: float
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        position = self._get_kodi().Player.GetProperties(
            playerid=player_id, properties=['time']).get('result', {}).get('time', {})

        position = self._time_obj_to_pos(position)
        return self.seek(player_id=player_id, position=position)

    @action
    def forward(self, offset=60, player_id=None, *args, **kwargs):
        """
        Move the player execution forward by delta_seconds

        :param offset: Forward seek duration (default: 60 seconds)
        :type offset: float
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        position = self._get_kodi().Player.GetProperties(
            playerid=player_id, properties=['time']).get('result', {}).get('time', {})

        position = self._time_obj_to_pos(position)
        return self.seek(player_id=player_id, position=position)

    @action
    def status(self, player_id=None):
        media_props = {
            'album': 'album',
            'artist': 'artist',
            'duration': 'duration',
            'fanart': 'fanart',
            'file': 'file',
            'season': 'season',
            'showtitle': 'showtitle',
            'streamdetails': 'streamdetails',
            'thumbnail': 'thumbnail',
            'title': 'title',
            'tvshowid': 'tvshowid',
            'url': 'file',
        }

        app_props = {
            'volume': 'volume',
            'mute': 'muted',
        }

        player_props = {
            "duration": "totaltime",
            "position": "time",
            "repeat": "repeat",
            "seekable": "canseek",
            'speed': 'speed',
            "subtitles": "subtitles",
        }

        ret = {'state': PlayerState.IDLE.value}

        try:
            kodi = self._get_kodi()
            players = kodi.Player.GetActivePlayers().get('result', [])
        except:
            return ret

        ret['state'] = PlayerState.STOP.value
        app = kodi.Application.GetProperties(properties=list(set(app_props.values()))).get('result', {})

        for status_prop, kodi_prop in app_props.items():
            ret[status_prop] = app.get(kodi_prop)

        if not players:
            return ret

        if player_id is None:
            player_id = players.pop().get('playerid')
        else:
            for p in players:
                if p['player_id'] == player_id:
                    player_id = p
                    break

        if player_id is None:
            return ret

        media = kodi.Player.GetItem(playerid=player_id,
                                    properties=list(set(media_props.values()))).get('result', {}).get('item', {})

        for status_prop, kodi_prop in media_props.items():
            ret[status_prop] = media.get(kodi_prop)

        player_info = kodi.Player.GetProperties(
            playerid=player_id,
            properties=list(set(player_props.values()))).get('result', {})

        for status_prop, kodi_prop in player_props.items():
            ret[status_prop] = player_info.get(kodi_prop)

        if ret['duration']:
            ret['duration'] = self._time_obj_to_pos(ret['duration'])

        if ret['position']:
            ret['position'] = self._time_obj_to_pos(ret['position'])

        ret['state'] = PlayerState.PAUSE.value if player_info.get('speed', 0) == 0 else PlayerState.PLAY.value
        return ret


# vim:sw=4:ts=4:et:
