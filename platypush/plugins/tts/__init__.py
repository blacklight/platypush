import urllib.parse
from typing import Optional

from platypush.context import get_plugin
from platypush.plugins import Plugin, action


class TtsPlugin(Plugin):
    """
    Default Text-to-Speech plugin. It leverages Google Translate's unofficial
    frontend API.
    """

    def __init__(self, language='en-US', **player_args):
        """
        :param language: Language code (default: ``en-US``).
        :param player_args: Additional arguments to be passed to
            :meth:`platypush.plugins.sound.SoundPlugin.play` (like volume,
            duration, channels etc.).
        """
        super().__init__()
        self.language = language
        self.player_args = player_args or {}

    def _playback(self, resource: str, **kwargs):
        audio = get_plugin('sound')
        assert audio
        audio.play(resource, **{**self.player_args, **kwargs})

    @action
    def say(
        self,
        text: str,
        language: Optional[str] = None,
        **player_args,
    ):
        """
        Say some text.

        :param text: Text to say.
        :param language: Language code override.
        :param player_args: Extends the additional arguments to be passed to
            :meth:`platypush.plugins.sound.SoundPlugin.play` (like volume,
            duration, channels etc.).
        """
        language = language or self.language
        url = 'https://translate.google.com/translate_tts?' + urllib.parse.urlencode(
            {
                'ie': 'UTF-8',
                'client': 'tw-ob',
                'tl': language,
                'q': text,
            }
        )

        self._playback(url, **player_args)

    @action
    def stop(self):
        """
        Stop the playback.
        """
        try:
            audio = get_plugin('sound')
        except Exception:
            return

        if audio:
            audio.stop_playback()


# vim:sw=4:ts=4:et:
