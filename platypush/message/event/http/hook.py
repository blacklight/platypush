from platypush.message.event import Event

class WebhookEvent(Event):
    """
    Event triggered when a custom webhook is called.
    """

    def __init__(self, hook, method, data=None, args=None, *argv, **kwargs):
        """
        :param hook: Name of the invoked web hook, from http://host:port/hook/<hook>
        :type hook: str

        :param method: HTTP method (in uppercase)
        :type method: str

        :param data: Extra data passed over POST/PUT/DELETE
        :type data: str or dict/list from JSON

        :param args: Extra query string arguments
        :type args: dict
        """

        super().__init__(hook=hook, method=method, data=data, args=args or {}, *argv, **kwargs)


# vim:sw=4:ts=4:et:

