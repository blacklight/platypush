from platypush.message.event import Event

class HttpEvent(Event):
    """
    Event triggered upon HTTP request/response cycle completion
    """

    def __init__(self, request, response, *args, **kwargs):
        """
        :param request: Reference to the original HTTP request
        :type request: dict

        :param response: The server response
        :type response: dict
        """

        super().__init__(request=request, response=response, *args, **kwargs)


# vim:sw=4:ts=4:et:

