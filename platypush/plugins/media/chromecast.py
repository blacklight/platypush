import datetime
import re
import time

from platypush.context import get_plugin, get_bus
from platypush.plugins import action
from platypush.plugins.media import MediaPlugin
from platypush.utils import get_mime_type
from platypush.message.event.media import MediaPlayEvent, MediaPlayRequestEvent, \
    MediaStopEvent, MediaPauseEvent, NewPlayingMediaEvent, MediaVolumeChangedEvent, MediaSeekEvent


def convert_status(status):
    attrs = [a for a in dir(status) if not a.startswith('_')
             and not callable(getattr(status, a))]

    renamed_attrs = {
        'current_time': 'position',
        'player_state': 'state',
        'supports_seek': 'seekable',
        'volume_level': 'volume',
        'volume_muted': 'mute',
        'content_id': 'url',
    }

    ret = {}
    for attr in attrs:
        value = getattr(status, attr)
        if attr == 'volume_level':
            value *= 100
        if attr == 'player_state':
            value = value.lower()
            if value == 'paused':
                value = 'pause'
            if value == 'playing':
                value = 'play'
        if isinstance(value, datetime.datetime):
            value = value.isoformat()

        if attr in renamed_attrs:
            ret[renamed_attrs[attr]] = value
        else:
            ret[attr] = value

    return ret


def post_event(evt_type, **evt):
    bus = get_bus()
    bus.post(evt_type(player=evt.get('device'), plugin='media.chromecast', **evt))


class MediaChromecastPlugin(MediaPlugin):
    """
    Plugin to interact with Chromecast devices

    Supported formats:

        * HTTP media URLs
        * YouTube URLs
        * Plex (through ``media.plex`` plugin, experimental)

    Requires:

        * **pychromecast** (``pip install pychromecast``)
    """

    STREAM_TYPE_UNKNOWN = "UNKNOWN"
    STREAM_TYPE_BUFFERED = "BUFFERED"
    STREAM_TYPE_LIVE = "LIVE"

    class MediaListener:
        def __init__(self, name, cast):
            self.name = name
            self.cast = cast
            self.status = convert_status(cast.media_controller.status)
            self.last_status_timestamp = time.time()

        def new_media_status(self, status):
            status = convert_status(status)

            if status.get('url') and status.get('url') != self.status.get('url'):
                post_event(NewPlayingMediaEvent, resource=status['url'],
                           title=status.get('title'), device=self.name)
            if status.get('state') != self.status.get('state'):
                if status.get('state') == 'play':
                    post_event(MediaPlayEvent, resource=status['url'], device=self.name)
                elif status.get('state') == 'pause':
                    post_event(MediaPauseEvent, resource=status['url'], device=self.name)
                elif status.get('state') in ['stop', 'idle']:
                    post_event(MediaStopEvent, device=self.name)
            if status.get('volume') != self.status.get('volume'):
                post_event(MediaVolumeChangedEvent, volume=status.get('volume'), device=self.name)
            if abs(status.get('position') - self.status.get('position')) > time.time() - self.last_status_timestamp + 5:
                post_event(MediaSeekEvent, position=status.get('position'), device=self.name)

            self.last_status_timestamp = time.time()
            self.status = status

    class SubtitlesAsyncHandler:
        def __init__(self, mc, subtitle_id):
            self.mc = mc
            self.subtitle_id = subtitle_id
            self.initialized = False

        # pylint: disable=unused-argument
        def new_media_status(self, status):
            if self.subtitle_id and not self.initialized:
                self.mc.update_status()
                self.mc.enable_subtitle(self.subtitle_id)
                self.initialized = True

    def __init__(self, chromecast=None, *args, **kwargs):
        """
        :param chromecast: Default Chromecast to cast to if no name is specified
        :type chromecast: str
        """

        super().__init__(*args, **kwargs)

        self._is_local = False
        self.chromecast = chromecast
        self.chromecasts = {}
        self._media_listeners = {}

    @staticmethod
    def _get_chromecasts(*args, **kwargs):
        import pychromecast
        chromecasts = pychromecast.get_chromecasts(*args, **kwargs)
        if isinstance(chromecasts, tuple):
            return chromecasts[0]
        return chromecasts

    @action
    def get_chromecasts(self, tries=2, retry_wait=10, timeout=60,
                        blocking=True, callback=None):
        """
        Get the list of Chromecast devices

        :param tries: Number of retries (default: 2)
        :type tries: int

        :param retry_wait: Number of seconds between retries (default: 10 seconds)
        :type retry_wait: int

        :param timeout: Timeout before failing the call (default: 60 seconds)
        :type timeout: int

        :param blocking: If true, then the function will block until all the Chromecast
            devices have been scanned. If false, then the provided callback function will be
            invoked when a new device is discovered
        :type blocking: bool

        :param callback: If blocking is false, then you can provide a callback function that
            will be invoked when a new device is discovered
        :type callback: func
        """

        import pychromecast
        self.chromecasts.update({
            cast.device.friendly_name: cast
            for cast in self._get_chromecasts(tries=tries, retry_wait=retry_wait,
                                              timeout=timeout, blocking=blocking,
                                              callback=callback)
        })

        for name, cast in self.chromecasts.items():
            self._update_listeners(name, cast)

        return [{
            'type': cc.cast_type,
            'name': cc.name,
            'manufacturer': cc.device.manufacturer,
            'model_name': cc.model_name,
            'uuid': str(cc.device.uuid),
            'address': cc.host,
            'port': cc.port,

            'status': ({
                'app': {
                    'id': cc.app_id,
                    'name': cc.app_display_name,
                },

                'media': self.status(cc.name).output,
                'is_active_input': cc.status.is_active_input,
                'is_stand_by': cc.status.is_stand_by,
                'is_idle': cc.is_idle,
                'namespaces': cc.status.namespaces,
                'volume': round(100*cc.status.volume_level, 2),
                'muted': cc.status.volume_muted,
            } if cc.status else {}),
        } for cc in self.chromecasts.values()]

    def _update_listeners(self, name, cast):
        if name not in self._media_listeners:
            cast.start()
            self._media_listeners[name] = self.MediaListener(name=name, cast=cast)
            cast.media_controller.register_status_listener(self._media_listeners[name])

    def get_chromecast(self, chromecast=None, n_tries=2):
        import pychromecast
        if isinstance(chromecast, pychromecast.Chromecast):
            return chromecast

        if not chromecast:
            if not self.chromecast:
                raise RuntimeError('No Chromecast specified nor default Chromecast configured')
            chromecast = self.chromecast

        if chromecast not in self.chromecasts:
            casts = {}
            while n_tries > 0:
                n_tries -= 1
                casts.update({
                    cast.device.friendly_name: cast
                    for cast in self._get_chromecasts()
                })

                if chromecast in casts:
                    self.chromecasts.update(casts)
                    break

            if chromecast not in self.chromecasts:
                raise RuntimeError('Device {} not found'.format(chromecast))

        cast = self.chromecasts[chromecast]
        cast.wait()
        return cast

    @action
    def play(self, resource, content_type=None, chromecast=None, title=None,
             image_url=None, autoplay=True, current_time=0,
             stream_type=STREAM_TYPE_BUFFERED, subtitles=None,
             subtitles_lang='en-US', subtitles_mime='text/vtt',
             subtitle_id=1):
        """
        Cast media to a visible Chromecast

        :param resource: Media to cast
        :type resource: str

        :param content_type: Content type as a MIME type string
        :type content_type: str

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str

        :param title: Optional title
        :type title: str

        :param image_url: URL of the image to use for the thumbnail
        :type image_url: str

        :param autoplay: Set it to false if you don't want the content to start playing immediately (default: true)
        :type autoplay: bool

        :param current_time: Time to start the playback in seconds (default: 0)
        :type current_time: int

        :param stream_type: Type of stream to cast. Can be BUFFERED (default), LIVE or UNKNOWN
        :type stream_type: str

        :param subtitles: URL of the subtitles to be shown
        :type subtitles: str

        :param subtitles_lang: Subtitles language (default: en-US)
        :type subtitles_lang: str

        :param subtitles_mime: Subtitles MIME type (default: text/vtt)
        :type subtitles_mime: str

        :param subtitle_id: ID of the subtitles to be loaded (default: 1)
        :type subtitle_id: int
        """

        from pychromecast.controllers.youtube import YouTubeController
        if not chromecast:
            chromecast = self.chromecast

        post_event(MediaPlayRequestEvent, resource=resource, device=chromecast)
        cast = self.get_chromecast(chromecast)

        mc = cast.media_controller
        yt = self._get_youtube_url(resource)

        if yt:
            self.logger.info('Playing YouTube video {} on {}'.format(
                yt, chromecast))

            hndl = YouTubeController()
            cast.register_handler(hndl)
            hndl.update_screen_id()
            return hndl.play_video(yt)

        resource = self._get_resource(resource)

        if resource.startswith('magnet:?'):
            player_args = {'chromecast': chromecast}
            return get_plugin('media.webtorrent').play(resource,
                                                       player='chromecast',
                                                       **player_args)

        if not content_type:
            content_type = get_mime_type(resource)

        if not content_type:
            raise RuntimeError('content_type required to process media {}'.
                               format(resource))

        if not resource.startswith('http://') and \
                not resource.startswith('https://'):
            resource = self.start_streaming(resource).output['url']
            self.logger.info('HTTP media stream started on {}'.format(resource))

        self.logger.info('Playing {} on {}'.format(resource, chromecast))

        mc.play_media(resource, content_type, title=title, thumb=image_url,
                      current_time=current_time, autoplay=autoplay,
                      stream_type=stream_type, subtitles=subtitles,
                      subtitles_lang=subtitles_lang,
                      subtitles_mime=subtitles_mime, subtitle_id=subtitle_id)

        if subtitles:
            mc.register_status_listener(self.SubtitlesAsyncHandler(mc, subtitle_id))

        mc.block_until_active()

        if self.volume:
            self.set_volume(volume=self.volume, chromecast=chromecast)

        return self.status(chromecast=chromecast)

    @classmethod
    def _get_youtube_url(cls, url):
        m = re.match('https?://www.youtube.com/watch\?v=([^&]+).*', url)
        if m:
            return m.group(1)

        m = re.match('youtube:video:(.*)', url)
        if m:
            return m.group(1)

        return None

    @action
    def load(self, *args, **kwargs):
        return self.play(*args, **kwargs)

    @action
    def pause(self, chromecast=None):
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)

        if cast.media_controller.is_paused:
            cast.media_controller.play()
        elif cast.media_controller.is_playing:
            cast.media_controller.pause()

        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def stop(self, chromecast=None):
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.media_controller.stop()
        cast.wait()

        return self.status(chromecast=chromecast)

    @action
    def rewind(self, chromecast=None):
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.media_controller.rewind()
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def set_position(self, position, chromecast=None):
        cast = self.get_chromecast(chromecast or self.chromecast)
        cast.media_controller.seek(position)
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def seek(self, position, chromecast=None):
        return self.forward(chromecast=chromecast, offset=position)

    @action
    def back(self, chromecast=None, offset=60):
        cast = self.get_chromecast(chromecast or self.chromecast)
        mc = cast.media_controller
        if mc.status.current_time:
            mc.seek(mc.status.current_time-offset)
            cast.wait()

        return self.status(chromecast=chromecast)

    @action
    def forward(self, chromecast=None, offset=60):
        cast = self.get_chromecast(chromecast or self.chromecast)
        mc = cast.media_controller
        if mc.status.current_time:
            mc.seek(mc.status.current_time+offset)
            cast.wait()

        return self.status(chromecast=chromecast)

    @action
    def is_playing(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.is_playing

    @action
    def is_paused(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.is_paused

    @action
    def is_idle(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.is_idle

    @action
    def list_subtitles(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast) \
            .media_controller.subtitle_tracks

    @action
    def enable_subtitles(self, chromecast=None, track_id=None):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        if track_id is not None:
            return mc.enable_subtitle(track_id)
        elif mc.subtitle_tracks:
            return mc.enable_subtitle(mc.subtitle_tracks[0].get('trackId'))

    @action
    def disable_subtitles(self, chromecast=None, track_id=None):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        if track_id:
            return mc.disable_subtitle(track_id)
        elif mc.current_subtitle_tracks:
            return mc.disable_subtitle(mc.current_subtitle_tracks[0])

    @action
    def toggle_subtitles(self, chromecast=None):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        all_subs = mc.status.subtitle_tracks
        cur_subs = mc.status.status.current_subtitle_tracks

        if cur_subs:
            return self.disable_subtitles(chromecast, cur_subs[0])
        else:
            return self.enable_subtitles(chromecast, all_subs[0].get('trackId'))

    @action
    def status(self, chromecast=None):
        cast = self.get_chromecast(chromecast or self.chromecast)
        status = cast.media_controller.status
        return convert_status(status)

    @action
    def disconnect(self, chromecast=None, timeout=None, blocking=True):
        """
        Disconnect a Chromecast and wait for it to terminate

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str

        :param timeout: Number of seconds to wait for disconnection (default: None: block until termination)
        :type timeout: float

        :param blocking: If set (default), then the code will wait until disconnection, otherwise it will return
            immediately.
        :type blocking: bool
        """

        cast = self.get_chromecast(chromecast)
        cast.disconnect(timeout=timeout, blocking=blocking)

    @action
    def join(self, chromecast=None, timeout=None):
        """
        Blocks the thread until the Chromecast connection is terminated.

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str

        :param timeout: Number of seconds to wait for disconnection (default: None: block until termination)
        :type timeout: float
        """

        cast = self.get_chromecast(chromecast)
        cast.join(timeout=timeout)

    @action
    def quit(self, chromecast=None):
        """
        Exits the current app on the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str
        """

        cast = self.get_chromecast(chromecast)
        cast.quit_app()

    @action
    def reboot(self, chromecast=None):
        """
        Reboots the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str
        """

        cast = self.get_chromecast(chromecast)
        cast.reboot()

    @action
    def set_volume(self, volume, chromecast=None):
        """
        Set the Chromecast volume

        :param volume: Volume to be set, between 0 and 100
        :type volume: float

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str
        """

        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.set_volume(volume/100)
        cast.wait()
        status = self.status(chromecast=chromecast)
        status.output['volume'] = volume
        return status

    @action
    def volup(self, chromecast=None, step=10):
        """
        Turn up the Chromecast volume by 10% or step.

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str

        :param step: Volume increment between 0 and 100 (default: 100%)
        :type step: float
        """

        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        step /= 100
        cast.volume_up(min(step, 1))
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def voldown(self, chromecast=None, step=10):
        """
        Turn down the Chromecast volume by 10% or step.

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str

        :param step: Volume decrement between 0 and 100 (default: 100%)
        :type step: float
        """

        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        step /= 100
        cast.volume_down(max(step, 0))
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def mute(self, chromecast=None):
        """
        Toggle the mute status on the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast
            will be used.
        :type chromecast: str
        """

        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.set_volume_muted(not cast.status.volume_muted)
        cast.wait()
        return self.status(chromecast=chromecast)


# vim:sw=4:ts=4:et:
