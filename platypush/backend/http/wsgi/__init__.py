from gunicorn.app.wsgiapp import WSGIApplication


class WSGIApplicationWrapper(WSGIApplication):
    """
    Wrapper for the Flask application into a WSGI application.
    """

    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None  # type: ignore
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)  # type: ignore
