from typing import Iterable, Dict, Optional, Union, Any

from watchdog.observers import Observer

from platypush.plugins import RunnablePlugin

from .entities.handlers import EventHandler
from .entities.resources import MonitoredResource, MonitoredPattern, MonitoredRegex


class FileMonitorPlugin(RunnablePlugin):
    """
    A plugin to monitor changes to files and directories.
    """

    def __init__(
        self, paths: Iterable[Union[str, Dict[str, Any], MonitoredResource]], **kwargs
    ):
        """
        :param paths: List of paths to monitor. Paths can either be expressed
            in any of the following ways:

                - Simple strings. In this case, paths will be interpreted as
                  absolute references to a file or a directory to monitor.
                  Example:

                  .. code-block:: yaml

                    file.monitor:
                        paths:
                            # Monitor changes on the /tmp folder
                            - /tmp
                            # Monitor changes on /etc/passwd
                            - /etc/passwd

                - Path with monitoring properties expressed as a key-value
                  object. Example showing the supported attributes:

                    .. code-block:: yaml

                        file.monitor:
                            paths:
                                # Monitor changes on the /tmp folder and its
                                # subfolders
                                - path: /tmp
                                  recursive: True

                - Path with pattern-based search criteria for the files to monitor
                  and exclude. Example:

                    .. code-block:: yaml

                        file.monitor:
                            paths:
                                # Recursively monitor changes on the
                                # ~/my-project folder that include all *.py
                                # files, excluding those whose name starts with
                                # tmp_ and all the files contained in the
                                # __pycache__ folders
                                - path: ~/my-project
                                  recursive: True
                                  patterns:
                                    - "*.py"
                                  ignore_patterns:
                                    - "tmp_*"
                                  ignore_directories:
                                    - "__pycache__"

                - Path with regex-based search criteria for the files to
                  monitor and exclude. Example:

                    .. code-block:: yaml

                        file.monitor:
                            paths:
                                # Recursively monitor changes on the
                                # ~/my-images folder that include all the files
                                # matching a JPEG extension in case-insensitive
                                # mode, excluding those whose name starts with
                                # tmp_ and all the files contained in the
                                # __MACOSX folders
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
        self.paths = set()

        for path in paths:
            handler = self.event_handler_from_resource(path)
            if not handler:
                continue

            self.paths.add(handler.resource.path)
            self._observer.schedule(
                handler, handler.resource.path, recursive=handler.resource.recursive
            )

    @staticmethod
    def event_handler_from_resource(
        resource: Union[str, Dict[str, Any], MonitoredResource]
    ) -> Optional[EventHandler]:
        """
        Create a file system event handler from a string, dictionary or
        ``MonitoredResource`` resource.
        """

        if isinstance(resource, str):
            res = MonitoredResource(resource)
        elif isinstance(resource, dict):
            if 'regexes' in resource or 'ignore_regexes' in resource:
                res = MonitoredRegex(**resource)
            elif (
                'patterns' in resource
                or 'ignore_patterns' in resource
                or 'ignore_directories' in resource
            ):
                res = MonitoredPattern(**resource)
            else:
                res = MonitoredResource(**resource)
        else:
            return None

        return EventHandler.from_resource(res)

    def stop(self):
        self._observer.stop()
        self._observer.join()
        super().stop()

    def main(self):
        self._observer.start()
        self.wait_stop()
