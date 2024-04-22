from dataclasses import dataclass
from time import time
from typing import Optional

from ._intent import Intent


@dataclass
class ConversationContext:
    """
    Context of the conversation process.
    """

    transcript: str = ''
    is_final: bool = False
    intent: Optional[Intent] = None
    timeout: Optional[float] = None
    t_start: Optional[float] = None

    def start(self):
        self.reset()
        self.t_start = time()

    def reset(self):
        self.transcript = ''
        self.intent = None
        self.is_final = False
        self.t_start = None

    @property
    def timed_out(self):
        return (
            (
                (not self.transcript and not self.is_final)
                or (not self.intent and not self.is_final)
            )
            and self.timeout
            and self.t_start
            and time() - self.t_start > self.timeout
        ) or (
            (
                (self.transcript and not self.is_final)
                or (self.intent and not self.is_final)
            )
            and self.timeout
            and self.t_start
            and time() - self.t_start > self.timeout * 2
        )


# vim:sw=4:ts=4:et:
