import re
import sys
from typing import Any, Mapping, Optional, Union

from platypush.context import get_plugin
from platypush.message.event import Event, EventMatchResult
from platypush.plugins.assistant import AssistantPlugin
from platypush.utils import get_plugin_name_by_class


class AssistantEvent(Event):
    """Base class for assistant events"""

    def __init__(
        self, *args, assistant: Optional[Union[str, AssistantPlugin]] = None, **kwargs
    ):
        """
        :param assistant: Name of the assistant plugin that triggered the event.
        """
        assistant = assistant or kwargs.get('assistant')
        if assistant:
            kwargs['plugin'] = kwargs['_assistant'] = (
                assistant
                if isinstance(assistant, str)
                else get_plugin_name_by_class(assistant.__class__)
            )

        super().__init__(*args, **kwargs)

    @property
    def assistant(self) -> Optional[AssistantPlugin]:
        assistant = self.args.get('_assistant')
        if not assistant:
            return None

        return get_plugin(assistant)

    def as_dict(self):
        evt_dict = super().as_dict()
        evt_args = {**evt_dict['args']}
        assistant = evt_args.pop('_assistant', None)
        if assistant:
            evt_args['assistant'] = assistant

        return {
            **evt_dict,
            'args': evt_args,
        }


class ConversationStartEvent(AssistantEvent):
    """
    Event triggered when a new conversation starts
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ConversationEndEvent(AssistantEvent):
    """
    Event triggered when a conversation ends
    """

    def __init__(self, *args, with_follow_on_turn: bool = False, **kwargs):
        """
        :param with_follow_on_turn: Set to true if the conversation expects a
            user follow-up, false otherwise
        """
        super().__init__(*args, with_follow_on_turn=with_follow_on_turn, **kwargs)


class ConversationTimeoutEvent(ConversationEndEvent):
    """
    Event triggered when a conversation times out
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ResponseEvent(AssistantEvent):
    """
    Event triggered when a response is processed by the assistant
    """

    def __init__(
        self, *args, response_text: str, with_follow_on_turn: bool = False, **kwargs
    ):
        """
        :param response_text: Response text processed by the assistant
        :param with_follow_on_turn: Set to true if the conversation expects a
            user follow-up, false otherwise
        """
        super().__init__(
            *args,
            response_text=response_text,
            with_follow_on_turn=with_follow_on_turn,
            **kwargs,
        )


class ResponseEndEvent(ConversationEndEvent):
    """
    Event triggered when a response has been rendered on the assistant.
    """

    def __init__(
        self, *args, response_text: str, with_follow_on_turn: bool = False, **kwargs
    ):
        """
        :param response_text: Response text rendered on the assistant.
        :param with_follow_on_turn: Set to true if the conversation expects a
            user follow-up, false otherwise.
        """
        super().__init__(
            *args,
            response_text=response_text,
            with_follow_on_turn=with_follow_on_turn,
            **kwargs,
        )


class NoResponseEvent(ConversationEndEvent):
    """
    Event triggered when a conversation ends with no response
    """


class SpeechRecognizedEvent(AssistantEvent):
    """
    Event triggered when a speech is recognized
    """

    def __init__(self, *args, phrase: str, **kwargs):
        """
        :param phrase: Recognized user phrase
        """

        super().__init__(*args, phrase=phrase, **kwargs)
        self.recognized_phrase = phrase.strip().lower()

    def matches_condition(self, condition):
        """
        Overrides matches condition, and stops the conversation to prevent the
        default assistant response if the event matched some event hook condition.
        """

        result = super().matches_condition(condition)
        if (
            result.is_match
            and condition.args.get('phrase')
            and self.assistant
            and self.assistant.stop_conversation_on_speech_match
        ):
            self.assistant.stop_conversation()

        return result

    def _matches_argument(self, argname, condition_value, event_args, result):
        """
        Overrides the default `_matches_argument` method to allow partial
        phrase matches and text extraction.

        Example::

            event_args = {
                'phrase': 'Hey dude turn on the living room lights'
            }

        - `self._matches_argument(argname='phrase', condition_value='Turn on the ${lights} lights')`
          will return `EventMatchResult(is_match=True, parsed_args={ 'lights': 'living room' })`

        - `self._matches_argument(argname='phrase', condition_value='Turn off the ${lights} lights')`
          will return `EventMatchResult(is_match=False, parsed_args={})`

        """

        if event_args.get(argname) == condition_value:
            # In case of an exact match, return immediately
            result.is_match = True
            result.score = sys.maxsize
            return result

        parsed_args = {}
        event_tokens = re.split(r'\s+', event_args.get(argname, '').strip().lower())
        condition_tokens = re.split(r'\s+', condition_value.strip().lower())

        while event_tokens and condition_tokens:
            event_token = event_tokens[0]
            condition_token = condition_tokens[0]

            if event_token == condition_token:
                event_tokens.pop(0)
                condition_tokens.pop(0)
                result.score += 1.5
            elif re.search(condition_token, event_token):
                m = re.search(f'({condition_token})', event_token)
                if m and m.group(1):
                    event_tokens.pop(0)
                    result.score += 1.25

                condition_tokens.pop(0)
            else:
                m = re.match(r'[^\\]*\${(.+?)}', condition_token)
                if m:
                    argname = m.group(1)
                    if argname not in parsed_args:
                        parsed_args[argname] = event_token
                        result.score += 1.0
                    else:
                        parsed_args[argname] += ' ' + event_token

                    if (len(condition_tokens) == 1 and len(event_tokens) == 1) or (
                        len(event_tokens) > 1
                        and len(condition_tokens) > 1
                        and event_tokens[1] == condition_tokens[1]
                    ):
                        # Stop appending tokens to this argument, as the next
                        # condition will be satisfied as well
                        condition_tokens.pop(0)

                    event_tokens.pop(0)
                else:
                    result.score -= 1.0
                    event_tokens.pop(0)

        # It's a match if all the tokens in the condition string have been satisfied
        result.is_match = len(condition_tokens) == 0
        if result.is_match:
            result.parsed_args = parsed_args

        return result


class IntentRecognizedEvent(AssistantEvent):
    """
    Event triggered when an intent is matched by a speech command.
    """

    def __init__(
        self, *args, intent: str, slots: Optional[Mapping[str, Any]] = None, **kwargs
    ):
        """
        :param intent: The intent that has been matched.
        :param slots: The slots extracted from the intent, as a key-value mapping.
        """
        super().__init__(*args, intent=intent, slots=slots or {}, **kwargs)

    def matches_condition(self, condition):
        """
        Overrides matches condition, and stops the conversation to prevent the
        default assistant response if the event matched some event hook condition.
        """
        result = super().matches_condition(condition)
        if (
            result.is_match
            and self.assistant
            and self.assistant.stop_conversation_on_speech_match
        ):
            self.assistant.stop_conversation()

        return result

    def _matches_argument(
        self, argname, condition_value, event_args, result: EventMatchResult
    ):
        if argname != 'slots':
            return super()._matches_argument(
                argname, condition_value, event_args, result
            )

        event_slots = set(event_args.get(argname, {}).items())
        slots = set(self.args.get(argname, {}).items())

        # All the slots in the condition must be in the event
        if slots.difference(event_slots) == 0:
            result.is_match = True
            result.score += 1
        else:
            result.is_match = False
            result.score = 0

        return result


class HotwordDetectedEvent(AssistantEvent):
    """
    Event triggered when a custom hotword is detected
    """

    def __init__(self, *args, hotword: Optional[str] = None, **kwargs):
        """
        :param hotword: The detected user hotword.
        """
        super().__init__(*args, hotword=hotword, **kwargs)


class VolumeChangedEvent(AssistantEvent):
    """
    Event triggered when the volume of the assistant changes.
    """

    def __init__(self, *args, volume: float, **kwargs):
        super().__init__(*args, volume=volume, **kwargs)


class AlertStartedEvent(AssistantEvent):
    """
    Event triggered when an alert starts on the assistant
    """


class AlertEndEvent(AssistantEvent):
    """
    Event triggered when an alert ends on the assistant
    """


class AlarmStartedEvent(AlertStartedEvent):
    """
    Event triggered when an alarm starts on the assistant
    """


class AlarmEndEvent(AlertEndEvent):
    """
    Event triggered when an alarm ends on the assistant
    """


class TimerStartedEvent(AlertStartedEvent):
    """
    Event triggered when a timer starts on the assistant
    """


class TimerEndEvent(AlertEndEvent):
    """
    Event triggered when a timer ends on the assistant
    """


class MicMutedEvent(AssistantEvent):
    """
    Event triggered when the microphone is muted.
    """


class MicUnmutedEvent(AssistantEvent):
    """
    Event triggered when the microphone is muted.
    """


# vim:sw=4:ts=4:et:
