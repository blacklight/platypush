import json
import re
import threading

import websocket

from platypush.backend import Backend
from platypush.message.event.music import MusicPlayEvent, MusicPauseEvent, \
    MusicStopEvent, NewPlayingTrackEvent, PlaylistChangeEvent, VolumeChangeEvent, \
    PlaybackConsumeModeChangeEvent, PlaybackSingleModeChangeEvent, \
    PlaybackRepeatModeChangeEvent, PlaybackRandomModeChangeEvent, \
    MuteChangeEvent, SeekChangeEvent


# noinspection PyUnusedLocal
class MusicMopidyBackend(Backend):
    """
    This backend listens for events on a Mopidy music server streaming port.
    Since this backend leverages the Mopidy websocket interface it is only
    compatible with Mopidy and not with other MPD servers. Please use the
    :class:`platypush.backend.music.mpd.MusicMpdBackend` for a similar polling
    solution if you're not running Mopidy or your instance has the websocket
    interface or web port disabled.

    Triggers:

        * :class:`platypush.message.event.music.MusicPlayEvent` if the playback state changed to play
        * :class:`platypush.message.event.music.MusicPauseEvent` if the playback state changed to pause
        * :class:`platypush.message.event.music.MusicStopEvent` if the playback state changed to stop
        * :class:`platypush.message.event.music.NewPlayingTrackEvent` if a new track is being played
        * :class:`platypush.message.event.music.PlaylistChangeEvent` if the main playlist has changed
        * :class:`platypush.message.event.music.VolumeChangeEvent` if the main volume has changed
        * :class:`platypush.message.event.music.MuteChangeEvent` if the mute status has changed
        * :class:`platypush.message.event.music.SeekChangeEvent` if a track seek event occurs

    Requires:

        * Mopidy installed and the HTTP service enabled
    """

    def __init__(self, host='localhost', port=6680, **kwargs):
        super().__init__(**kwargs)

        self.host = host
        self.port = int(port)
        self.url = 'ws://{}:{}/mopidy/ws'.format(host, port)
        self._msg_id = 0
        self._ws = None
        self._latest_status = {}
        self._reconnect_thread = None
        self._connected_event = threading.Event()

        try:
            self._latest_status = self._get_tracklist_status()
        except Exception as e:
            self.logger.warning('Unable to get mopidy status: {}'.format(str(e)))

    @staticmethod
    def _parse_track(track, pos=None):
        if not track:
            return {}

        conv_track = track.get('track', {}).copy()
        conv_track['id'] = track.get('tlid')
        conv_track['file'] = conv_track['uri']
        del conv_track['uri']

        if 'artists' in conv_track:
            conv_track['artist'] = conv_track['artists'][0].get('name')
            del conv_track['artists']

        if 'name' in conv_track:
            conv_track['title'] = conv_track['name']
            del conv_track['name']

        if 'album' in conv_track:
            conv_track['album'] = conv_track['album']['name']

        if 'length' in conv_track:
            conv_track['time'] = conv_track['length']/1000 \
                if conv_track['length'] else conv_track['length']
            del conv_track['length']

        if pos is not None:
            conv_track['pos'] = pos

        if '__model__' in conv_track:
            del conv_track['__model__']

        return conv_track

    def _communicate(self, msg):

        if isinstance(msg, str):
            msg = json.loads(msg)

        self._msg_id += 1
        msg['jsonrpc'] = '2.0'
        msg['id'] = self._msg_id
        msg = json.dumps(msg)

        ws = websocket.create_connection(self.url)
        ws.send(msg)
        response = json.loads(ws.recv()).get('result')
        ws.close()
        return response

    def _get_tracklist_status(self):
        return {
            'repeat': self._communicate({
                'method': 'core.tracklist.get_repeat'}),
            'random': self._communicate({
                'method': 'core.tracklist.get_random'}),
            'single': self._communicate({
                'method': 'core.tracklist.get_single'}),
            'consume': self._communicate({
                'method': 'core.tracklist.get_consume'}),
        }

    def _on_msg(self):
        def hndl(*args):
            msg = args[1] if len(args) > 1 else args[0]
            msg = json.loads(msg)
            event = msg.get('event')
            if not event:
                return

            status = {}
            track = msg.get('tl_track', {})

            if event == 'track_playback_paused':
                status['state'] = 'pause'
                track = self._parse_track(track)
                if not track:
                    return
                self.bus.post(MusicPauseEvent(status=status, track=track, plugin_name='music.mpd'))
            elif event == 'track_playback_resumed':
                status['state'] = 'play'
                track = self._parse_track(track)
                if not track:
                    return
                self.bus.post(MusicPlayEvent(status=status, track=track, plugin_name='music.mpd'))
            elif event == 'track_playback_ended' or (
                    event == 'playback_state_changed'
                    and msg.get('new_state') == 'stopped'):
                status['state'] = 'stop'
                track = self._parse_track(track)
                self.bus.post(MusicStopEvent(status=status, track=track, plugin_name='music.mpd'))
            elif event == 'track_playback_started':
                track = self._parse_track(track)
                if not track:
                    return

                status['state'] = 'play'
                status['position'] = 0.0
                status['time'] = track.get('time')
                self.bus.post(NewPlayingTrackEvent(status=status, track=track, plugin_name='music.mpd'))
            elif event == 'stream_title_changed':
                m = re.match('^\s*(.+?)\s+-\s+(.*)\s*$', msg.get('title', ''))
                if not m:
                    return

                track['artist'] = m.group(1)
                track['title'] = m.group(2)
                status['state'] = 'play'
                status['position'] = 0.0
                self.bus.post(NewPlayingTrackEvent(status=status, track=track, plugin_name='music.mpd'))
            elif event == 'volume_changed':
                status['volume'] = msg.get('volume')
                self.bus.post(VolumeChangeEvent(volume=status['volume'], status=status, track=track,
                                                plugin_name='music.mpd'))
            elif event == 'mute_changed':
                status['mute'] = msg.get('mute')
                self.bus.post(MuteChangeEvent(mute=status['mute'], status=status, track=track,
                                              plugin_name='music.mpd'))
            elif event == 'seeked':
                status['position'] = msg.get('time_position')/1000
                self.bus.post(SeekChangeEvent(position=status['position'], status=status, track=track,
                                              plugin_name='music.mpd'))
            elif event == 'tracklist_changed':
                tracklist = [self._parse_track(t, pos=i)
                             for i, t in enumerate(self._communicate({
                                'method': 'core.tracklist.get_tl_tracks'}))]

                self.bus.post(PlaylistChangeEvent(changes=tracklist, plugin_name='music.mpd'))
            elif event == 'options_changed':
                new_status = self._get_tracklist_status()
                if new_status['random'] != self._latest_status.get('random'):
                    self.bus.post(PlaybackRandomModeChangeEvent(state=new_status['random'], plugin_name='music.mpd'))
                if new_status['repeat'] != self._latest_status['repeat']:
                    self.bus.post(PlaybackRepeatModeChangeEvent(state=new_status['repeat'], plugin_name='music.mpd'))
                if new_status['single'] != self._latest_status['single']:
                    self.bus.post(PlaybackSingleModeChangeEvent(state=new_status['single'], plugin_name='music.mpd'))
                if new_status['consume'] != self._latest_status['consume']:
                    self.bus.post(PlaybackConsumeModeChangeEvent(state=new_status['consume'], plugin_name='music.mpd'))

                self._latest_status = new_status

        return hndl

    def _retry_connect(self):
        def reconnect():
            while not self.should_stop() and not self._connected_event.is_set():
                try:
                    self._connect()
                except Exception as e:
                    self.logger.warning('Error on websocket reconnection: '.format(str(e)))

                self._connected_event.wait(timeout=10)

            self._reconnect_thread = None

        if not self._reconnect_thread or not self._reconnect_thread.is_alive():
            self._reconnect_thread = threading.Thread(target=reconnect)
            self._reconnect_thread.start()

    def _on_error(self):
        def hndl(*args):
            error = args[1] if len(args) > 1 else args[0]
            ws = args[0] if len(args) > 1 else None
            self.logger.warning('Mopidy websocket error: {}'.format(error))
            if ws:
                ws.close()

        return hndl

    def _on_close(self):
        def hndl(*_):
            self._connected_event.clear()
            self._ws = None
            self.logger.warning('Mopidy websocket connection closed')

            if not self.should_stop():
                self._retry_connect()

        return hndl

    def _on_open(self):
        def hndl(*_):
            self._connected_event.set()
            self.logger.info('Mopidy websocket connected')

        return hndl

    def _connect(self):
        if not self._ws:
            self._ws = websocket.WebSocketApp(self.url,
                                              on_open=self._on_open(),
                                              on_message=self._on_msg(),
                                              on_error=self._on_error(),
                                              on_close=self._on_close())

            self._ws.run_forever()

    def run(self):
        super().run()
        self.logger.info('Started tracking Mopidy events backend on {}:{}'.format(self.host, self.port))
        self._connect()

    def on_stop(self):
        self.logger.info('Received STOP event on the Mopidy backend')
        if self._ws:
            self._ws.close()

        self.logger.info('Mopidy backend terminated')


# vim:sw=4:ts=4:et:
