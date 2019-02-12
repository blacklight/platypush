import asyncio
import time

from platypush.backend import Backend
from platypush.message.event.music import MusicPlayEvent, MusicPauseEvent, \
    MusicStopEvent, NewPlayingTrackEvent, PlaylistChangeEvent, VolumeChangeEvent, \
    PlaybackConsumeModeChangeEvent, PlaybackSingleModeChangeEvent, \
    PlaybackRepeatModeChangeEvent, PlaybackRandomModeChangeEvent


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

    Requires:
        * **websockets** (``pip install websockets``)
        * Mopidy installed and the HTTP service enabled
    """

    def __init__(self, server='localhost', port=6680, **kwargs):
        super().__init__(**kwargs)

        self.server = server
        self.port = int(port)
        self.url = 'ws://{}:{}/mopidy/ws'.format(server, port)

    async def poll_events(self):
        import websockets

        try:
            while not self.should_stop():
                async with websockets.connect(self.url) as ws:
                    msg = await ws.recv()
                    # TODO handle the message
        except Exception as e:
            self.logger.warning('The Mopidy backend raised an exception')
            self.logger.exception(e)
            time.sleep(2)  # Wait a bit before retrying

    def run(self):
        super().run()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while not self.should_stop():
            loop.run_until_complete(self.poll_events())


# vim:sw=4:ts=4:et:
