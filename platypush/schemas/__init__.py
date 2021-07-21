from datetime import datetime
from typing import Optional


def normalize_datetime(dt: str) -> Optional[datetime]:
    if not dt:
        return
    if dt.endswith('Z'):
        dt = dt[:-1] + '+00:00'
    return datetime.fromisoformat(dt)
