from datetime import datetime
from typing import Optional, Union

from dateutil.parser import isoparse
from dateutil.tz import tzutc
from marshmallow import fields


class StrippedString(fields.Function):   # lgtm [py/missing-call-to-init]
    def __init__(self, *args, **kwargs):
        kwargs['serialize'] = self._strip
        kwargs['deserialize'] = self._strip
        super().__init__(*args, **kwargs)

    @staticmethod
    def _strip(value: str):
        return value.strip()


class DateTime(fields.Function):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = {
            'example': datetime.now(tz=tzutc()).isoformat(),
            **(self.metadata or {}),
        }

    def _serialize(self, value, attr, obj, **kwargs) -> Optional[str]:
        value = normalize_datetime(obj.get(attr))
        if value:
            return value.isoformat()

    def _deserialize(self, value, attr, data, **kwargs) -> Optional[datetime]:
        return normalize_datetime(value)


def normalize_datetime(dt: Union[str, datetime]) -> Optional[datetime]:
    if not dt:
        return
    if isinstance(dt, datetime):
        return dt
    return isoparse(dt)
