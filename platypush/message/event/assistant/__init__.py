import logging
import re

from platypush.context import get_backend
from platypush.message.event import Event, EventMatchResult

class AssistantEvent(Event):
    """ Base class for assistant events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._assistant = get_backend('assistant.google')
        except KeyError as e:
            logging.warning('google.assistant backend not configured/initialized')
            self._assistant = None


class ConversationStartEvent(AssistantEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ConversationEndEvent(AssistantEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SpeechRecognizedEvent(AssistantEvent):
    def __init__(self, phrase, *args, **kwargs):
        super().__init__(phrase=phrase, *args, **kwargs)
        self.recognized_phrase = phrase.strip().lower()

    def matches_condition(self, condition):
        result = super().matches_condition(condition)
        if result.is_match and self._assistant and 'phrase' in condition.args:
            self._assistant.stop_conversation()

        return result


# vim:sw=4:ts=4:et:

