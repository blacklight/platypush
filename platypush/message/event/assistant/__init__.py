import logging
import re

from platypush.context import get_backend
from platypush.message.event import Event, EventMatchResult

logger = logging.getLogger(__name__)


class AssistantEvent(Event):
    """ Base class for assistant events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._assistant = get_backend('assistant.google')
        except KeyError as e:
            try:
                self._assistant = get_backend('assistant.google.pushtotalk')
            except KeyError as e:
                logger.warning('google.assistant backend not configured/initialized')
                self._assistant = None


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

    def __init__(self, with_follow_on_turn=False, *args, **kwargs):
        """
        :param with_follow_on_turn: Set to true if the conversation expects a user follow-up, false otherwise
        :type with_follow_on_turn: str
        """

        super().__init__(*args, with_follow_on_turn=with_follow_on_turn, **kwargs)


class ConversationTimeoutEvent(ConversationEndEvent):
    """
    Event triggered when a conversation times out
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ResponseEvent(ConversationEndEvent):
    """
    Event triggered when a response is processed by the assistant
    """

    def __init__(self, response_text, *args, **kwargs):
        """
        :param response_text: Response text processed by the assistant
        :type response_text: str
        """

        super().__init__(*args, response_text=response_text, **kwargs)


class NoResponseEvent(ConversationEndEvent):
    """
    Event triggered when a conversation ends with no response
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SpeechRecognizedEvent(AssistantEvent):
    """
    Event triggered when a speech is recognized
    """

    def __init__(self, phrase, *args, **kwargs):
        """
        :param phrase: Recognized user phrase
        :type phrase: str
        """

        super().__init__(phrase=phrase, *args, **kwargs)
        self.recognized_phrase = phrase.strip().lower()

    def matches_condition(self, condition):
        """
        Overrides matches condition, and stops the conversation to prevent the
        default assistant response if the event matched some event hook condition
        """

        result = super().matches_condition(condition)
        if result.is_match and self._assistant and 'phrase' in condition.args:
            self._assistant.stop_conversation()

        return result


class HotwordDetectedEvent(AssistantEvent):
    """
    Event triggered when a custom hotword is detected
    """

    def __init__(self, hotword=None, *args, **kwargs):
        """
        :param hotword: The detected user hotword
        :type hotword: str
        """

        super().__init__(*args, hotword=hotword, **kwargs)


# vim:sw=4:ts=4:et:

