import asyncio
import json
import queue
import re
import threading
import time

from platypush.backend import Backend
from platypush.message.event.music import MusicPlayEvent, MusicPauseEvent, \
    MusicStopEvent, NewPlayingTrackEvent, PlaylistChangeEvent, VolumeChangeEvent, \
    PlaybackConsumeModeChangeEvent, PlaybackSingleModeChangeEvent, \
    PlaybackRepeatModeChangeEvent, PlaybackRandomModeChangeEvent, \
    MuteChangeEvent, SeekChangeEvent


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
        * **websockets** (``pip install websockets``)
        * Mopidy installed and the HTTP service enabled
    """

    def __init__(self, host='localhost', port=6680, **kwargs):
        super().__init__(**kwargs)

        self.host = host
        self.port = int(port)
        self.url = 'ws://{}:{}/mopidy/ws'.format(host, port)
        self._msg_id = 0
        self._latest_status = self._get_tracklist_status()

    async def _poll_events(self):
        import websockets

        try:
            while not self.should_stop():
                async with websockets.connect(self.url) as ws:
                    msg = await ws.recv()
                    if isinstance(msg, bytes):
                        msg = msg.decode()
                self._handle_msg(msg)
        except Exception as e:
            self.logger.warning('The Mopidy backend raised an exception')
            self.logger.exception(e)
            time.sleep(2)  # Wait a bit before retrying

    def _parse_track(self, track, pos=None):
        if not track:
            return {}

        conv_track = track.get('track', {}).copy()
        conv_track['id'] = track.get('tlid')
        conv_track['file'] = conv_track['uri']
        del conv_track['uri']

        if 'artists' in conv_track:
            conv_track['artist'] = conv_track['artists'][0]
            del conv_track['artists']

        if 'album' in conv_track:
            conv_track['album'] = conv_track['album']['name']

        if 'length' in conv_track:
            conv_track['time'] = conv_track['length']/1000 \
                if conv_track['length'] else conv_track['length']
            del conv_track['length']

        if pos is not None:
            conv_track['pos'] = pos

        return conv_track


    def _communicate(self, msg):
        import websockets

        if isinstance(msg, str):
            msg = json.loads(msg)

        self._msg_id += 1
        msg['jsonrpc'] = '2.0'
        msg['id'] = self._msg_id
        msg = json.dumps(msg)
        resp_queue = queue.Queue()

        async def get_response():
            async with websockets.connect(self.url) as ws:
                await ws.send(msg)
                response = await ws.recv()
                if isinstance(response, bytes):
                    response = response.decode()
                resp_queue.put(json.loads(response))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_response())
        return resp_queue.get().get('result')

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

    def _handle_msg(self, msg):
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
            self.bus.post(MusicPauseEvent(status=status, track=track))
        elif event == 'track_playback_resumed':
            status['state'] = 'play'
            track = self._parse_track(track)
            if not track:
                return
            self.bus.post(MusicPlayEvent(status=status, track=track))
        elif event == 'track_playback_ended':
            status['state'] = 'stop'
            track = self._parse_track(track)
            if not track:
                return
            self.bus.post(MusicPlayEvent(status=status, track=track))
        elif event == 'track_playback_started':
            track = self._parse_track(track)
            if not track:
                return
            self.bus.post(NewPlayingTrackEvent(status=status, track=track))
        elif event == 'stream_title_changed':
            m = re.match('^\s*(.+?)\s+-\s+(.*)\s*$', msg.get('title', ''))
            if not m:
                return

            track['artist'] = m.group(1)
            track['title'] = m.group(2)
            self.bus.post(NewPlayingTrackEvent(status=status, track=track))
        elif event == 'volume_changed':
            status['volume'] = msg.get('volume')
            self.bus.post(VolumeChangeEvent(volume=status['volume'],
                                            status=status, track=track))
        elif event == 'mute_changed':
            status['mute'] = msg.get('mute')
            self.bus.post(MuteChangeEvent(mute=status['mute'],
                                          status=status, track=track))
        elif event == 'seeked':
            status['position'] = msg.get('time_position')
            self.bus.post(SeekChangeEvent(position=status['position'],
                                          status=status, track=track))
        elif event == 'tracklist_changed':
            tracklist = [self._parse_track(t, pos=i)
                         for i, t in self._communicate({
                             'method': 'core.tracklist.get_tl_tracks' })]

            self.bus.post(PlaylistChangeEvent(changes=tracklist))
        elif event == 'options_changed':
            new_status = self._get_tracklist_status()
            if new_status['random'] != self._latest_status['random']:
                self.bus.post(PlaybackRandomModeChangeEvent(state=new_status['random']))
            if new_status['repeat'] != self._latest_status['repeat']:
                self.bus.post(PlaybackRepeatModeChangeEvent(state=new_status['repeat']))
            if new_status['single'] != self._latest_status['single']:
                self.bus.post(PlaybackSingleModeChangeEvent(state=new_status['single']))
            if new_status['consume'] != self._latest_status['consume']:
                self.bus.post(PlaybackConsumeModeChangeEvent(state=new_status['consume']))

            self._latest_status = new_status

    def run(self):
        super().run()
        self.logger.info('Started Mopidy events backend on {}:{}'.format(
            self.host, self.port))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while not self.should_stop():
            loop.run_until_complete(self._poll_events())


# vim:sw=4:ts=4:et:
