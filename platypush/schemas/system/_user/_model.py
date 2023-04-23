from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    System user wrapper.
    """

    username: str = field(
        metadata={
            'metadata': {
                'description': 'Username',
                'example': 'root',
            }
        }
    )

    terminal: Optional[str] = field(
        metadata={
            'metadata': {
                'description': 'Identifier of the terminal the user is connected to',
                'example': 'pts/1',
            }
        }
    )

    started: Optional[datetime] = field(
        metadata={
            'metadata': {
                'description': 'When the user session started',
            }
        }
    )

    pid: Optional[int] = field(
        metadata={
            'metadata': {
                'description': 'PID of the process that holds the session',
                'example': 12345,
            }
        }
    )
