import os
import tempfile
from contextlib import contextmanager
from multiprocessing import Process
from typing import Generator, Optional

import requests

from platypush.context import get_plugin
from platypush.plugins import action
from platypush.plugins.openai import OpenaiPlugin
from platypush.plugins.tts import TtsPlugin


class TtsOpenaiPlugin(TtsPlugin):
    r"""
    This plugin provides an interface to the `OpenAI text-to-speech API
    <https://platform.openai.com/docs/guides/text-to-speech>`_.

    It requires the :class:`platypush.plugins.openai.OpenaiPlugin` plugin to be
    configured.
    """

    _BUFSIZE = 1024

    def __init__(
        self,
        model: str = 'tts-1',
        voice: str = 'nova',
        timeout: float = 10,
        **kwargs,
    ):
        """
        :param model: Model to be used for the text-to-speech conversion.
            See the `OpenAI API models documentation
            <https://platform.openai.com/docs/models/tts>`_ for the list of
            available models (default: ``tts-1``).
        :param voice: Default voice to be used. See the `OpenAI API
            voices documentation
            <https://platform.openai.com/docs/guides/text-to-speech/voice-options>`_
            for the list of available voices (default: ``nova``).
        :param timeout: Default timeout for the API requests (default: 10s).
        """
        super().__init__(**kwargs)
        openai = get_plugin('openai')
        assert openai, 'openai plugin not configured'

        self.openai: OpenaiPlugin = openai
        self.model = model
        self.voice = voice
        self.timeout = timeout
        self._audio_proc: Optional[Process] = None

    def _process_response(
        self,
        response: requests.Response,
        audio_file: str,
    ) -> Process:
        def proc_fn():
            try:
                with open(audio_file, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=self._BUFSIZE):
                        if chunk:
                            file.write(chunk)
                            file.flush()
            except KeyboardInterrupt:
                pass

        self._audio_proc = Process(target=proc_fn, name='openai-tts-response-processor')
        self._audio_proc.start()
        return self._audio_proc

    def _make_request(
        self,
        text: str,
        model: Optional[str] = None,
        voice: Optional[str] = None,
    ) -> requests.Response:
        rs = requests.post(
            "https://api.openai.com/v1/audio/speech",
            timeout=self.timeout,
            stream=True,
            headers={
                "Authorization": f"Bearer {self.openai._api_key}",  # pylint: disable=protected-access
                "Content-Type": "application/json",
            },
            json={
                "model": model or self.model,
                "voice": voice or self.voice,
                "input": text,
            },
        )

        rs.raise_for_status()
        return rs

    @contextmanager
    def _audio_fifo(self) -> Generator[str, None, None]:
        fifo_dir = tempfile.mkdtemp()
        fifo_path = os.path.join(fifo_dir, 'platypush-tts-openai-fifo')
        os.mkfifo(fifo_path)
        yield fifo_path

        os.unlink(fifo_path)
        os.rmdir(fifo_dir)

    @action
    def say(
        self,
        text: str,
        *_,
        model: Optional[str] = None,
        voice: Optional[str] = None,
        **player_args,
    ):
        """
        Say some text.

        :param text: Text to say.
        :param model: Default ``model`` override.
        :param voice: Default ``voice`` override.
        :param player_args: Extends the additional arguments to be passed to
            :meth:`platypush.plugins.sound.SoundPlugin.play` (like volume,
            duration, channels etc.).
        """
        response_processor: Optional[Process] = None

        try:
            response = self._make_request(text, model=model, voice=voice)

            with self._audio_fifo() as audio_file:
                response_processor = self._process_response(
                    response=response, audio_file=audio_file
                )
                self._playback(audio_file, **player_args)
                response_processor.join()
                response_processor = None
        finally:
            if response_processor:
                response_processor.terminate()

    @action
    def stop(self):
        super().stop()
        if self._audio_proc and self._audio_proc.is_alive():
            self._audio_proc.terminate()
            self._audio_proc.join()


# vim:sw=4:ts=4:et:
