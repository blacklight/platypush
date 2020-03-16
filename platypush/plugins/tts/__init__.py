import subprocess
import urllib.parse
from typing import Optional, List

from platypush.plugins import Plugin, action


class TtsPlugin(Plugin):
    """
    Default Text-to-Speech plugin. It leverages Google Translate.

    Requires:

        * **mplayer** - see your distribution docs on how to install the mplayer package
    """

    def __init__(self, language='en-gb', player_args: Optional[List[str]] = None):
        """
        :param language: Language code (default: ``en-gb``).
        :param player_args: Extra options to be passed to the audio player (default: ``mplayer``).
        """
        super().__init__()
        self.language = language
        self.player_args = player_args or []

    @action
    def say(self, text: str, language: Optional[str] = None, player_args: Optional[List[str]] = None):
        """
        Say some text.

        :param text: Text to say.
        :param language: Language code override.
        :param player_args: ``player_args`` override.
        """
        language = language or self.language
        player_args = player_args or self.player_args
        cmd = [
            'mplayer -ao alsa -really-quiet -noconsolecontrols ' +
            ' '.join(player_args) + ' ' +
            '"http://translate.google.com/translate_tts?{}"'.format(
                urllib.parse.urlencode({
                    'ie': 'UTF-8',
                    'client': 'tw-ob',
                    'tl': language,
                    'q': text,
                })
            )
        ]

        try:
            return subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.output.decode('utf-8'))

# vim:sw=4:ts=4:et:
