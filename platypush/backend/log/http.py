import datetime
import os
import re

from dataclasses import dataclass
from logging import getLogger
from threading import RLock
from typing import List, Optional, Iterable

from platypush.backend.file.monitor import FileMonitorBackend, EventHandler, MonitoredResource
from platypush.context import get_bus
from platypush.message.event.log.http import HttpLogEvent

logger = getLogger(__name__)


class LogEventHandler(EventHandler):
    http_line_regex = re.compile(r'^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+\[([^]]+)]\s+"([^"]+)"\s+([\d]+)\s+'
                                 r'([\d]+)\s*("([^"\s]+)")?\s*("([^"]+)")?$')

    @dataclass
    class FileResource:
        path: str
        pos: int = 0
        lock: RLock = RLock()
        last_timestamp: Optional[datetime.datetime] = None

    def __init__(self, *args, monitored_files: Optional[Iterable[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._monitored_files = {}
        self.monitor_files(monitored_files or [])

    def monitor_files(self, files: Iterable[str]):
        self._monitored_files.update({
            f: self.FileResource(path=f, pos=self._get_size(f))
            for f in files
        })

    @staticmethod
    def _get_size(file: str) -> int:
        try:
            return os.path.getsize(file)
        except Exception as e:
            logger.warning('Could not open {}: {}'.format(file, str(e)))
            return 0

    def on_created(self, event):
        self._reset_file(event.src_path)

    def on_deleted(self, event):
        self._reset_file(event.src_path)

    def on_moved(self, event):
        self._reset_file(event.src_path)

    def _reset_file(self, path: str):
        file_info = self._monitored_files.get(path)
        if not file_info:
            return

        file_info.pos = 0

    def on_modified(self, event):
        file_info = self._monitored_files.get(event.src_path)
        if not file_info:
            return

        try:
            file_size = os.path.getsize(event.src_path)
        except OSError as e:
            logger.warning('Could not get the size of {}: {}'.format(event.src_path, str(e)))
            return

        if file_info.pos > file_size:
            logger.warning('The size of {} been unexpectedly decreased from {} to {} bytes'.format(
                event.src_path, file_info.pos, file_size))
            file_info.pos = 0

        try:
            with file_info.lock, open(event.src_path, 'r') as f:
                f.seek(file_info.pos)
                for line in f.readlines():
                    evt = self._build_event(file=event.src_path, line=line)
                    if evt and (not file_info.last_timestamp or evt.args['time'] >= file_info.last_timestamp):
                        get_bus().post(evt)
                        file_info.last_timestamp = evt.args['time']

                file_info.pos = f.tell()
        except OSError as e:
            logger.warning('Error while reading from {}: {}'.format(self.resource.path, str(e)))

    @classmethod
    def _build_event(cls, file: str, line: str) -> Optional[HttpLogEvent]:
        line = line.strip()
        if not line:
            return

        m = cls.http_line_regex.match(line.strip())
        if not m:
            logger.warning('Could not parse log line from {}: {}'.format(file, line))
            return

        url = None
        method = 'GET'
        http_version = '1.0'

        try:
            url = m.group(5).split(' ')[1]
            method = m.group(5).split(' ')[0]
            http_version = m.group(5).split(' ')[2].split('/')[1]
        except Exception as e:
            logger.debug(str(e))

        if not url:
            return

        info = {
            'address': m.group(1),
            'user_identifier': m.group(2),
            'user_id': m.group(3),
            'time': datetime.datetime.strptime(m.group(4), '%d/%b/%Y:%H:%M:%S %z'),
            'method': method,
            'url': url,
            'http_version': http_version,
            'status': int(m.group(6)),
            'size': int(m.group(7)),
            'referrer': m.group(9),
            'user_agent': m.group(11),
        }

        for attr, value in info.items():
            if value == '-':
                info[attr] = None

        return HttpLogEvent(logfile=file, **info)


class LogHttpBackend(FileMonitorBackend):
    """
    This backend can be used to monitor one or more HTTP log files (tested on Apache and Nginx) and trigger events
    whenever a new log line is added.

    Triggers:

        * :class:`platypush.message.event.log.http.HttpLogEvent` when a new log line is created.

    Requires:

        * **watchdog** (``pip install watchdog``)

    """

    class EventHandlerFactory:
        @staticmethod
        def from_resource(resource: str) -> LogEventHandler:
            resource = MonitoredResource(resource)
            return LogEventHandler.from_resource(resource)

    def __init__(self, log_files: List[str], **kwargs):
        """
        :param log_files: List of log files to be monitored.
        """
        self.log_files = {os.path.expanduser(log) for log in log_files}
        directories = {os.path.dirname(log) for log in self.log_files}
        super().__init__(paths=directories, **kwargs)

        # noinspection PyProtectedMember
        handlers = self._observer._handlers
        for hndls in handlers.values():
            for hndl in hndls:
                hndl.monitor_files(self.log_files)
