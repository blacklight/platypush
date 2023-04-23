from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from platypush.schemas.dataclasses import percent_field


@dataclass
class Process:
    """
    System process data class.
    """

    pid: int = field(
        metadata={
            'metadata': {
                'description': 'Process PID',
                'example': 12345,
            }
        }
    )

    name: str = field(
        metadata={
            'metadata': {
                'description': 'Process name',
                'example': 'python',
            }
        }
    )

    parent_pid: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'PID of the parent process',
                'example': 1000,
            }
        }
    )

    username: str = field(
        metadata={
            'metadata': {
                'description': 'Username that owns the process',
                'example': 'root',
            }
        }
    )

    command_line: List[str] = field(
        metadata={
            'metadata': {
                'description': 'Command line of the process',
                'example': ['/usr/bin/python', '-m', 'platypush'],
            }
        }
    )

    status: str = field(
        metadata={
            'metadata': {
                'description': 'Process status',
                'example': 'running',
            }
        }
    )

    terminal: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Terminal the process is running on',
                'example': 'pts/1',
            }
        }
    )

    current_directory: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Current directory of the process',
                'example': '/root',
            }
        }
    )

    started: Optional[datetime] = field(
        metadata={
            'metadata': {
                'description': 'When the process started',
            }
        }
    )

    cpu_percent: float = percent_field(
        metadata={
            'metadata': {
                'description': 'Percentage of CPU used by the process, between 0 and 1',
                'example': 0.1,
            }
        }
    )

    memory_percent: float = percent_field(
        metadata={
            'metadata': {
                'description': 'Percentage of memory used by the process, between 0 and 1',
                'example': 0.05,
            }
        }
    )
