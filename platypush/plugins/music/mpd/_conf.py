from dataclasses import dataclass


@dataclass
class MpdConfig:
    """
    MPD configuration
    """

    host: str = 'localhost'
    port: int = 6600
    password: str = ''
