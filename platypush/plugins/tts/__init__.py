import subprocess
import urllib.parse

from platypush.message.response import Response

from .. import Plugin

class TtsPlugin(Plugin):
    """ Default Text-to-Speech plugin. It leverages Google Translate and
        requires mplayer """

    def __init__(self, lang='en-gb'):
        super().__init__()
        self.lang=lang

    def say(self, phrase, lang=None):
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

