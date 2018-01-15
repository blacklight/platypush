import logging
import re
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.music import \
    MusicPlayEvent, MusicPauseEvent, MusicStopEvent, NewPlayingTrackEvent


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

        plugin = get_plugin('music.mpd')
        last_state = None
        last_track = None

        while not self.should_stop():
            status = plugin.status().output
            state = status['state'].lower()
            track = plugin.currentsong().output

            if state != last_state:
                if state == 'stop':
                    self.bus.post(MusicStopEvent(status=status, track=track))
                elif state == 'pause':
                    self.bus.post(MusicPauseEvent(status=status, track=track))
                elif state == 'play':
                    self.bus.post(MusicPlayEvent(status=status, track=track))

            if 'title' in track and ('artist' not in track
                                        or not track['artist']
                                        or re.search('^tunein:', track['file'])):
                m = re.match('^\s*(.+?)\s+-\s+(.*)\s*$', track['title'])
                if m and m.group(1) and m.group(2):
                    track['artist'] = m.group(1)
                    track['title'] = m.group(2)

            if state == 'play' and track != last_track:
                self.bus.post(NewPlayingTrackEvent(status=status, track=track))

            last_state = state
            last_track = track
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

