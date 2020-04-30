from datetime import datetime
from typing import Optional

from platypush.message.event import Event


class Covid19UpdateEvent(Event):
    def __init__(self,
                 confirmed: int,
                 deaths: int,
                 recovered: int,
                 country: Optional[str] = None,
                 country_code: Optional[str] = None,
                 update_time: Optional[datetime] = None,
                 *args, **kwargs):
        super().__init__(*args,
                         confirmed=confirmed,
                         deaths=deaths,
                         recovered=recovered,
                         country=country,
                         country_code=country_code,
                         update_time=update_time,
                         **kwargs)


# vim:sw=4:ts=4:et:
