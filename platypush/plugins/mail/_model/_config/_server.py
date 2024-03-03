from dataclasses import dataclass
from typing import Optional

from .._transport import TransportEncryption


@dataclass
class ServerConfig:
    """
    Configuration for a mail server.
    """

    server: str
    port: int
    encryption: TransportEncryption
    timeout: float
    keyfile: Optional[str] = None
    certfile: Optional[str] = None
    domain: Optional[str] = None


# vim:sw=4:ts=4:et:
