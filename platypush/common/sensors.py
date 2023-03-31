from typing import Iterable, Mapping, Union

Numeric = Union[float, int]
SensorDataType = Union[Numeric, Mapping[str, Numeric], Iterable[Numeric]]
"""
Numeric sensor data published by integrations can be either of:

    - ``int``/``float``
    - Mapping of ``str -> int/float``
    - List of ``int``/``float``
"""
