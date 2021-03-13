from platypush.message.event import Event


class FileSystemEvent(Event):
    """
    Base class for file system events - namely, file/directory creation, deletion and modification.
    """
    def __init__(self, path: str, *, is_directory: bool, **kwargs):
        super().__init__(path=path, is_directory=is_directory, **kwargs)


class FileSystemCreateEvent(FileSystemEvent):
    """
    Event triggered when a monitored file or directory is created.
    """


class FileSystemDeleteEvent(FileSystemEvent):
    """
    Event triggered when a monitored file or directory is deleted.
    """


class FileSystemModifyEvent(FileSystemEvent):
    """
    Event triggered when a monitored file or directory is modified.
    """
