import os
from typing import Optional

from platypush.message.event import Event


class InotifyEvent(Event):
    """
    Generic super-class for inotify events.
    """
    def __init__(self, path: str, resource: Optional[str] = None, resource_type: Optional[str] = None,
                 *args, **kwargs):
        """
        :param path: Monitored path.
        :param resource: File/resource name.
        :param resource_type: INotify type of the resource, if available.
        """
        kwargs['full_path'] = os.path.join(path, resource) if resource else path
        super().__init__(*args, path=path, resource=resource,
                         resource_type=self._resource_type_code_to_name(resource_type), **kwargs)

    @staticmethod
    def _resource_type_code_to_name(resource_type: Optional[str] = None) -> Optional[str]:
        if resource_type == 'IN_ISDIR':
            return 'directory'

        return resource_type or 'file'


class InotifyOpenEvent(InotifyEvent):
    """
    Event triggered when a monitored resource is opened.
    """


class InotifyCloseEvent(InotifyEvent):
    """
    Event triggered when a monitored resource is closed.
    """


class InotifyAccessEvent(InotifyEvent):
    """
    Event triggered when a monitored resource is accessed.
    """


class InotifyCreateEvent(InotifyEvent):
    """
    Event triggered when a monitored resource is created.
    """


class InotifyDeleteEvent(InotifyEvent):
    """
    Event triggered when a monitored resource is deleted.
    """


class InotifyModifyEvent(InotifyEvent):
    """
    Event triggered when a monitored resource is modified.
    """


class InotifyMovedEvent(InotifyEvent):
    """
    Event triggered when a resource in a monitored path is moved.
    """
    def __init__(self, path: str, old: Optional[str] = None, new: Optional[str] = None, *args, **kwargs):
        """
        :param path: Monitored path.
        :param old: Old name.
        :param new: New name.
        """
        super().__init__(path=path, old=old, new=new, *args, **kwargs)


class InotifyPermissionsChangeEvent(InotifyEvent):
    """
    Event triggered when the permissions on a monitored resource are changed.
    """
    def __init__(self, path: str, umask: int, resource: Optional[str] = None, *args, **kwargs):
        """
        :param path: Monitored path.
        :param umask: New umask.
        :param resource: File/resource name.
        """
        super().__init__(path=path, resource=resource, umask=umask, *args, **kwargs)


# vim:sw=4:ts=4:et:
