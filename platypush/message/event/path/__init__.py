from platypush.message.event import Event


class PathOpenEvent(Event):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path=path, *args, **kwargs)

class PathCloseEvent(Event):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path=path, *args, **kwargs)

class PathCreateEvent(Event):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path=path, *args, **kwargs)

class PathDeleteEvent(Event):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path=path, *args, **kwargs)

class PathModifyEvent(Event):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path=path, *args, **kwargs)

class PathPermissionsChangeEvent(Event):
    def __init__(self, path, umask, *args, **kwargs):
        super().__init__(path=path, umask=umask, *args, **kwargs)


# vim:sw=4:ts=4:et:

