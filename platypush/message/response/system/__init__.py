from datetime import datetime
from typing import Optional, List

from platypush.message.response import Response


class SystemResponse(Response):
    pass


class CpuResponse(SystemResponse):
    pass


class MemoryResponse(SystemResponse):
    pass


class DiskResponse(SystemResponse):
    pass


class NetworkResponse(SystemResponse):
    pass


class SensorResponse(SystemResponse):
    pass


class SensorTemperatureResponse(SensorResponse):
    def __init__(
        self,
        name: str,
        current: float,
        high: Optional[float] = None,
        critical: Optional[float] = None,
        label: Optional[str] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            *args,
            output={
                'name': name,
                'current': current,
                'high': high,
                'critical': critical,
                'label': label,
            },
            **kwargs
        )


class SensorFanResponse(SensorResponse):
    def __init__(
        self, name: str, current: int, label: Optional[str] = None, *args, **kwargs
    ):
        super().__init__(
            *args,
            output={
                'name': name,
                'current': current,
                'label': label,
            },
            **kwargs
        )


class SensorBatteryResponse(SensorResponse):
    def __init__(
        self, percent: float, secs_left: int, power_plugged: bool, *args, **kwargs
    ):
        super().__init__(
            *args,
            output={
                'percent': percent,
                'secs_left': secs_left,
                'power_plugged': power_plugged,
            },
            **kwargs
        )


class ConnectUserResponse(SystemResponse):
    def __init__(
        self,
        name: str,
        terminal: str,
        host: str,
        started: datetime,
        pid: Optional[int] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            *args,
            output={
                'name': name,
                'terminal': terminal,
                'host': host,
                'started': started,
                'pid': pid,
            },
            **kwargs
        )


class ProcessResponse(SystemResponse):
    def __init__(
        self,
        pid: int,
        name: str,
        started: datetime,
        ppid: Optional[int],
        children: Optional[List[int]] = None,
        exe: Optional[List[str]] = None,
        status: Optional[str] = None,
        username: Optional[str] = None,
        terminal: Optional[str] = None,
        cpu_user_time: Optional[float] = None,
        cpu_system_time: Optional[float] = None,
        cpu_children_user_time: Optional[float] = None,
        cpu_children_system_time: Optional[float] = None,
        mem_rss: Optional[int] = None,
        mem_vms: Optional[int] = None,
        mem_shared: Optional[int] = None,
        mem_text: Optional[int] = None,
        mem_data: Optional[int] = None,
        mem_lib: Optional[int] = None,
        mem_dirty: Optional[int] = None,
        mem_percent: Optional[float] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            *args,
            output={
                'pid': pid,
                'name': name,
                'started': started,
                'ppid': ppid,
                'exe': exe,
                'status': status,
                'username': username,
                'terminal': terminal,
                'cpu_user_time': cpu_user_time,
                'cpu_system_time': cpu_system_time,
                'cpu_children_user_time': cpu_children_user_time,
                'cpu_children_system_time': cpu_children_system_time,
                'mem_rss': mem_rss,
                'mem_vms': mem_vms,
                'mem_shared': mem_shared,
                'mem_text': mem_text,
                'mem_data': mem_data,
                'mem_lib': mem_lib,
                'mem_dirty': mem_dirty,
                'mem_percent': mem_percent,
                'children': children or [],
            },
            **kwargs
        )


class SystemResponseList(SystemResponse):
    def __init__(self, responses: List[SystemResponse], *args, **kwargs):
        super().__init__(output=[r.output for r in responses], *args, **kwargs)


class SensorResponseList(SensorResponse, SystemResponseList):
    def __init__(self, responses: List[SensorResponse], *args, **kwargs):
        super().__init__(responses=responses, *args, **kwargs)


class ConnectedUserResponseList(SystemResponseList):
    def __init__(self, responses: List[ConnectUserResponse], *args, **kwargs):
        super().__init__(responses=responses, *args, **kwargs)


class ProcessResponseList(SystemResponseList):
    def __init__(self, responses: List[ProcessResponse], *args, **kwargs):
        super().__init__(responses=responses, *args, **kwargs)


# vim:sw=4:ts=4:et:
