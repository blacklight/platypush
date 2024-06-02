from abc import ABC
from dataclasses import asdict, dataclass
from enum import Enum
import os
from threading import Event
from typing import Any, Collection, Dict, Optional, Type

from platypush.context import get_bus, get_plugin
from platypush.entities.assistants import Assistant
from platypush.entities.managers.assistants import AssistantEntityManager
from platypush.message.event import Event as AppEvent
from platypush.plugins import Plugin, action
from platypush.utils import get_plugin_name_by_class


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
        stop_conversation_on_speech_match: bool = True,
        **kwargs,
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

        :param stop_conversation_on_speech_match: If set, the plugin will
            prevent the default assistant response when a
            :class:`platypush.message.event.assistant.SpeechRecognizedEvent`
            matches a user hook with a condition on a ``phrase`` field. This is
            useful to prevent the assistant from responding with a default "*I'm
            sorry, I can't help you with that*" when e.g. you say "*play the
            music*", and you have a hook that matches the phrase "*play the
            music*" and handles it with a custom action. If set, and you wish
            the assistant to also provide an answer if an event matches one of
            your hooks, then you should call the :meth:`render_response` method
            in your hook handler. If not set, then the assistant will always try
            and respond with a default message, even if a speech event matches
            the phrase of one of your hooks. In this case, if you want to prevent
            the default response, you should call :meth:`stop_conversation`
            explicitly from your hook handler. Default: True.
        """
        super().__init__(*args, **kwargs)
        self.tts_plugin = tts_plugin
        self.tts_plugin_args = {'join': True, **(tts_plugin_args or {})}
        self.stop_conversation_on_speech_match = stop_conversation_on_speech_match
        self._conversation_start_sound = None
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
        self._plugin_name = get_plugin_name_by_class(type(self))

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

    @action
    def stop_conversation(self, *_, **__):
        """
        Programmatically stops a conversation.
        """
        self._stop_conversation()

    def _stop_conversation(self, *_, **__):
        tts = self._get_tts_plugin()
        if tts:
            tts.stop()

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

    @action
    def render_response(
        self, text: str, *_, with_follow_on_turn: Optional[bool] = None, **__
    ) -> bool:
        """
        Render a response text as audio over the configured TTS plugin.

        :param text: Text to render.
        :param with_follow_on_turn: If set, the assistant will wait for a follow-up.
            By default, ``with_follow_on_turn`` will be automatically set to true if
            the ``text`` ends with a question mark.
        :return: True if the assistant is waiting for a follow-up, False otherwise.
        """
        if not text:
            self._on_no_response()
            return False

        follow_up = (
            bool(text and text.strip().endswith('?'))
            if with_follow_on_turn is None
            else with_follow_on_turn
        )

        self._on_response_render_start(text, with_follow_on_turn=follow_up)
        self._render_response(text)
        self._on_response_render_end(with_follow_on_turn=follow_up)

        if follow_up:
            self.start_conversation()
        else:
            self.stop_conversation()

        return follow_up

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

    def _send_event(self, event_type: Type[AppEvent], **kwargs):
        self.publish_entities([self])
        get_bus().post(event_type(assistant=self._plugin_name, **kwargs))

    def _on_conversation_start(self):
        from platypush.message.event.assistant import ConversationStartEvent

        self._last_response = None
        self._last_query = None
        self._conversation_running.set()
        self._send_event(ConversationStartEvent)
        self._play_conversation_start_sound()

    def _on_conversation_end(self):
        from platypush.message.event.assistant import ConversationEndEvent

        self._conversation_running.clear()
        self._send_event(ConversationEndEvent)

    def _on_conversation_timeout(self):
        from platypush.message.event.assistant import ConversationTimeoutEvent

        self._last_response = None
        self._last_query = None
        self._conversation_running.clear()
        self._send_event(ConversationTimeoutEvent)

    def _on_no_response(self):
        from platypush.message.event.assistant import NoResponseEvent

        self._last_response = None
        self._conversation_running.clear()
        self._send_event(NoResponseEvent)

    def _on_response_render_start(
        self, text: Optional[str], with_follow_on_turn: bool = False
    ):
        from platypush.message.event.assistant import ResponseEvent

        self._last_response = text
        self._send_event(
            ResponseEvent, response_text=text, with_follow_on_turn=with_follow_on_turn
        )

    def _render_response(self, text: Optional[str]):
        if not text:
            return

        tts = self._get_tts_plugin()
        if not tts:
            self.logger.warning(
                'Got a response to render, but no TTS plugin is configured: %s', text
            )
            return

        tts.say(text=text, **self.tts_plugin_args)

    def _on_response_render_end(self, with_follow_on_turn: bool = False):
        from platypush.message.event.assistant import ResponseEndEvent

        self._send_event(
            ResponseEndEvent,
            response_text=self._last_response,
            with_follow_on_turn=with_follow_on_turn,
        )

    def _on_hotword_detected(self, hotword: Optional[str]):
        from platypush.message.event.assistant import HotwordDetectedEvent

        self._send_event(HotwordDetectedEvent, hotword=hotword)

    def _on_speech_recognized(self, phrase: Optional[str]):
        from platypush.message.event.assistant import SpeechRecognizedEvent

        phrase = (phrase or '').lower().strip()
        self._last_query = phrase
        self._send_event(SpeechRecognizedEvent, phrase=phrase)

    def _on_intent_matched(self, intent: str, slots: Optional[Dict[str, Any]] = None):
        from platypush.message.event.assistant import IntentRecognizedEvent

        self._send_event(IntentRecognizedEvent, intent=intent, slots=slots)

    def _on_alarm_start(self):
        from platypush.message.event.assistant import AlarmStartedEvent

        self._cur_alert_type = AlertType.ALARM
        self._send_event(AlarmStartedEvent)

    def _on_alarm_end(self):
        from platypush.message.event.assistant import AlarmEndEvent

        self._cur_alert_type = None
        self._send_event(AlarmEndEvent)

    def _on_timer_start(self):
        from platypush.message.event.assistant import TimerStartedEvent

        self._cur_alert_type = AlertType.TIMER
        self._send_event(TimerStartedEvent)

    def _on_timer_end(self):
        from platypush.message.event.assistant import TimerEndEvent

        self._cur_alert_type = None
        self._send_event(TimerEndEvent)

    def _on_alert_start(self):
        from platypush.message.event.assistant import AlertStartedEvent

        self._cur_alert_type = AlertType.ALERT
        self._send_event(AlertStartedEvent)

    def _on_alert_end(self):
        from platypush.message.event.assistant import AlertEndEvent

        self._cur_alert_type = None
        self._send_event(AlertEndEvent)

    def _on_mute(self):
        from platypush.message.event.assistant import MicMutedEvent

        self._is_muted = True
        self._send_event(MicMutedEvent)

    def _on_unmute(self):
        from platypush.message.event.assistant import MicUnmutedEvent

        self._is_muted = False
        self._send_event(MicUnmutedEvent)

    def _on_mute_changed(self, value: bool):
        if value:
            self._on_mute()
        else:
            self._on_unmute()

    def transform_entities(self, entities: Collection['AssistantPlugin'], **_):
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
