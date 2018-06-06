import re
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.music import MusicPlayEvent, MusicPauseEvent, \
    MusicStopEvent, NewPlayingTrackEvent, PlaylistChangeEvent


class MusicMpdBackend(Backend):
    def __init__(self, server='localhost', port=6600, poll_seconds=3, **kwargs):
        super().__init__(**kwargs)

        self.server = server
        self.port = port
        self.poll_seconds = poll_seconds


    def send_message(self, msg):
        pass


    def run(self):
        super().run()

        last_state = None
        last_track = None
        last_playlist = None
        plugin = None

        while not self.should_stop():
            success = False

            while not success:
                try:
                    plugin = get_plugin('music.mpd')
                    status = plugin.status().output
                    track = plugin.currentsong().output
                    state = status['state'].lower()
                    playlist = status['playlist']
                    success = True
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.info('Reloading crashed MPD plugin')
                    plugin = get_plugin('music.mpd', reload=True)
                    time.sleep(self.poll_seconds)

            if state != last_state:
                if state == 'stop':
                    self.bus.post(MusicStopEvent(status=status, track=track))
                elif state == 'pause':
                    self.bus.post(MusicPauseEvent(status=status, track=track))
                elif state == 'play':
                    self.bus.post(MusicPlayEvent(status=status, track=track))

            if playlist != last_playlist:
                if last_playlist:
                    changes = plugin.plchanges(last_playlist).output
                    self.bus.post(PlaylistChangeEvent(changes=changes))
                last_playlist = playlist

            if state == 'play' and track != last_track:
                self.bus.post(NewPlayingTrackEvent(status=status, track=track))

            last_state = state
            last_track = track
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

