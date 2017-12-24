import re

from platypush.context import get_backend
from platypush.message.event import Event, EventMatchResult

class AssistantEvent(Event):
    """ Base class for assistant events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._assistant = get_backend('assistant.google')


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
        result = EventMatchResult(is_match=False, score=0)

        if not isinstance(self, condition.type): return result

        recognized_tokens = re.split('\s+', self.recognized_phrase.strip().lower())
        condition_tokens = re.split('\s+', condition.args['phrase'].strip().lower())

        while recognized_tokens and condition_tokens:
            rec_token = recognized_tokens[0]
            cond_token = condition_tokens[0]

            if rec_token == cond_token:
                recognized_tokens.pop(0)
                condition_tokens.pop(0)
                result.score += 1
            elif re.search(cond_token, rec_token):
                condition_tokens.pop(0)
            else:
                m = re.match('^\$([\w\d_])', cond_token)
                if m:
                    result.parsed_args[cond_token[1:]] = rec_token
                    recognized_tokens.pop(0)
                    condition_tokens.pop(0)
                    result.score += 1
                else:
                    recognized_tokens.pop(0)

        result.is_match = len(condition_tokens) == 0
        if result.is_match and self._assistant: self._assistant.stop_conversation()

        return result


# vim:sw=4:ts=4:et:

