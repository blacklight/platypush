from platypush.message.event import Event


class DashboardIframeUpdateEvent(Event):
    """
    Deliver a DashboardIframeUpdateEvent if you are using the web dashboard
    and you want the connected web clients to show a certain URL in the iframe
    modal window for (optionally) a certain time.
    """

    def __init__(self, url, width=None, height=None, timeout=None, *args, **kwargs):
        """
        :param url: URL to show in the iframe dashboard element
        :type url: str

        :param width: Iframe width, as int (pixels) or CSS string
        :param height: Iframe height, as int (pixels) or CSS string

        :param timeout: If set, the iframe will be closed after this time (in seconds)
        :type timeout: float
        """

        super().__init__(url=url, width=width, height=height, timeout=timeout, *args, **kwargs)


# vim:sw=4:ts=4:et:

