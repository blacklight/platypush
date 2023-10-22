from abc import ABC, abstractmethod
from threading import Event
from typing import Any, Dict, Optional

from platypush.context import get_plugin
from platypush.plugins import Plugin, action


class AssistantPlugin(ABC, Plugin):
    """
    Base class for assistant plugins.
    """

    def __init__(
        self,
        *args,
        tts_plugin: Optional[str] = None,
        tts_plugin_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        :param tts_plugin: If set, the assistant will use this plugin (e.g.
            ``tts``, ``tts.google`` or ``tts.mimic3``) to render the responses,
            instead of using the built-in assistant voice.

        :param tts_plugin_args: Optional arguments to be passed to the TTS
            ``say`` action, if ``tts_plugin`` is set.
        """
        super().__init__(*args, **kwargs)
        self.tts_plugin = tts_plugin
        self.tts_plugin_args = tts_plugin_args or {}
        self._detection_paused = Event()

    @abstractmethod
    def start_conversation(self, *_, **__):
        """
        Programmatically starts a conversation.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_conversation(self, *_, **__):
        """
        Programmatically stops a conversation.
        """
        raise NotImplementedError

    @action
    def pause_detection(self):
        """
        Put the assistant on pause. No new conversation events will be triggered.
        """
        self._detection_paused.set()

    @action
    def resume_detection(self):
        """
        Resume the assistant hotword detection from a paused state.
        """
        self._detection_paused.clear()

    @action
    def is_detecting(self) -> bool:
        """
        :return: True if the asistant is detecting, False otherwise.
        """
        return not self._detection_paused.is_set()

    def _get_tts_plugin(self):
        if not self.tts_plugin:
            return None

        return get_plugin(self.tts_plugin)


# vim:sw=4:ts=4:et:
