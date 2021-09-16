import urllib.parse
from typing import Optional

from platypush.config import Config
from platypush.context import get_plugin
from platypush.plugins import Plugin, action
from platypush.plugins.media import MediaPlugin


class TtsPlugin(Plugin):
    """
    Default Text-to-Speech plugin. It leverages Google Translate.

    Requires:

        * At least a *media plugin* (see :class:`platypush.plugins.media.MediaPlugin`) enabled/configured - used for
          speech playback.

    """

    _supported_media_plugins = [
        'media.gstreamer',
        'media.omxplayer',
        'media.mplayer',
        'media.mpv',
        'media.vlc',
    ]

    def __init__(self, language='en-gb', media_plugin: Optional[str] = None, player_args: Optional[dict] = None):
        """
        :param language: Language code (default: ``en-gb``).
        :param media_plugin: Media plugin to be used for audio playback. Supported:

            - ``media.gstreamer``
            - ``media.omxplayer``
            - ``media.mplayer``
            - ``media.mpv``
            - ``media.vlc``

        :param player_args: Optional arguments that should be passed to the player plugin's
            :meth:`platypush.plugins.media.MediaPlugin.play` method.
        """
        super().__init__()
        self.language = language
        self.player_args = player_args or {}
        self.media_plugin = get_plugin(media_plugin) if media_plugin else self._get_media_plugin()
        assert self.media_plugin, 'No media playback plugin configured. Supported plugins: [{}]'.format(
            ', '.join(self._supported_media_plugins))

    @classmethod
    def _get_media_plugin(cls) -> Optional[MediaPlugin]:
        for plugin in cls._supported_media_plugins:
            if plugin in Config.get():
                return get_plugin(plugin)

    @action
    def say(self, text: str, language: Optional[str] = None, player_args: Optional[dict] = None):
        """
        Say some text.

        :param text: Text to say.
        :param language: Language code override.
        :param player_args: Optional arguments that should be passed to the player plugin's
            :meth:`platypush.plugins.media.MediaPlugin.play` method.
        """
        language = language or self.language
        player_args = player_args or self.player_args
        url = 'https://translate.google.com/translate_tts?{}'.format(
            urllib.parse.urlencode({
                'ie': 'UTF-8',
                'client': 'tw-ob',
                'tl': language,
                'q': text,
            }))

        self.media_plugin.play(url, **player_args)


# vim:sw=4:ts=4:et:
