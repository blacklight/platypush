import datetime
import re
import pychromecast

from pychromecast.controllers.youtube import YouTubeController

from platypush.context import get_plugin
from platypush.plugins import Plugin, action
from platypush.plugins.media import MediaPlugin
from platypush.utils import get_mime_type


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

    def __init__(self, chromecast=None, *args, **kwargs):
        """
        :param chromecast: Default Chromecast to cast to if no name is specified
        :type chromecast: str
        """

        super().__init__(*args, **kwargs)

        self._is_local = False
        self.chromecast = chromecast
        self.chromecasts = {}


    @action
    def get_chromecasts(self):
        """
        Get the list of Chromecast devices
        """

        self.chromecasts.update({
            cast.device.friendly_name: cast
            for cast in pychromecast.get_chromecasts()
        })

        return [ {
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
        } for cc in self.chromecasts.values() ]


    def get_chromecast(self, chromecast=None, n_tries=3):
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
                    for cast in pychromecast.get_chromecasts()
                })

                if chromecast in casts:
                    self.chromecasts.update(casts)
                    break

            if chromecast not in self.chromecasts:
                raise RuntimeError('Device {} not found'.format(chromecast))

        return self.chromecasts[chromecast]


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

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
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

        if not chromecast:
            chromecast = self.chromecast

        cast = self.get_chromecast(chromecast)
        cast.wait()

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
            player_args = { 'chromecast': cast }
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
                      subtitles_lang=subtitles_lang, subtitles_mime=subtitles_mime,
                      subtitle_id=subtitle_id)

        mc.block_until_active()


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
        cast = self.get_chromecast(chromecast or self.chromecast)
        if cast.media_controller.is_paused:
            return cast.media_controller.play()
        elif cast.media_controller.is_playing:
            return cast.media_controller.pause()


    @action
    def stop(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.stop()


    @action
    def rewind(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.rewind()


    @action
    def set_position(self, position, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.seek(position)

    @action
    def seek(self, position, chromecast=None):
        return self.forward(chromecast=chromecast, offset=position)

    @action
    def back(self, chromecast=None, offset=60):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        if mc.status.current_time:
            return mc.seek(mc.status.current_time-offset)


    @action
    def forward(self, chromecast=None, offset=60):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        if mc.status.current_time:
            return mc.seek(mc.status.current_time+offset)


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
    def enable_subtitle(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.enable_subtitle()


    @action
    def disable_subtitle(self, chromecast=None):
        return self.get_chromecast(chromecast or self.chromecast).media_controller.disable_subtitle()


    @action
    def status(self, chromecast=None):
        status = self.get_chromecast(chromecast or self.chromecast) \
            .media_controller.status
        attrs = [a for a in dir(status) if not a.startswith('_')
                 and not callable(getattr(status, a))]
        renamed_attrs = {
            'player_state': 'state',
            'volume_level': 'volume',
            'volume_muted': 'muted',
        }

        ret = {}
        for attr in attrs:
            value = getattr(status, attr)
            if attr == 'volume_level':
                value *= 100
            if attr == 'player_state':
                value = value.lower()
                if value == 'paused': value = 'pause'
                if value == 'playing': value = 'play'
            if isinstance(value, datetime.datetime):
                value = value.isoformat()

            if attr in renamed_attrs:
                ret[renamed_attrs[attr]] = value
            else:
                ret[attr] = value

        return ret


    @action
    def disconnect(self, chromecast=None, timeout=None, blocking=True):
        """
        Disconnect a Chromecast and wait for it to terminate

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str

        :param timeout: Number of seconds to wait for disconnection (default: None: block until termination)
        :type timeout: float

        :param blocking: If set (default), then the code will wait until disconnection, otherwise it will return immediately.
        :type blocking: bool
        """

        cast = self.get_chromecast(chromecast)
        cast.disconnect(timeout=timeout, blocking=blocking)

    @action
    def join(self, chromecast=None, timeout=None, blocking=True):
        """
        Blocks the thread until the Chromecast connection is terminated.

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str

        :param timeout: Number of seconds to wait for disconnection (default: None: block until termination)
        :type timeout: float

        :param blocking: If set (default), then the code will wait until disconnection, otherwise it will return immediately.
        :type blocking: bool
        """

        cast = self.get_chromecast(chromecast)
        cast.join(timeout=timeout, blocking=blocking)

    @action
    def quit(self, chromecast=None):
        """
        Exits the current app on the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str
        """

        cast = self.get_chromecast(chromecast)
        cast.quit_app()

    @action
    def reboot(self, chromecast=None):
        """
        Reboots the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
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

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str
        """

        cast = self.get_chromecast(chromecast)
        cast.set_volume(volume/100)

    @action
    def volup(self, chromecast=None, step=10):
        """
        Turn up the Chromecast volume by 10% or step.

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str

        :param step: Volume increment between 0 and 100 (default: 100%)
        :type step: float
        """

        cast = self.get_chromecast(chromecast)
        step /= 100
        cast.volume_up(min(step, 1))


    @action
    def voldown(self, chromecast=None, step=10):
        """
        Turn down the Chromecast volume by 10% or step.

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str

        :param step: Volume decrement between 0 and 100 (default: 100%)
        :type step: float
        """

        cast = self.get_chromecast(chromecast)
        step /= 100
        cast.volume_down(max(step, 0))


    @action
    def mute(self, chromecast=None):
        """
        Toggle the mute status on the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then the default configured Chromecast will be used.
        :type chromecast: str
        """

        cast = self.get_chromecast(chromecast)
        cast.set_volume_muted(not cast.status.volume_muted)


# vim:sw=4:ts=4:et:
