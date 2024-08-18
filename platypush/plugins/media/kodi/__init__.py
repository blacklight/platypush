import json
import threading
import time
from typing import Optional
from urllib.parse import urlparse

from platypush.context import get_bus
from platypush.plugins import action
from platypush.plugins.media import MediaPlugin, PlayerState
from platypush.message.event.media import (
    MediaPlayEvent,
    MediaPauseEvent,
    MediaStopEvent,
    MediaSeekEvent,
    MediaVolumeChangedEvent,
)


class MediaKodiPlugin(MediaPlugin):
    """
    Plugin to interact with a Kodi media player instance
    """

    def __init__(
        self,
        rpc_url: str = 'http://localhost:8080/jsonrpc',
        websocket_port: int = 9090,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
        """
        :param rpc_url: Base URL for the Kodi JSON RPC API (default:
            http://localhost:8080/jsonrpc). You need to make sure that the RPC
            API is enabled on your Kodi instance - you can enable it from the
            settings.
        :param websocket_port: Kodi JSON RPC websocket port, used to receive player events
        :param username: Kodi username (optional)
        :param password: Kodi password (optional)
        """

        super().__init__(**kwargs)

        self.url = rpc_url
        host, port = kwargs.get('host'), kwargs.get('port', 8080)

        if host and port:
            self.logger.warning('host and port are deprecated, use rpc_url instead')
            self.url = f'http://{host}:{port}/jsonrpc'

        self.host = urlparse(self.url).hostname
        self.websocket_port = websocket_port
        self.websocket_url = f'ws://{self.host}:{websocket_port}/jsonrpc'
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
                self.logger.warning(
                    'websocket-client is not installed, Kodi events will be disabled'
                )
                return

            if not self._ws:
                self._ws = websocket.WebSocketApp(
                    self.websocket_url,
                    on_message=self._on_ws_msg(),
                    on_error=self._on_ws_error(),
                    on_close=self._on_ws_close(),
                )

                self.logger.info('Kodi websocket interface for events started')
                self._ws.run_forever()

        return thread_hndl

    def _post_event(self, evt_type, **evt):
        bus = get_bus()
        bus.post(evt_type(player=self.host, plugin='media.kodi', **evt))

    def _on_ws_msg(self):
        def hndl(*args):
            msg = args[1] if len(args) > 1 else args[0]
            self.logger.info("Received Kodi message: %s", msg)
            msg = json.loads(msg)
            method = msg.get('method')

            if method == 'Player.OnPlay':
                item = msg.get('params', {}).get('data', {}).get('item', {})
                player = msg.get('params', {}).get('data', {}).get('player', {})
                self._post_event(
                    MediaPlayEvent,
                    player_id=player.get('playerid'),
                    title=item.get('title'),
                    media_type=item.get('type'),
                )
            elif method == 'Player.OnPause':
                item = msg.get('params', {}).get('data', {}).get('item', {})
                player = msg.get('params', {}).get('data', {}).get('player', {})
                self._post_event(
                    MediaPauseEvent,
                    player_id=player.get('playerid'),
                    title=item.get('title'),
                    media_type=item.get('type'),
                )
            elif method == 'Player.OnStop':
                player = msg.get('params', {}).get('data', {}).get('player', {})
                self._post_event(MediaStopEvent, player_id=player.get('playerid'))
                self._clear_resource()
            elif method == 'Player.OnSeek':
                player = msg.get('params', {}).get('data', {}).get('player', {})
                position = self._time_obj_to_pos(player.get('seekoffset'))
                self._post_event(
                    MediaSeekEvent, position=position, player_id=player.get('playerid')
                )
            elif method == 'Application.OnVolumeChanged':
                volume = msg.get('params', {}).get('data', {}).get('volume')
                self._post_event(MediaVolumeChangedEvent, volume=volume)

        return hndl

    def _on_ws_error(self):
        def hndl(*args):
            error = args[1] if len(args) > 1 else args[0]
            self.logger.warning("Kodi websocket connection error: %s", error)

        return hndl

    def _on_ws_close(self):
        def hndl(*_):
            self._ws = None
            self.logger.warning("Kodi websocket connection closed")
            time.sleep(5)
            self._websocket_thread()

        return hndl

    def _build_result(self, result):
        status = self.status().output
        status['result'] = result.get('result')
        return status, result.get('error')

    def _clear_resource(self):
        if self._latest_resource:
            self._latest_resource.close()
            self._latest_resource = None

    @action
    def play(self, resource: str, **kwargs):
        """
        Open and play the specified file or URL

        :param resource: URL or path to the media to be played
        """
        media = self._latest_resource = self._get_resource(resource, **kwargs)
        media.open(**kwargs)
        result = self._get_kodi().Player.Open(item={'file': media.resource})
        if self.volume:
            self.set_volume(volume=int(self.volume))

        return self._build_result(result)

    @action
    def pause(self, player_id=None, **_):
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
    def get_movies(self, **_):
        """
        Get the list of movies on the Kodi server
        """

        result = self._get_kodi().VideoLibrary.GetMovies()
        return result.get('result'), result.get('error')

    @action
    def stop(self, player_id=None, **_):
        """
        Stop the current media
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        result = self._get_kodi().Player.Stop(playerid=player_id)
        self._clear_resource()
        return self._build_result(result)

    @action
    def notify(self, title, message, **_):
        """
        Send a notification to the Kodi UI
        """

        result = self._get_kodi().GUI.ShowNotification(title=title, message=message)
        return result.get('result'), result.get('error')

    @action
    def left(self, **_):
        """
        Simulate a left input event
        """

        result = self._get_kodi().Input.Left()
        return result.get('result'), result.get('error')

    @action
    def right(self, **_):
        """
        Simulate a right input event
        """

        result = self._get_kodi().Input.Right()
        return result.get('result'), result.get('error')

    @action
    def up(self, **_):
        """
        Simulate an up input event
        """

        result = self._get_kodi().Input.Up()
        return result.get('result'), result.get('error')

    @action
    def down(self, **_):
        """
        Simulate a down input event
        """

        result = self._get_kodi().Input.Down()
        return result.get('result'), result.get('error')

    @action
    def back_btn(self, **_):
        """
        Simulate a back input event
        """

        result = self._get_kodi().Input.Back()
        return result.get('result'), result.get('error')

    @action
    def select(self, **_):
        """
        Simulate a select input event
        """

        result = self._get_kodi().Input.Select()
        return result.get('result'), result.get('error')

    @action
    def send_text(self, text, **_):
        """
        Simulate a send_text input event

        :param text: Text to send
        :type text: str
        """

        result = self._get_kodi().Input.SendText(text=text)
        return result.get('result'), result.get('error')

    @action
    def get_volume(self, **_):
        result = self._get_kodi().Application.GetProperties(properties=['volume'])

        return result.get('result'), result.get('error')

    @action
    def volup(self, step=10.0, **_):
        """Volume up (default: +10%)"""
        volume = (
            self._get_kodi()
            .Application.GetProperties(properties=['volume'])
            .get('result', {})
            .get('volume')
        )

        result = self._get_kodi().Application.SetVolume(
            volume=int(min(volume + step, 100))
        )
        return self._build_result(result)

    @action
    def voldown(self, step=10.0, **_):
        """Volume down (default: -10%)"""
        volume = (
            self._get_kodi()
            .Application.GetProperties(properties=['volume'])
            .get('result', {})
            .get('volume')
        )

        result = self._get_kodi().Application.SetVolume(
            volume=int(max(volume - step, 0))
        )
        return self._build_result(result)

    @action
    def set_volume(self, volume, **_):
        """
        Set the application volume

        :param volume: Volume to set between 0 and 100
        :type volume: int
        """

        result = self._get_kodi().Application.SetVolume(volume=int(volume))
        return self._build_result(result)

    @action
    def mute(self, **_):
        """
        Mute/unmute the application
        """

        muted = (
            self._get_kodi()
            .Application.GetProperties(properties=['muted'])
            .get('result', {})
            .get('muted')
        )

        result = self._get_kodi().Application.SetMute(mute=(not muted))
        return self._build_result(result)

    @action
    def is_muted(self, **_):
        """
        Return the muted status of the application
        """

        result = self._get_kodi().Application.GetProperties(properties=['muted'])
        return result.get('result')

    @action
    def scan_video_library(self, **_):
        """
        Scan the video library
        """

        result = self._get_kodi().VideoLibrary.Scan()
        return result.get('result'), result.get('error')

    @action
    def scan_audio_library(self, **_):
        """
        Scan the audio library
        """

        result = self._get_kodi().AudioLibrary.Scan()
        return result.get('result'), result.get('error')

    @action
    def clean_video_library(self, **_):
        """
        Clean the video library
        """

        result = self._get_kodi().VideoLibrary.Clean()
        return result.get('result'), result.get('error')

    @action
    def clean_audio_library(self, **_):
        """
        Clean the audio library
        """

        result = self._get_kodi().AudioLibrary.Clean()
        return result.get('result'), result.get('error')

    @action
    def quit(self, **_):
        """
        Quit the application
        """

        result = self._get_kodi().Application.Quit()
        self._clear_resource()
        return result.get('result'), result.get('error')

    @action
    def get_songs(self, **_):
        """
        Get the list of songs in the audio library
        """

        result = self._get_kodi().Application.GetSongs()
        return result.get('result'), result.get('error')

    @action
    def get_artists(self, **_):
        """
        Get the list of artists in the audio library
        """

        result = self._get_kodi().Application.GetArtists()
        return result.get('result'), result.get('error')

    @action
    def get_albums(self, **_):
        """
        Get the list of albums in the audio library
        """

        result = self._get_kodi().Application.GetAlbums()
        return result.get('result'), result.get('error')

    @action
    def fullscreen(self, **_):
        """
        Set/unset fullscreen mode
        """

        fullscreen = (
            self._get_kodi()
            .GUI.GetProperties(properties=['fullscreen'])
            .get('result', {})
            .get('fullscreen')
        )

        result = self._get_kodi().GUI.SetFullscreen(fullscreen=(not fullscreen))
        return result.get('result'), result.get('error')

    @action
    def shuffle(self, player_id=None, shuffle=None, **_):
        """
        Set/unset shuffle mode
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        if shuffle is None:
            shuffle = (
                self._get_kodi()
                .Player.GetProperties(playerid=player_id, properties=['shuffled'])
                .get('result', {})
                .get('shuffled')
            )

        result = self._get_kodi().Player.SetShuffle(
            playerid=player_id, shuffle=(not shuffle)
        )
        return result.get('result'), result.get('error')

    @action
    def repeat(self, player_id=None, repeat=None, **_):
        """
        Set/unset repeat mode
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        if repeat is None:
            repeat = (
                self._get_kodi()
                .Player.GetProperties(playerid=player_id, properties=['repeat'])
                .get('result', {})
                .get('repeat')
            )

        result = self._get_kodi().Player.SetRepeat(
            playerid=player_id, repeat='off' if repeat in ('one', 'all') else 'off'
        )

        return result.get('result'), result.get('error')

    @staticmethod
    def _time_pos_to_obj(t):
        hours = int(t / 3600)
        minutes = int((t - hours * 3600) / 60)
        seconds = t - hours * 3600 - minutes * 60
        milliseconds = t - int(t)

        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'milliseconds': milliseconds,
        }

    @staticmethod
    def _time_obj_to_pos(t):
        return (
            t.get('hours', 0) * 3600
            + t.get('minutes', 0) * 60
            + t.get('seconds', 0)
            + t.get('milliseconds', 0) / 1000
        )

    @action
    def seek(self, position, player_id=None, **_):
        """
        Move to the specified time position in seconds

        :param position: Seek time in seconds
        :type position: float
        :param player_id: ID of the target player (default: configured/current player).
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
        :param player_id: ID of the target player (default: configured/current player).
        """
        return self.seek(*args, position=position, player_id=player_id, **kwargs)

    @action
    def back(self, offset=30, player_id=None, **_):
        """
        Move the player execution backward by delta_seconds

        :param offset: Backward seek duration (default: 30 seconds)
        :type offset: float
        :param player_id: ID of the target player (default: configured/current player).
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        position = (
            self._get_kodi()
            .Player.GetProperties(playerid=player_id, properties=['time'])
            .get('result', {})
            .get('time', {})
        )

        position = self._time_obj_to_pos(position) - offset
        return self.seek(player_id=player_id, position=position)

    @action
    def forward(self, offset=30, player_id=None, **_):
        """
        Move the player execution forward by delta_seconds

        :param offset: Forward seek duration (default: 30 seconds)
        :type offset: float
        :param player_id: ID of the target player (default: configured/current player).
        """

        if player_id is None:
            player_id = self._get_player_id()
        if player_id is None:
            return None, 'No active players found'

        position = (
            self._get_kodi()
            .Player.GetProperties(playerid=player_id, properties=['time'])
            .get('result', {})
            .get('time', {})
        )

        position = self._time_obj_to_pos(position) + offset
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
        except Exception as e:
            self.logger.debug(f'Could not get active players: {str(e)}')
            return ret

        ret['state'] = PlayerState.STOP.value
        app = kodi.Application.GetProperties(
            properties=list(set(app_props.values()))
        ).get('result', {})

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

        media = (
            kodi.Player.GetItem(
                playerid=player_id, properties=list(set(media_props.values()))
            )
            .get('result', {})
            .get('item', {})
        )

        for status_prop, kodi_prop in media_props.items():
            ret[status_prop] = media.get(kodi_prop)

        player_info = kodi.Player.GetProperties(
            playerid=player_id, properties=list(set(player_props.values()))
        ).get('result', {})

        for status_prop, kodi_prop in player_props.items():
            ret[status_prop] = player_info.get(kodi_prop)

        if ret['duration']:
            ret['duration'] = self._time_obj_to_pos(ret['duration'])

        if ret['position']:
            ret['position'] = self._time_obj_to_pos(ret['position'])

        ret['state'] = (
            PlayerState.PAUSE.value
            if player_info.get('speed', 0) == 0
            else PlayerState.PLAY.value
        )
        return ret

    def toggle_subtitles(self, *_, **__):
        raise NotImplementedError

    def set_subtitles(self, *_, **__):
        raise NotImplementedError

    def remove_subtitles(self, *_, **__):
        raise NotImplementedError

    def is_playing(self, *_, **__):
        raise NotImplementedError

    def load(self, *_, **__):
        raise NotImplementedError

    @property
    def supports_local_media(self) -> bool:
        return False

    @property
    def supports_local_pipe(self) -> bool:
        return False


# vim:sw=4:ts=4:et:
