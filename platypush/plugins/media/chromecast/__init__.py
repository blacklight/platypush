from typing import Optional

from pychromecast import (
    CastBrowser,
    Chromecast,
    ChromecastConnectionError,
    SimpleCastListener,
    get_chromecast_from_cast_info,
)

from platypush.backend.http.app.utils import get_remote_base_url
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.media import MediaPlugin
from platypush.utils import get_mime_type
from platypush.message.event.media import MediaPlayRequestEvent

from ._listener import MediaListener
from ._subtitles import SubtitlesAsyncHandler
from ._utils import convert_status, post_event


class MediaChromecastPlugin(MediaPlugin, RunnablePlugin):
    """
    Plugin to control Chromecast devices.
    """

    STREAM_TYPE_UNKNOWN = "UNKNOWN"
    STREAM_TYPE_BUFFERED = "BUFFERED"
    STREAM_TYPE_LIVE = "LIVE"

    def __init__(
        self, chromecast: Optional[str] = None, poll_interval: float = 30, **kwargs
    ):
        """
        :param chromecast: Default Chromecast to cast to if no name is specified.
        :param poll_interval: How often the plugin should poll for new/removed
            Chromecast devices (default: 30 seconds).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)

        self._is_local = False
        self.chromecast = chromecast
        self._chromecasts_by_uuid = {}
        self._chromecasts_by_name = {}
        self._media_listeners = {}
        self._zc = None
        self._browser = None

    @property
    def zc(self):
        from zeroconf import Zeroconf

        if not self._zc:
            self._zc = Zeroconf()

        return self._zc

    @property
    def browser(self):
        if not self._browser:
            self._browser = CastBrowser(
                SimpleCastListener(self._on_chromecast_discovered), self.zc
            )

            self._browser.start_discovery()

        return self._browser

    def _on_chromecast_discovered(self, _, service: str):
        self.logger.info('Discovered Chromecast: %s', service)

    @staticmethod
    def _get_device_property(cc, prop: str):
        if hasattr(cc, 'device'):  # Previous pychromecast API
            return getattr(cc.device, prop)
        return getattr(cc.cast_info, prop)

    def _serialize_device(self, cc: Chromecast) -> dict:
        """
        Convert a Chromecast object and its status to a dictionary.
        """
        if hasattr(cc, 'cast_info'):  # Newer PyChromecast API
            host = cc.cast_info.host
            port = cc.cast_info.port
        elif hasattr(cc, 'host'):
            host = getattr(cc, 'host', None)
            port = getattr(cc, 'port', None)
        elif hasattr(cc, 'uri'):
            host, port = cc.uri.split(':')
        else:
            raise RuntimeError('Invalid Chromecast object')

        return {
            'type': cc.cast_type,
            'name': cc.name,
            'manufacturer': self._get_device_property(cc, 'manufacturer'),
            'model_name': cc.model_name,
            'uuid': str(cc.uuid),
            'address': host,
            'port': port,
            'status': (
                {
                    'app': {
                        'id': cc.app_id,
                        'name': cc.app_display_name,
                    },
                    'is_active_input': cc.status.is_active_input,
                    'is_stand_by': cc.status.is_stand_by,
                    'is_idle': cc.is_idle,
                    'namespaces': cc.status.namespaces,
                    'volume': round(100 * cc.status.volume_level, 2),
                    'muted': cc.status.volume_muted,
                    **convert_status(cc.media_controller.status),
                }
                if cc.status
                else {}
            ),
        }

    def _event_callback(self, _, cast: Chromecast):
        self._chromecasts_by_uuid[cast.uuid] = cast
        self._chromecasts_by_name[
            self._get_device_property(cast, 'friendly_name')
        ] = cast

    def get_chromecast(self, chromecast=None):
        if isinstance(chromecast, Chromecast):
            return chromecast

        if self._chromecasts_by_uuid.get(chromecast):
            return self._chromecasts_by_uuid[chromecast]

        if self._chromecasts_by_name.get(chromecast):
            return self._chromecasts_by_name[chromecast]

        raise AssertionError(f'Chromecast {chromecast} not found')

    @action
    def play(
        self,
        resource: str,
        *_,
        content_type: Optional[str] = None,
        chromecast: Optional[str] = None,
        title: Optional[str] = None,
        image_url: Optional[str] = None,
        autoplay: bool = True,
        current_time: int = 0,
        stream_type: str = STREAM_TYPE_BUFFERED,
        subtitles: Optional[str] = None,
        subtitles_lang: str = 'en-US',
        subtitles_mime: str = 'text/vtt',
        subtitle_id: int = 1,
        **__,
    ):
        """
        Cast media to an available Chromecast device.

        :param resource: Media to cast
        :param content_type: Content type as a MIME type string
        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        :param title: Optional title
        :param image_url: URL of the image to use for the thumbnail
        :param autoplay: Set it to false if you don't want the content to start
            playing immediately (default: true)
        :param current_time: Time to start the playback in seconds (default: 0)
        :param stream_type: Type of stream to cast. Can be BUFFERED (default),
            LIVE or UNKNOWN
        :param subtitles: URL of the subtitles to be shown
        :param subtitles_lang: Subtitles language (default: en-US)
        :param subtitles_mime: Subtitles MIME type (default: text/vtt)
        :param subtitle_id: ID of the subtitles to be loaded (default: 1)
        """

        if not chromecast:
            chromecast = self.chromecast

        post_event(MediaPlayRequestEvent, resource=resource, device=chromecast)
        cast = self.get_chromecast(chromecast)
        mc = cast.media_controller
        resource = self._get_resource(resource)

        if not content_type:
            content_type = get_mime_type(resource)

        if not content_type:
            raise RuntimeError(f'content_type required to process media {resource}')

        if not resource.startswith('http://') and not resource.startswith('https://'):
            resource = self._start_streaming(resource)['url']
            resource = get_remote_base_url() + resource
            self.logger.info('HTTP media stream started on %s', resource)

        if self._latest_resource:
            if not title:
                title = self._latest_resource.title
            if not image_url:
                image_url = self._latest_resource.image

        self.logger.info('Playing %s on %s', resource, chromecast)

        mc.play_media(
            resource,
            content_type,
            title=self._latest_resource.title if self._latest_resource else title,
            thumb=image_url,
            current_time=current_time,
            autoplay=autoplay,
            stream_type=stream_type,
            subtitles=subtitles,
            subtitles_lang=subtitles_lang,
            subtitles_mime=subtitles_mime,
            subtitle_id=subtitle_id,
        )

        if subtitles:
            mc.register_status_listener(SubtitlesAsyncHandler(mc, subtitle_id))

        mc.block_until_active()
        if self.volume:
            self.set_volume(volume=self.volume, chromecast=chromecast)

        return self.status(chromecast=chromecast)

    @action
    def load(self, *args, **kwargs):
        """
        Alias for :meth:`.play`.
        """
        return self.play(*args, **kwargs)

    @action
    def pause(self, *_, chromecast: Optional[str] = None, **__):
        """
        Pause the current media on the Chromecast.
        """
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)

        if cast.media_controller.status.player_is_paused:
            cast.media_controller.play()
        elif cast.media_controller.status.player_is_playing:
            cast.media_controller.pause()

        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def stop(self, *_, chromecast: Optional[str] = None, **__):  # type: ignore
        if self.should_stop():
            if self._zc:
                self._zc.close()
                self._zc = None

            if self._browser:
                self._browser.stop_discovery()
                self._browser = None

            return

        chromecast = chromecast or self.chromecast
        if not chromecast:
            return None

        cast = self.get_chromecast(chromecast)
        cast.media_controller.stop()
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def rewind(self, chromecast: Optional[str] = None):
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.media_controller.rewind()
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def set_position(self, position: float, chromecast: Optional[str] = None, **_):
        cast = self.get_chromecast(chromecast or self.chromecast)
        cast.media_controller.seek(position)
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def seek(self, position: float, chromecast: Optional[str] = None, **_):
        return self.forward(chromecast=chromecast, offset=position)

    @action
    def back(self, chromecast: Optional[str] = None, offset: int = 30, **_):
        cast = self.get_chromecast(chromecast or self.chromecast)
        mc = cast.media_controller
        if mc.status.current_time:
            mc.seek(mc.status.current_time - offset)
            cast.wait()

        return self.status(chromecast=chromecast)

    @action
    def forward(self, chromecast: Optional[str] = None, offset: int = 30, **_):
        cast = self.get_chromecast(chromecast or self.chromecast)
        mc = cast.media_controller
        if mc.status.current_time:
            mc.seek(mc.status.current_time + offset)
            cast.wait()

        return self.status(chromecast=chromecast)

    @action
    def is_playing(self, chromecast: Optional[str] = None, **_):
        return self.get_chromecast(
            chromecast or self.chromecast
        ).media_controller.status.player_is_playing

    @action
    def is_paused(self, chromecast: Optional[str] = None, **_):
        return self.get_chromecast(
            chromecast or self.chromecast
        ).media_controller.status.player_is_paused

    @action
    def is_idle(self, chromecast: Optional[str] = None):
        return self.get_chromecast(
            chromecast or self.chromecast
        ).media_controller.status.player_is_idle

    @action
    def list_subtitles(self, chromecast: Optional[str] = None):
        return self.get_chromecast(
            chromecast or self.chromecast
        ).media_controller.status.subtitle_tracks

    @action
    def enable_subtitles(
        self, chromecast: Optional[str] = None, track_id: Optional[int] = None, **_
    ):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        if track_id is not None:
            return mc.enable_subtitle(track_id)
        if mc.status.subtitle_tracks:
            return mc.enable_subtitle(mc.status.subtitle_tracks[0].get('trackId'))

    @action
    def disable_subtitles(
        self, chromecast: Optional[str] = None, track_id: Optional[int] = None, **_
    ):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        if track_id:
            return mc.disable_subtitle(track_id)
        if mc.status.current_subtitle_tracks:
            return mc.disable_subtitle(mc.status.current_subtitle_tracks[0])

    @action
    def toggle_subtitles(self, chromecast: Optional[str] = None, **_):
        mc = self.get_chromecast(chromecast or self.chromecast).media_controller
        all_subs = mc.status.subtitle_tracks
        cur_subs = mc.status.current_subtitle_tracks

        if cur_subs:
            return self.disable_subtitles(chromecast, cur_subs[0])

        return self.enable_subtitles(chromecast, all_subs[0].get('trackId'))

    @action
    def status(self, chromecast: Optional[str] = None):
        """
        :return: The status of a Chromecast (if ``chromecast`` is specified) or
            all the discovered/available Chromecasts. Format:

                .. code-block:: javascript

                    {
                      "type": "cast",  // Can be "cast" or "audio"
                      "name": "Living Room TV",
                      "manufacturer": "Google Inc.",
                      "model_name": "Chromecast",
                      "uuid": "f812afac-80ff-11ee-84dc-001500e8f607",
                      "address": "192.168.1.2",
                      "port": 8009,
                      "status": {
                        "app": {
                          "id": "CC1AD845",
                          "name": "Default Media Receiver"
                        },
                        "is_active_input": false,
                        "is_stand_by": true,
                        "is_idle": true,
                        "namespaces": [
                          "urn:x-cast:com.google.cast.cac",
                          "urn:x-cast:com.google.cast.debugoverlay",
                          "urn:x-cast:com.google.cast.media"
                        ],
                        "volume": 100,
                        "muted": false,
                        "adjusted_current_time": 14.22972,
                        "album_artist": null,
                        "album_name": null,
                        "artist": null,
                        "url": "https://some/video.mp4",
                        "content_type": "video/mp4",
                        "current_subtitle_tracks": [],
                        "position": 1.411891,
                        "duration": 253.376145,
                        "episode": null,
                        "idle_reason": null,
                        "images": [
                          [
                            "https://some/image.jpg",
                            null,
                            null
                          ]
                        ],
                        "last_updated": "2023-11-12T02:03:33.888843",
                        "media_custom_data": {},
                        "media_is_generic": true,
                        "media_is_movie": false,
                        "media_is_musictrack": false,
                        "media_is_photo": false,
                        "media_is_tvshow": false,
                        "media_metadata": {
                          "title": "Some media",
                          "thumb": "https://some/image.jpg",
                          "images": [
                            {
                              "url": "https://some/image.jpg"
                            }
                          ],
                          "metadataType": 0
                        },
                        "media_session_id": 1,
                        "metadata_type": 0,
                        "playback_rate": 1,
                        "player_is_idle": false,
                        "player_is_paused": false,
                        "player_is_playing": true,
                        "state": "play",
                        "season": null,
                        "series_title": null,
                        "stream_type": "BUFFERED",
                        "stream_type_is_buffered": true,
                        "stream_type_is_live": false,
                        "subtitle_tracks": [],
                        "supported_media_commands": 12303,
                        "supports_pause": true,
                        "supports_queue_next": false,
                        "supports_queue_prev": false,
                        "seekable": true,
                        "supports_skip_backward": false,
                        "supports_skip_forward": false,
                        "supports_stream_mute": true,
                        "supports_stream_volume": true,
                        "title": "Some media",
                        "track": null
                      }
                    }

        """
        return self._status(chromecast=chromecast)

    def _status(self, chromecast: Optional[str] = None) -> dict:
        if chromecast:
            assert (
                chromecast in self._chromecasts_by_name
            ), f'No such Chromecast device: {chromecast}'
            return self._serialize_device(self._chromecasts_by_name[chromecast])

        return {
            name: self._serialize_device(cast)
            for name, cast in self._chromecasts_by_name.items()
        }

    @action
    def disconnect(
        self,
        chromecast: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Disconnect a Chromecast and wait for it to terminate

        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        :param timeout: Number of seconds to wait for disconnection (default:
            None: block until termination).
        """
        cast = self.get_chromecast(chromecast)
        cast.disconnect(timeout=timeout)

    @action
    def join(self, chromecast: Optional[str] = None, timeout: Optional[float] = None):
        """
        Blocks the thread until the Chromecast connection is terminated.

        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        :param timeout: Number of seconds to wait for disconnection (default:
            None: block until termination).
        """
        cast = self.get_chromecast(chromecast)
        cast.join(timeout=timeout)

    @action
    def quit(self, chromecast: Optional[str] = None):
        """
        Exits the current app on the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        """
        cast = self.get_chromecast(chromecast)
        cast.quit_app()

    @action
    def set_volume(self, volume: float, chromecast: Optional[str] = None):
        """
        Set the Chromecast volume

        :param volume: Volume to be set, between 0 and 100.
        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        """
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.set_volume(volume / 100)
        cast.wait()
        return {
            **self._status(chromecast=chromecast),
            'volume': volume,
        }

    @action
    def volup(self, chromecast: Optional[str] = None, step: float = 10, **_):
        """
        Turn up the Chromecast volume by 10% or step.

        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        :param step: Volume increment between 0 and 100 (default: 10%).
        """
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        step /= 100
        cast.volume_up(min(step, 1))
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def voldown(self, chromecast: Optional[str] = None, step: float = 10, **_):
        """
        Turn down the Chromecast volume by 10% or step.

        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        :param step: Volume decrement between 0 and 100 (default: 10%).
        """
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        step /= 100
        cast.volume_down(max(step, 0))
        cast.wait()
        return self.status(chromecast=chromecast)

    @action
    def mute(self, chromecast: Optional[str] = None):
        """
        Toggle the mute status on the Chromecast

        :param chromecast: Chromecast to cast to. If none is specified, then
            the default configured Chromecast will be used.
        """
        chromecast = chromecast or self.chromecast
        cast = self.get_chromecast(chromecast)
        cast.set_volume_muted(not cast.media_controller.status.volume_muted)
        cast.wait()
        return self.status(chromecast=chromecast)

    def set_subtitles(self, *_, **__):
        raise NotImplementedError

    def remove_subtitles(self, *_, **__):
        raise NotImplementedError

    def _refresh_chromecasts(self):
        cast_info = {cast.friendly_name: cast for cast in self.browser.devices.values()}

        for info in cast_info.values():
            name = info.friendly_name
            if self._chromecasts_by_uuid.get(
                info.uuid
            ) and self._chromecasts_by_name.get(name):
                self.logger.debug('Chromecast %s already connected', name)
                continue

            self.logger.info('Started scan for Chromecast %s', name)

            try:
                cc = get_chromecast_from_cast_info(
                    info,
                    self.browser.zc,
                    tries=2,
                    retry_wait=5,
                    timeout=30,
                )

                self._chromecasts_by_name[cc.name] = cc
            except ChromecastConnectionError:
                self.logger.warning('Failed to connect to Chromecast %s', info)
                continue

            if cc.uuid not in self._chromecasts_by_uuid:
                self._chromecasts_by_uuid[cc.uuid] = cc
                self.logger.debug('Connecting to Chromecast %s', name)

                if name not in self._media_listeners:
                    cc.start()
                    self._media_listeners[name] = MediaListener(
                        name=name or str(cc.uuid),
                        cast=cc,
                        callback=self._event_callback,
                    )

                    cc.media_controller.register_status_listener(
                        self._media_listeners[name]
                    )

                    self.logger.info('Connected to Chromecast %s', name)

            self._chromecasts_by_uuid[cc.uuid] = cc
            self._chromecasts_by_name[name] = cc

    def main(self):
        while not self.should_stop():
            try:
                self._refresh_chromecasts()
            finally:
                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
