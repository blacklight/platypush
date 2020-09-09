import os

from platypush.backend import Backend
from platypush.message.event.inotify import InotifyCreateEvent, InotifyDeleteEvent, \
    InotifyOpenEvent, InotifyModifyEvent, InotifyCloseEvent, InotifyAccessEvent, InotifyMovedEvent


class InotifyBackend(Backend):
    """
    (Linux only) This backend will listen for events on the filesystem (whether
    a file/directory on a watch list is opened, modified, created, deleted,
    closed or had its permissions changed) and will trigger a relevant event.

    Triggers:

        * :class:`platypush.message.event.inotify.InotifyCreateEvent` if a resource is created
        * :class:`platypush.message.event.inotify.InotifyAccessEvent` if a resource is accessed
        * :class:`platypush.message.event.inotify.InotifyOpenEvent` if a resource is opened
        * :class:`platypush.message.event.inotify.InotifyModifyEvent` if a resource is modified
        * :class:`platypush.message.event.inotify.InotifyPermissionsChangeEvent` if the permissions of a resource are changed
        * :class:`platypush.message.event.inotify.InotifyCloseEvent` if a resource is closed
        * :class:`platypush.message.event.inotify.InotifyDeleteEvent` if a resource is removed

    Requires:

        * **inotify** (``pip install inotify``)

    """

    inotify_watch = None

    def __init__(self, watch_paths=None, **kwargs):
        """
        :param watch_paths: Filesystem resources to watch for events
        :type watch_paths: str
        """

        super().__init__(**kwargs)
        self.watch_paths = set(map(
            lambda path: os.path.abspath(os.path.expanduser(path)),
            watch_paths if watch_paths else []))

    def _cleanup(self):
        if not self.inotify_watch:
            return

        for path in self.watch_paths:
            self.inotify_watch.remove_watch(path)

        self.inotify_watch = None

    def run(self):
        import inotify.adapters
        super().run()

        self.inotify_watch = inotify.adapters.Inotify()
        for path in self.watch_paths:
            self.inotify_watch.add_watch(path)

        moved_file = None
        self.logger.info('Initialized inotify file monitoring backend, monitored resources: {}'
                         .format(self.watch_paths))

        try:
            for inotify_event in self.inotify_watch.event_gen():
                if inotify_event is not None:
                    (header, inotify_types, watch_path, filename) = inotify_event
                    event = None
                    resource_type = inotify_types[1] if len(inotify_types) > 1 else None

                    if moved_file:
                        new = filename if 'IN_MOVED_TO' in inotify_types else None
                        event = InotifyMovedEvent(path=watch_path, old=moved_file, new=new)
                        moved_file = None

                    if 'IN_OPEN' in inotify_types:
                        event = InotifyOpenEvent(path=watch_path, resource=filename, resource_type=resource_type)
                    elif 'IN_ACCESS' in inotify_types:
                        event = InotifyAccessEvent(path=watch_path, resource=filename, resource_type=resource_type)
                    elif 'IN_CREATE' in inotify_types:
                        event = InotifyCreateEvent(path=watch_path, resource=filename, resource_type=resource_type)
                    elif 'IN_MOVED_FROM' in inotify_types:
                        moved_file = filename
                    elif 'IN_MOVED_TO' in inotify_types and not moved_file:
                        event = InotifyMovedEvent(path=watch_path, old=None, new=filename)
                    elif 'IN_DELETE' in inotify_types:
                        event = InotifyDeleteEvent(path=watch_path, resource=filename, resource_type=resource_type)
                    elif 'IN_MODIFY' in inotify_types:
                        event = InotifyModifyEvent(path=watch_path, resource=filename, resource_type=resource_type)
                    elif 'IN_CLOSE_WRITE' in inotify_types or 'IN_CLOSE_NOWRITE' in inotify_types:
                        event = InotifyCloseEvent(path=watch_path, resource=filename, resource_type=resource_type)

                    if event:
                        self.bus.post(event)
        finally:
            self._cleanup()


# vim:sw=4:ts=4:et:
