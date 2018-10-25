import os
import inotify.adapters

from platypush.backend import Backend
from platypush.message.event.path import PathCreateEvent, PathDeleteEvent, \
    PathOpenEvent, PathModifyEvent, PathPermissionsChangeEvent, PathCloseEvent


class InotifyBackend(Backend):
    """
    (Linux only) This backend will listen for events on the filesystem (whether
    a file/directory on a watch list is opened, modified, created, deleted,
    closed or had its permissions changed) and will trigger a relevant event.

    Triggers:

        * :class:`platypush.message.event.path.PathCreateEvent` if a resource is created
        * :class:`platypush.message.event.path.PathOpenEvent` if a resource is opened
        * :class:`platypush.message.event.path.PathModifyEvent` if a resource is modified
        * :class:`platypush.message.event.path.PathPermissionsChangeEvent` if the permissions of a resource are changed
        * :class:`platypush.message.event.path.PathCloseEvent` if a resource is closed
        * :class:`platypush.message.event.path.PathDeleteEvent` if a resource is removed

    Requires:

        * **inotify** (``pip install inotify``)
    """

    inotify_watch = None

    def __init__(self, watch_paths=[], **kwargs):
        """
        :param watch_paths: Filesystem resources to watch for events
        :type watch_paths: str
        """

        super().__init__(**kwargs)
        self.watch_paths = set(map(
            lambda path: os.path.abspath(os.path.expanduser(path)),
            watch_paths))

    def _cleanup(self):
        if not self.inotify_watch:
            return

        for path in self.watch_paths:
            self.inotify_watch.remove_watch(path)

        self.inotify_watch = None

    def run(self):
        super().run()

        self.inotify_watch = inotify.adapters.Inotify()
        for path in self.watch_paths:
            self.inotify_watch.add_watch(path)

        self.logger.info('Initialized inotify file monitoring backend, monitored resources: {}'
                     .format(self.watch_paths))

        try:
            for inotify_event in self.inotify_watch.event_gen():
                if inotify_event is not None:
                    (header, inotify_types, watch_path, filename) = inotify_event
                    event = None

                    if 'IN_OPEN' in inotify_types:
                        event = PathOpenEvent(path=watch_path)
                    elif 'IN_MODIFY' in inotify_types:
                        event = PathModifyEvent(path=watch_path)
                    elif 'IN_CLOSE_WRITE' in inotify_types or 'IN_CLOSE_NOWRITE' in inotify_types:
                        event = PathCloseEvent(path=watch_path)

                    if event:
                        self.bus.post(event)
        finally:
            self._cleanup()


# vim:sw=4:ts=4:et:

