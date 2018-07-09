from platypush.message.event import Event


class PathOpenEvent(Event):
    """
    Event triggered when a monitored file is opened
    """

    def __init__(self, path, *args, **kwargs):
        """
        :param path: File name
        :type path: str
        """

        super().__init__(path=path, *args, **kwargs)

class PathCloseEvent(Event):
    """
    Event triggered when a monitored file is closed
    """

    def __init__(self, path, *args, **kwargs):
        """
        :param path: File name
        :type path: str
        """

        super().__init__(path=path, *args, **kwargs)

class PathCreateEvent(Event):
    """
    Event triggered when a monitored file is created
    """

    def __init__(self, path, *args, **kwargs):
        """
        :param path: File name
        :type path: str
        """

        super().__init__(path=path, *args, **kwargs)

class PathDeleteEvent(Event):
    """
    Event triggered when a monitored file is deleted
    """

    def __init__(self, path, *args, **kwargs):
        """
        :param path: File name
        :type path: str
        """

        super().__init__(path=path, *args, **kwargs)

class PathModifyEvent(Event):
    """
    Event triggered when a monitored file is modified
    """

    def __init__(self, path, *args, **kwargs):
        """
        :param path: File name
        :type path: str
        """

        super().__init__(path=path, *args, **kwargs)

class PathPermissionsChangeEvent(Event):
    """
    Event triggered when the permissions on a monitored file are changed
    """

    def __init__(self, path, umask, *args, **kwargs):
        """
        :param path: File name
        :type path: str

        :param umask: New file umask
        :type umask: int
        """

        super().__init__(path=path, umask=umask, *args, **kwargs)


# vim:sw=4:ts=4:et:

