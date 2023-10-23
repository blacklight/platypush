from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
import os
from threading import Event
from typing import Any, Collection, Dict, Optional

from platypush.context import get_bus, get_plugin
from platypush.entities.assistants import Assistant
from platypush.entities.managers.assistants import AssistantEntityManager
from platypush.message.event.assistant import (
    AssistantEvent,
    ConversationStartEvent,
    ConversationEndEvent,
    ConversationTimeoutEvent,
    ResponseEvent,
    NoResponseEvent,
    SpeechRecognizedEvent,
    AlarmStartedEvent,
    AlarmEndEvent,
    TimerStartedEvent,
    TimerEndEvent,
    AlertStartedEvent,
    AlertEndEvent,
    MicMutedEvent,
    MicUnmutedEvent,
)
from platypush.plugins import Plugin, action
from platypush.utils import get_plugin_name_by_class


@dataclass
class AlertType(Enum):
    """
    Enum representing the type of an alert.
    """

    ALARM = 'alarm'
    TIMER = 'timer'
    ALERT = 'alert'


@dataclass
class AssistantState:
    """
    Dataclass representing the state of an assistant.
    """

    last_query: Optional[str] = None
    last_response: Optional[str] = None
    conversation_running: bool = False
    is_muted: bool = False
    is_detecting: bool = True
    alert_state: Optional[str] = None


class AssistantPlugin(Plugin, AssistantEntityManager, ABC):
    """
    Base class for assistant plugins.
    """

    _entity_name = 'Assistant'

    def __init__(
        self,
        *args,
        tts_plugin: Optional[str] = None,
        tts_plugin_args: Optional[Dict[str, Any]] = None,
        conversation_start_sound: Optional[str] = None,
        **kwargs
    ):
        """
        :param tts_plugin: If set, the assistant will use this plugin (e.g.
            ``tts``, ``tts.google`` or ``tts.mimic3``) to render the responses,
            instead of using the built-in assistant voice.

        :param tts_plugin_args: Optional arguments to be passed to the TTS
            ``say`` action, if ``tts_plugin`` is set.

        :param conversation_start_sound: If set, the assistant will play this
            audio file when it detects a speech. The sound file will be played
            on the default audio output device. If not set, the assistant won't
            play any sound when it detects a speech.
        """
        super().__init__(*args, **kwargs)
        self.tts_plugin = tts_plugin
        self.tts_plugin_args = tts_plugin_args or {}
        if conversation_start_sound:
            self._conversation_start_sound = os.path.abspath(
                os.path.expanduser(conversation_start_sound)
            )

        self._detection_paused = Event()
        self._conversation_running = Event()
        self._is_muted = False
        self._last_query: Optional[str] = None
        self._last_response: Optional[str] = None
        self._cur_alert_type: Optional[AlertType] = None

    @property
    def _state(self) -> AssistantState:
        return AssistantState(
            last_query=self._last_query,
            last_response=self._last_response,
            conversation_running=self._conversation_running.is_set(),
            is_muted=self._is_muted,
            is_detecting=not self._detection_paused.is_set(),
            alert_state=self._cur_alert_type.value if self._cur_alert_type else None,
        )

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
    def pause_detection(self, *_, **__):
        """
        Put the assistant on pause. No new conversation events will be triggered.
        """
        self._detection_paused.set()

    @action
    def resume_detection(self, *_, **__):
        """
        Resume the assistant hotword detection from a paused state.
        """
        self._detection_paused.clear()

    @action
    def is_detecting(self, *_, **__) -> bool:
        """
        :return: True if the asistant is detecting, False otherwise.
        """
        return not self._detection_paused.is_set()

    @action
    def is_muted(self, *_, **__) -> bool:
        """
        :return: True if the microphone is muted, False otherwise.
        """
        return self._is_muted

    @action
    def status(self, *_, **__):
        """
        :return: The current assistant status:

            .. code-block:: json

                {
                    "last_query": "What time is it?",
                    "last_response": "It's 10:30 AM",
                    "conversation_running": true,
                    "is_muted": false,
                    "is_detecting": true
                }

        """
        self.publish_entities([self])
        return asdict(self._state)

    def _get_tts_plugin(self):
        if not self.tts_plugin:
            return None

        return get_plugin(self.tts_plugin)

    def _play_conversation_start_sound(self):
        if not self._conversation_start_sound:
            return

        audio = get_plugin('sound')
        if not audio:
            self.logger.warning(
                'Unable to play conversation start sound: sound plugin not found'
            )
            return

        audio.play(self._conversation_start_sound)

    def _send_event(self, event: AssistantEvent):
        self.publish_entities([self])
        get_bus().post(event)

    def _on_conversation_start(self):
        self._last_response = None
        self._last_query = None
        self._conversation_running.set()
        self._send_event(ConversationStartEvent(assistant=self))
        self._play_conversation_start_sound()

    def _on_conversation_end(self):
        self._conversation_running.clear()
        self._send_event(ConversationEndEvent(assistant=self))

    def _on_conversation_timeout(self):
        self._last_response = None
        self._last_query = None
        self._conversation_running.clear()
        self._send_event(ConversationTimeoutEvent(assistant=self))

    def _on_no_response(self):
        self._last_response = None
        self._conversation_running.clear()
        self._send_event(NoResponseEvent(assistant=self))

    def _on_reponse_rendered(self, text: Optional[str]):
        self._last_response = text
        self._send_event(ResponseEvent(assistant=self, response_text=text))
        tts = self._get_tts_plugin()

        if tts and text:
            self.stop_conversation()
            tts.say(text=text, **self.tts_plugin_args)

    def _on_speech_recognized(self, phrase: Optional[str]):
        phrase = (phrase or '').lower().strip()
        self._last_query = phrase
        self._send_event(SpeechRecognizedEvent(assistant=self, phrase=phrase))

    def _on_alarm_start(self):
        self._cur_alert_type = AlertType.ALARM
        self._send_event(AlarmStartedEvent(assistant=self))

    def _on_alarm_end(self):
        self._cur_alert_type = None
        self._send_event(AlarmEndEvent(assistant=self))

    def _on_timer_start(self):
        self._cur_alert_type = AlertType.TIMER
        self._send_event(TimerStartedEvent(assistant=self))

    def _on_timer_end(self):
        self._cur_alert_type = None
        self._send_event(TimerEndEvent(assistant=self))

    def _on_alert_start(self):
        self._cur_alert_type = AlertType.ALERT
        self._send_event(AlertStartedEvent(assistant=self))

    def _on_alert_end(self):
        self._cur_alert_type = None
        self._send_event(AlertEndEvent(assistant=self))

    def _on_mute(self):
        self._is_muted = True
        self._send_event(MicMutedEvent(assistant=self))

    def _on_unmute(self):
        self._is_muted = False
        self._send_event(MicUnmutedEvent(assistant=self))

    def _on_mute_changed(self, value: bool):
        if value:
            self._on_mute()
        else:
            self._on_unmute()

    def transform_entities(self, entities: Collection['AssistantPlugin']):
        return super().transform_entities(
            [
                Assistant(
                    external_id=get_plugin_name_by_class(type(dev)),
                    name=self._entity_name,
                    last_query=dev._state.last_query,
                    last_response=dev._state.last_response,
                    conversation_running=dev._state.conversation_running,
                    is_muted=dev._state.is_muted,
                    is_detecting=dev._state.is_detecting,
                )
                for dev in (entities or [])
            ]
        )


# vim:sw=4:ts=4:et:
