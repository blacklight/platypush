from platypush.message.event.http import HttpEvent

class NewFeedEvent(HttpEvent):
    def __init__(self, request, response, source_id=None, title=None,
                 digest_format=None, digest_filename=None, *args, **kwargs):

        super().__init__(request=request, response=response, source_id=source_id,
                         digest_format=digest_format, title=title,
                         digest_filename=digest_filename, *args, **kwargs)


# vim:sw=4:ts=4:et:

