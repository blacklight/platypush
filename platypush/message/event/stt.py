from platypush.message.event import Event


class SttEvent(Event):
    """ Base class for speech-to-text events """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SpeechStartedEvent(SttEvent):
    """
    Event triggered when speech starts being detected.
    """
    pass


class SpeechDetectedEvent(SttEvent):
    """
    Event triggered when speech is detected.
    """

    def __init__(self, speech: str, *args, **kwargs):
        """
        :param speech: Speech detected, as a string
        """
        super().__init__(*args, speech=speech.strip(), **kwargs)


class ConversationDetectedEvent(SpeechDetectedEvent):
    """
    Event triggered when speech is detected after a hotword.
    """
    pass

class HotwordDetectedEvent(SttEvent):
    """
    Event triggered when a custom hotword is detected.
    """

    def __init__(self, hotword: str = '', *args, **kwargs):
        """
        :param hotword: The detected user hotword.
        """
        super().__init__(*args, hotword=hotword, **kwargs)


class SpeechDetectionStartedEvent(SttEvent):
    """
    Event triggered when the speech detection engine starts.
    """
    pass


class SpeechDetectionStoppedEvent(SttEvent):
    """
    Event triggered when the speech detection engine stops.
    """
    pass


# vim:sw=4:ts=4:et:
