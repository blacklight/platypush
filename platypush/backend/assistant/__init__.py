from abc import ABC
import threading
from typing import Optional, Dict, Any, Tuple

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.plugins.tts import TtsPlugin


class AssistantBackend(Backend):
    def __init__(self, tts_plugin: Optional[str] = None, tts_args: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Default assistant backend constructor.

        :param tts_plugin: If set, and if the assistant returns the processed response as text, then the processed
            response will be played through the selected text-to-speech plugin (can be e.g. "``tts``",
            "``tts.google``" or any other implementation of :class:`platypush.plugins.tts.TtsPlugin`).
        :param tts_args: Extra parameters to pass to the ``say`` method of the selected TTS plugin (e.g.
            language, voice or gender).
        """
        super().__init__(**kwargs)
        self._detection_paused = threading.Event()
        self.tts_plugin = tts_plugin
        self.tts_args = tts_args or {}

    def pause_detection(self):
        self._detection_paused.set()

    def resume_detection(self):
        self._detection_paused.clear()

    def is_detecting(self):
        return not self._detection_paused.is_set()

    def _get_tts_plugin(self) -> Tuple[Optional[TtsPlugin], Dict[str, Any]]:
        return get_plugin(self.tts_plugin) if self.tts_plugin else None, self.tts_args


# vim:sw=4:ts=4:et:
