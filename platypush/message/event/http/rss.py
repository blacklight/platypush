from platypush.message.event.http import HttpEvent


class NewFeedEvent(HttpEvent):
    """
    Event triggered when a monitored RSS feed has some new content
    """

    def __init__(self, request, response: list, source_id=None, source_title=None, source_url=None, title=None,
                 digest_format=None, digest_filename=None, *args, **kwargs):
        """
        :param request: Original request
        :param response: Received response
        :param source_id: ID of the source that generated the event
        :param source_title: Name of the source, if available
        :param source_url: URL of the source
        :param title: Title of the new element
        :param digest_format: Format of the digest - either 'html' or 'pdf', if set
        :param digest_filename: File name of the digest, if it was dumped to file
        """
        super().__init__(request=request, response=response, source_id=source_id, source_title=source_title,
                         source_url=source_url, digest_format=digest_format, title=title,
                         digest_filename=digest_filename, *args, **kwargs)


# vim:sw=4:ts=4:et:
