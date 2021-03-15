from datetime import datetime
from typing import Optional

from platypush.message.event import Event


class HttpLogEvent(Event):
    """
    Event triggered when a new HTTP log entry is created.
    """
    def __init__(self, logfile: str, address: str, time: datetime, method: str, url: str, status: int, size: int,
                 http_version: str = '1.0', user_id: Optional[str] = None, user_identifier: Optional[str] = None,
                 referrer: Optional[str] = None, user_agent: Optional[str] = None, **kwargs):
        super().__init__(logfile=logfile, address=address, time=time, method=method, url=url, status=status, size=size,
                         http_version=http_version, user_id=user_id, user_identifier=user_identifier, referrer=referrer,
                         user_agent=user_agent, **kwargs)
