import logging

class MediaHandler:
    """
    Abstract class to manage media handlers that can be streamed over the HTTP
    server through the `/media` endpoint.
    """

    prefix_handlers = []

    def __init__(self, source, filename=None,
                 mime_type='application/octet-stream', name=None, url=None,
                 subtitles=None):
        matched_handlers = [hndl for hndl in self.prefix_handlers
                            if source.startswith(hndl)]

        if not matched_handlers:
            raise AttributeError(('No matched handlers found for source "{}" ' +
                                  'through {}. Supported handlers: {}').format(
                                      source, self.__class__.__name__,
                                      self.prefix_handlers))

        self.name = name
        self.path = None
        self.filename = filename
        self.source = source
        self.url = url
        self.mime_type = mime_type
        self.subtitles = subtitles
        self.content_length = 0
        self._matched_handler = matched_handlers[0]

    @classmethod
    def build(cls, source, *args, **kwargs):
        errors = {}

        for hndl_class in supported_handlers:
            try:
                return hndl_class(source, *args, **kwargs)
            except Exception as e:
                logging.exception(e)
                errors[hndl_class.__name__] = str(e)

        raise AttributeError(('The source {} has no handlers associated. ' +
                              'Errors: {}').format(source, errors))

    def get_data(self, from_bytes=None, to_bytes=None, chunk_size=None):
        raise NotImplementedError()

    def set_subtitles(self, subtitles_file):
        self.subtitles = subtitles_file

    def remove_subtitles(self):
        self.subtitles = None

    def __iter__(self):
        for attr in ['name', 'source', 'mime_type', 'url', 'subtitles',
                     'prefix_handlers', 'media_id']:
            if hasattr(self, attr):
                yield (attr, getattr(self, attr))


from .file import FileHandler

__all__ = ['MediaHandler', 'FileHandler']


supported_handlers = [eval(hndl) for hndl in __all__
                      if hndl != MediaHandler.__name__]


# vim:sw=4:ts=4:et:
