from platypush.message.event import Event


class NgrokEvent(Event):
    """
    ``ngrok`` base event.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NgrokProcessStartedEvent(Event):
    """
    Event triggered when the ``ngrok`` process is started.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NgrokTunnelStartedEvent(Event):
    """
    Event triggered when a tunnel is started.
    """
    def __init__(self, *args, name: str, url: str, protocol: str, **kwargs):
        super().__init__(*args, name=name, url=url, protocol=protocol, **kwargs)


class NgrokTunnelStoppedEvent(Event):
    """
    Event triggered when a tunnel is stopped.
    """
    def __init__(self, *args, name: str, url: str, protocol: str, **kwargs):
        super().__init__(*args, name=name, url=url, protocol=protocol, **kwargs)


class NgrokProcessStoppedEvent(Event):
    """
    Event triggered when the ngrok process is stopped.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
