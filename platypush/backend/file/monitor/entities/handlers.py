import os

from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler, RegexMatchingEventHandler

from platypush.backend.file.monitor.entities.resources import MonitoredResource, MonitoredPattern, MonitoredRegex
from platypush.context import get_bus
from platypush.message.event.file import FileSystemModifyEvent, FileSystemCreateEvent, FileSystemDeleteEvent


class EventHandler(FileSystemEventHandler):
    """
    Base class for Watchdog event handlers.
    """
    def __init__(self, resource: MonitoredResource, **kwargs):
        super().__init__(**kwargs)
        resource.path = os.path.expanduser(resource.path)
        self.resource = resource

    def on_created(self, event):
        get_bus().post(FileSystemCreateEvent(path=event.src_path, is_directory=event.is_directory))

    def on_deleted(self, event):
        get_bus().post(FileSystemDeleteEvent(path=event.src_path, is_directory=event.is_directory))

    def on_modified(self, event):
        get_bus().post(FileSystemModifyEvent(path=event.src_path, is_directory=event.is_directory))

    def on_moved(self, event):
        pass

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
        super().__init__(resource=resource,
                         patterns=resource.patterns,
                         ignore_patterns=resource.ignore_patterns,
                         ignore_directories=resource.ignore_directories,
                         case_sensitive=resource.case_sensitive)


class RegexEventHandler(EventHandler, RegexMatchingEventHandler):
    """
    Event handler for regex-based file patterns.
    """
    def __init__(self, resource: MonitoredRegex):
        super().__init__(resource=resource,
                         regexes=resource.regexes,
                         ignore_regexes=resource.ignore_regexes,
                         ignore_directories=resource.ignore_directories,
                         case_sensitive=resource.case_sensitive)
