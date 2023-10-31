from contextlib import contextmanager
import os
import tempfile
from typing import Generator, Optional
from urllib.parse import urljoin

import requests

from platypush.plugins import action
from platypush.plugins.tts import TtsPlugin
from platypush.schemas.tts.mimic3 import Mimic3VoiceSchema


class TtsMimic3Plugin(TtsPlugin):
    r"""
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

    """

    def __init__(
        self,
        server_url: str,
        voice: str = 'en_US/vctk_low',
        **kwargs,
    ):
        """
        :param server_url: Base URL of the web server that runs the Mimic3 engine.
        :param voice: Default voice to be used (default: ``en_US/vctk_low``).
            You can get a full list of the voices available on the server
            through :meth:`.voices`.
        """
        super().__init__(**kwargs)
        self.server_url = server_url
        self.voice = voice
        self.player_args.update(
            {
                'channels': 1,
                'sample_rate': 22050,
                'dtype': 'int16',
            }
        )

    @staticmethod
    @contextmanager
    def _save_audio(
        text: str,
        server_url: str,
        voice: str,
        timeout: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """
        Saves the raw audio stream from the Mimic3 server to an audio file for
        playback.

        :param text: Text to be spoken.
        :param server_url: Base URL of the Mimic3 server.
        :param voice: Voice to be used.
        :param timeout: Timeout for the audio stream retrieval.
        """

        rs = requests.post(
            urljoin(server_url, '/api/tts'),
            data=text,
            timeout=timeout,
            params={
                'voice': voice,
            },
        )

        rs.raise_for_status()
        tmp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_file.write(rs.content)
        yield tmp_file.name

        tmp_file.close()
        os.unlink(tmp_file.name)

    @action
    def say(
        self,
        text: str,
        *_,
        server_url: Optional[str] = None,
        voice: Optional[str] = None,
        **player_args,
    ):
        """
        Say some text.

        :param text: Text to say.
        :param server_url: Default ``server_url`` override.
        :param voice: Default ``voice`` override.
        :param player_args: Extends the additional arguments to be passed to
            :meth:`platypush.plugins.sound.SoundPlugin.play` (like volume,
            duration, channels etc.).
        """

        server_url = server_url or self.server_url
        voice = voice or self.voice

        with self._save_audio(text, server_url, voice) as audio_file:
            self._playback(audio_file, join=True, **player_args)

    @action
    def voices(self, server_url: Optional[str] = None):
        """
        List the voices available on the server.

        :param server_url: Default ``server_url`` override.
        :return: .. schema:: tts.mimic3.Mimic3VoiceSchema(many=True)
        """
        server_url = server_url or self.server_url
        rs = requests.get(urljoin(server_url, '/api/voices'), timeout=10)
        rs.raise_for_status()
        return Mimic3VoiceSchema().dump(rs.json(), many=True)


# vim:sw=4:ts=4:et:
