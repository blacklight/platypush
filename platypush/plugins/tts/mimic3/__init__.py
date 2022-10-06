import requests
from typing import Optional
from urllib.parse import urljoin, urlencode
from platypush.backend.http.app.utils import get_local_base_url

from platypush.context import get_backend
from platypush.plugins import action
from platypush.plugins.tts import TtsPlugin
from platypush.schemas.tts.mimic3 import Mimic3VoiceSchema


class TtsMimic3Plugin(TtsPlugin):
    """
    TTS plugin that uses the `Mimic3 webserver
    <https://github.com/MycroftAI/mimic3>`_ provided by `Mycroft
    <https://mycroft.ai/>`_ as a text-to-speech engine.

    The easiest way to deploy a Mimic3 instance is probably via Docker:

    .. code-block:: bash

        $ mkdir -p "$HOME/.local/share/mycroft/mimic3"
        $ chmod a+rwx "$HOME/.local/share/mycroft/mimic3"
        $ docker run --rm \
            -p 59125:59125 \
            -v "%h/.local/share/mycroft/mimic3:/home/mimic3/.local/share/mycroft/mimic3" \
            'mycroftai/mimic3'

    Requires:

        * At least a *media plugin* (see
          :class:`platypush.plugins.media.MediaPlugin`) enabled/configured -
          used for speech playback.
        * The ``http`` backend (:class:`platypush.backend.http.HttpBackend`)
          enabled - used for proxying the API calls.

    """

    def __init__(
        self,
        server_url: str,
        voice: str = 'en_UK/apope_low',
        media_plugin: Optional[str] = None,
        player_args: Optional[dict] = None,
        **kwargs
    ):
        """
        :param server_url: Base URL of the web server that runs the Mimic3 engine.
        :param voice: Default voice to be used (default: ``en_UK/apope_low``).
            You can get a full list of the voices available on the server
            through :meth:`.voices`.
        :param media_plugin: Media plugin to be used for audio playback. Supported:

            - ``media.gstreamer``
            - ``media.omxplayer``
            - ``media.mplayer``
            - ``media.mpv``
            - ``media.vlc``

        :param player_args: Optional arguments that should be passed to the player plugin's
            :meth:`platypush.plugins.media.MediaPlugin.play` method.
        """
        super().__init__(media_plugin=media_plugin, player_args=player_args, **kwargs)

        self.server_url = server_url
        self.voice = voice

    @action
    def say(
        self,
        text: str,
        server_url: Optional[str] = None,
        voice: Optional[str] = None,
        player_args: Optional[dict] = None,
    ):
        """
        Say some text.

        :param text: Text to say.
        :param server_url: Default ``server_url`` override.
        :param voice: Default ``voice`` override.
        :param player_args: Default ``player_args`` override.
        """
        server_url = server_url or self.server_url
        voice = voice or self.voice
        player_args = player_args or self.player_args
        http = get_backend('http')
        assert http, 'http backend not configured'
        assert self.media_plugin, 'No media plugin configured'

        url = (
            urljoin(get_local_base_url(), '/tts/mimic3/say')
            + '?'
            + urlencode(
                {
                    'text': text,
                    'server_url': server_url,
                    'voice': voice,
                }
            )
        )

        self.media_plugin.play(url, **player_args)

    @action
    def voices(self, server_url: Optional[str] = None):
        """
        List the voices available on the server.

        :param server_url: Default ``server_url`` override.
        :return: .. schema:: tts.mimic3.Mimic3VoiceSchema(many=True)
        """
        server_url = server_url or self.server_url
        rs = requests.get(urljoin(server_url, '/api/voices'))
        rs.raise_for_status()
        return Mimic3VoiceSchema().dump(rs.json(), many=True)


# vim:sw=4:ts=4:et:
