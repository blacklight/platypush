from platypush.message.event import Event

class HttpEvent(Event):
    def __init__(self, request, response, *args, **kwargs):
        super().__init__(request=request, response=response, *args, **kwargs)


# vim:sw=4:ts=4:et:

