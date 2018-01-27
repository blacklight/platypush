from platypush.message.event.http import HttpEvent

class NewFeedEvent(HttpEvent):
    def __init__(self, request, response, *args, **kwargs):
        super().__init__(request=request, response=response, *args, **kwargs)


# vim:sw=4:ts=4:et:

