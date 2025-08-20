import os
import re
from typing import Optional

from watchdog.events import (
    FileSystemEventHandler,
    PatternMatchingEventHandler,
    RegexMatchingEventHandler,
)

from platypush.bus import Bus
from platypush.context import get_bus
from platypush.message.event.file import (
    FileSystemModifyEvent,
    FileSystemCreateEvent,
    FileSystemDeleteEvent,
    FileSystemMovedEvent,
)

from .resources import (
    MonitoredResource,
    MonitoredPattern,
    MonitoredRegex,
)


class EventHandler(FileSystemEventHandler):
    """
    Base class for Watchdog event handlers.
    """

    def __init__(
        self, resource: MonitoredResource, bus: Optional[Bus] = None, **kwargs
    ):
        super().__init__(**kwargs)
        resource.path = os.path.expanduser(resource.path)
        self.resource = resource
        self.bus = bus or get_bus()

    def _should_ignore_event(self, event) -> bool:
        ignore_dirs = [
            os.path.expanduser(
                _dir
                if os.path.expanduser(_dir).strip('/').startswith(self.resource.path)
                else os.path.join(self.resource.path, _dir)
            )
            for _dir in getattr(self.resource, 'ignore_directories', [])
        ]

        ignore_patterns = getattr(self.resource, 'ignore_patterns', None)
        ignore_regexes = getattr(self.resource, 'ignore_regexes', None)

        if ignore_dirs and any(
            event.src_path.startswith(ignore_dir) for ignore_dir in ignore_dirs
        ):
            return True

        if ignore_patterns and any(
            re.match(r'^{}$'.format(pattern.replace('*', '.*')), event.src_path)
            for pattern in ignore_patterns
        ):
            return True

        if ignore_regexes and any(
            re.match(regex, event.src_path) for regex in (ignore_patterns or [])
        ):
            return True

        return False

    def _on_event(self, event, output_event_type, **kwargs):
        if self._should_ignore_event(event):
            return

        self.bus.post(
            output_event_type(
                path=event.src_path, is_directory=event.is_directory, **kwargs
            )
        )

    def on_created(self, event):
        self._on_event(event, FileSystemCreateEvent)

    def on_deleted(self, event):
        self._on_event(event, FileSystemDeleteEvent)

    def on_modified(self, event):
        self._on_event(event, FileSystemModifyEvent)

    def on_moved(self, event):
        self._on_event(event, FileSystemMovedEvent, new_path=event.dest_path)

    @classmethod
    def from_resource(cls, resource: MonitoredResource):
        if isinstance(resource, MonitoredPattern):
            return PatternEventHandler(resource)
        if isinstance(resource, MonitoredRegex):
            return RegexEventHandler(resource)
        return cls(resource)


class PatternEventHandler(EventHandler, PatternMatchingEventHandler):
    """
    Event handler for file patterns.
    """

    def __init__(self, resource: MonitoredPattern):
        super().__init__(
            resource=resource,
            patterns=resource.patterns,
            ignore_patterns=resource.ignore_patterns,
            ignore_directories=resource.ignore_directories,
            case_sensitive=resource.case_sensitive,
        )


class RegexEventHandler(EventHandler, RegexMatchingEventHandler):
    """
    Event handler for regex-based file patterns.
    """

    def __init__(self, resource: MonitoredRegex):
        super().__init__(
            resource=resource,
            regexes=resource.regexes,
            ignore_regexes=resource.ignore_regexes,
            ignore_directories=resource.ignore_directories,
            case_sensitive=resource.case_sensitive,
        )
