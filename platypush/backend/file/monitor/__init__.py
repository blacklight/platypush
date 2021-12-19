from typing import Iterable, Dict, Union, Any

from watchdog.observers import Observer

from platypush.backend import Backend
from .entities.handlers import EventHandler
from .entities.resources import MonitoredResource, MonitoredPattern, MonitoredRegex


class FileMonitorBackend(Backend):
    """
    This backend monitors changes to local files and directories using the Watchdog API.

    Triggers:

        * :class:`platypush.message.event.file.FileSystemCreateEvent` if a resource is created.
        * :class:`platypush.message.event.file.FileSystemDeleteEvent` if a resource is removed.
        * :class:`platypush.message.event.file.FileSystemModifyEvent` if a resource is modified.

    Requires:

        * **watchdog** (``pip install watchdog``)

    """

    class EventHandlerFactory:
        """
        Create a file system event handler from a string, dictionary or ``MonitoredResource`` resource.
        """

        @staticmethod
        def from_resource(resource: Union[str, Dict[str, Any], MonitoredResource]) -> EventHandler:
            if isinstance(resource, str):
                resource = MonitoredResource(resource)
            elif isinstance(resource, dict):
                if 'regexes' in resource or 'ignore_regexes' in resource:
                    resource = MonitoredRegex(**resource)
                elif 'patterns' in resource or 'ignore_patterns' in resource or 'ignore_directories' in resource:
                    resource = MonitoredPattern(**resource)
                else:
                    resource = MonitoredResource(**resource)

            return EventHandler.from_resource(resource)

    def __init__(self, paths: Iterable[Union[str, Dict[str, Any], MonitoredResource]], **kwargs):
        """
        :param paths: List of paths to monitor. Paths can either be expressed in any of the following ways:

            - Simple strings. In this case, paths will be interpreted as absolute references to a file or a directory
              to monitor. Example:

              .. code-block:: yaml

                backend.file.monitor:
                    paths:
                        # Monitor changes on the /tmp folder
                        - /tmp
                        # Monitor changes on /etc/passwd
                        - /etc/passwd

            - Path with monitoring properties expressed as a key-value object. Example showing the supported attributes:

                .. code-block:: yaml

                    backend.file.monitor:
                        paths:
                            # Monitor changes on the /tmp folder and its subfolders
                            - path: /tmp
                              recursive: True

            - Path with pattern-based search criteria for the files to monitor and exclude. Example:

                .. code-block:: yaml

                    backend.file.monitor:
                        paths:
                            # Recursively monitor changes on the ~/my-project folder that include all
                            # *.py files, excluding those whose name starts with tmp_ and
                            # all the files contained in the __pycache__ folders
                            - path: ~/my-project
                              recursive: True
                              patterns:
                                - "*.py"
                              ignore_patterns:
                                - "tmp_*"
                              ignore_directories:
                                - "__pycache__"

            - Path with regex-based search criteria for the files to monitor and exclude. Example:

                .. code-block:: yaml

                    backend.file.monitor:
                        paths:
                            # Recursively monitor changes on the ~/my-images folder that include all
                            # the files matching a JPEG extension in case-insensitive mode,
                            # excluding those whose name starts with tmp_ and
                            # all the files contained in the __MACOSX folders
                            - path: ~/my-images
                              recursive: True
                              case_sensitive: False
                              regexes:
                                - '.*\\.jpe?g$'
                              ignore_patterns:
                                - '^tmp_.*'
                              ignore_directories:
                                - '__MACOSX'

        """

        super().__init__(**kwargs)
        self._observer = Observer()

        for path in paths:
            handler = self.EventHandlerFactory.from_resource(path)
            self._observer.schedule(handler, handler.resource.path, recursive=handler.resource.recursive)

    def run(self):
        super().run()
        self.logger.info('Initializing file monitor backend')
        self._observer.start()
        self.wait_stop()

    def on_stop(self):
        self.logger.info('Stopping file monitor backend')
        self._observer.stop()
        self._observer.join()
        self.logger.info('Stopped file monitor backend')
