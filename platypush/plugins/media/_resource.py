from dataclasses import dataclass
from typing import Optional


@dataclass
class MediaResource:
    """
    Models a media resource
    """

    resource: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None
    image: Optional[str] = None
    duration: Optional[float] = None
    channel: Optional[str] = None
    channel_url: Optional[str] = None
    type: Optional[str] = None
    resolution: Optional[str] = None
