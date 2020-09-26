import logging

from platypush.context import get_backend, get_plugin
from platypush.message.event import Event


class AssistantEvent(Event):
    """ Base class for assistant events """

    def __init__(self, assistant=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('platypush:assistant')

        if assistant:
            self._assistant = assistant
        else:
            self._assistant = get_backend('assistant.google')

            if not self._assistant:
                self._assistant = get_plugin('assistant.google.pushtotalk')

            if not self._assistant:
                self.logger.warning('Assistant plugin/backend not configured/initialized')
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

        super().__init__(*args, phrase=phrase, **kwargs)
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


class VolumeChangedEvent(AssistantEvent):
    """
    Event triggered when the volume of the assistant changes
    """

    def __init__(self, volume, *args, **kwargs):
        super().__init__(*args, volume=volume, **kwargs)


class AlertStartedEvent(AssistantEvent):
    """
    Event triggered when an alert starts on the assistant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AlertEndEvent(AssistantEvent):
    """
    Event triggered when an alert ends on the assistant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AlarmStartedEvent(AlertStartedEvent):
    """
    Event triggered when an alarm starts on the assistant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AlarmEndEvent(AlertEndEvent):
    """
    Event triggered when an alarm ends on the assistant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TimerStartedEvent(AlertStartedEvent):
    """
    Event triggered when a timer starts on the assistant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TimerEndEvent(AlertEndEvent):
    """
    Event triggered when a timer ends on the assistant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MicMutedEvent(AssistantEvent):
    """
    Event triggered when the microphone is muted.
    """
    pass


class MicUnmutedEvent(AssistantEvent):
    """
    Event triggered when the microphone is muted.
    """
    pass


# vim:sw=4:ts=4:et:
