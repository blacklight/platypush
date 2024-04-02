from dataclasses import dataclass
from typing import Optional

from ._common import DEFAULT_TIMEOUT


@dataclass
class MopidyConfig:
    """
    Mopidy configuration.
    """

    host: str = 'localhost'
    port: int = 6680
    ssl: bool = False
    timeout: Optional[float] = DEFAULT_TIMEOUT

    @property
    def url(self) -> str:
        return f'ws{"s" if self.ssl else ""}://{self.host}:{self.port}/mopidy/ws'


# vim:sw=4:ts=4:et:
