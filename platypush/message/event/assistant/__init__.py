import re

from platypush.message.event import Event

class AssistantEvent(Event):
    """ Base class for assistant events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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
        if not isinstance(self, condition.type): return [False, {}]

        recognized_tokens = re.split('\s+', self.recognized_phrase.strip().lower())
        condition_tokens = re.split('\s+', condition.args['phrase'].strip().lower())
        parsed_args = {}

        while recognized_tokens and condition_tokens:
            rec_token = recognized_tokens[0]
            cond_token = condition_tokens[0]

            if rec_token == cond_token:
                recognized_tokens.pop(0)
                condition_tokens.pop(0)
            elif re.search(cond_token, rec_token):
                condition_tokens.pop(0)
            else:
                m = re.match('^\$([\w\d_])', cond_token)
                if m:
                    parsed_args[cond_token[1:]] = rec_token
                    recognized_tokens.pop(0)
                    condition_tokens.pop(0)
                else:
                    recognized_tokens.pop(0)

        return [len(condition_tokens) == 0, parsed_args]


# vim:sw=4:ts=4:et:

