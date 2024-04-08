from dataclasses import dataclass
from time import time
from typing import Optional


@dataclass
class ConversationContext:
    """
    Context of the conversation process.
    """

    partial_transcript: str = ''
    is_final: bool = False
    timeout: Optional[float] = None
    t_start: Optional[float] = None
    t_end: Optional[float] = None

    def start(self):
        self.reset()
        self.t_start = time()

    def stop(self):
        self.reset()
        self.t_end = time()

    def reset(self):
        self.partial_transcript = ''
        self.is_final = False
        self.t_start = None
        self.t_end = None

    @property
    def timed_out(self):
        return (
            not self.partial_transcript
            and not self.is_final
            and self.timeout
            and self.t_start
            and time() - self.t_start > self.timeout
        )


# vim:sw=4:ts=4:et:
