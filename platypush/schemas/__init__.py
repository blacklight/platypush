from datetime import datetime
from typing import Optional

from marshmallow import fields


class StrippedString(fields.Function):   # lgtm [py/missing-call-to-init]
    def __init__(self, *args, **kwargs):
        kwargs['serialize'] = self._strip
        kwargs['deserialize'] = self._strip
        super().__init__(*args, **kwargs)

    @staticmethod
    def _strip(value: str):
        return value.strip()


def normalize_datetime(dt: str) -> Optional[datetime]:
    if not dt:
        return
    if dt.endswith('Z'):
        dt = dt[:-1] + '+00:00'
    return datetime.fromisoformat(dt)
