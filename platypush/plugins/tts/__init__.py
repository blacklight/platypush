import subprocess
import urllib.parse

from platypush.message.response import Response

from .. import Plugin

class TtsPlugin(Plugin):
    """
    Default Text-to-Speech plugin. It leverages Google Translate.

    Requires:

        * **mplayer** - see your distribution docs on how to install the mplayer package
    """

    def __init__(self, lang='en-gb'):
        super().__init__()
        self.lang=lang

    def say(self, phrase, lang=None):
        """
        Say a phrase

        :param phrase: Phrase to say
        :type phrase: str

        :param lang: Language code
        :type lang: str
        """
        if lang is None: lang=self.lang
        output = None
        errors = []
        cmd = ['mplayer -ao alsa -really-quiet -noconsolecontrols ' +
               '"http://translate.google.com/translate_tts?{}"'
               .format(urllib.parse.urlencode({
                   'ie'     : 'UTF-8',
                   'client' : 'tw-ob',
                   'tl'     : lang,
                   'q'      : phrase,
                }))]

        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            errors = [e.output.decode('utf-8')]

        return Response(output=output, errors=errors)


# vim:sw=4:ts=4:et:

