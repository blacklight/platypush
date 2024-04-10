from enum import Enum


class AssistantState(Enum):
    """
    Possible states of the assistant.
    """

    IDLE = 'idle'
    DETECTING_HOTWORD = 'detecting_hotword'
    DETECTING_SPEECH = 'detecting_speech'
    RESPONDING = 'responding'


# vim:sw=4:ts=4:et:
