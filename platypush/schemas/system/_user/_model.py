from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    System user wrapper.
    """

    username: str
    terminal: Optional[str] = None
    started: Optional[datetime] = None
    pid: Optional[int] = None
