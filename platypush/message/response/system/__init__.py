from datetime import datetime
from typing import Optional, List

from platypush.message.response import Response


class SystemResponse(Response):
    pass


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


class ProcessResponseList(SystemResponseList):
    def __init__(self, responses: List[ProcessResponse], *args, **kwargs):
        super().__init__(responses=responses, *args, **kwargs)


# vim:sw=4:ts=4:et:
