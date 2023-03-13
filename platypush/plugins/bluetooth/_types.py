from typing import Union
from uuid import UUID

RawServiceClass = Union[UUID, int]
"""
Raw type for service classes received by pybluez.
Can be either a 16-bit integer or a UUID.
"""
