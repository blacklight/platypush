from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Process:
    """
    System process data class.
    """

    pid: int
    name: str
    parent_pid: Optional[int] = None
    username: Optional[str] = None
    command_line: List[str] = field(default_factory=list)
    status: Optional[str] = None
    terminal: Optional[str] = None
    current_directory: Optional[str] = None
    started: Optional[datetime] = None
    cpu_percent: float = 0
    memory_percent: float = 0
