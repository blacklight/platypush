from datetime import datetime, date
from typing import Optional, Union

from dateutil.parser import isoparse
from dateutil.tz import tzutc
from marshmallow import fields


class StrippedString(fields.Function):   # lgtm [py/missing-call-to-init]
    def __init__(self, *args, **kwargs):
        kwargs['serialize'] = self._strip
        kwargs['deserialize'] = self._strip
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs) -> Optional[str]:
        if obj.get(attr) is not None:
            return self._strip(obj.get(attr))

    @staticmethod
    def _strip(value: str):
        return value.strip()


class DateTime(fields.Function):   # lgtm [py/missing-call-to-init]
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


class Date(fields.Function):   # lgtm [py/missing-call-to-init]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = {
            'example': date.today().isoformat(),
            **(self.metadata or {}),
        }

    def _serialize(self, value, attr, obj, **kwargs) -> Optional[str]:
        value = normalize_datetime(obj.get(attr))
        if value:
            return date(value.year, value.month, value.day).isoformat()

    def _deserialize(self, value, attr, data, **kwargs) -> Optional[date]:
        dt = normalize_datetime(value)
        return date.fromtimestamp(dt.timestamp())


def normalize_datetime(dt: Union[str, date, datetime]) -> Optional[Union[date, datetime]]:
    if not dt:
        return
    if isinstance(dt, datetime) or isinstance(dt, date):
        return dt

    try:
        dt = float(dt)
        return datetime.fromtimestamp(dt)
    except (TypeError, ValueError):
        return isoparse(dt)
