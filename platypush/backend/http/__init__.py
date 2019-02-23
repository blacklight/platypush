import os
import threading

from multiprocessing import Process

from platypush.backend import Backend
from platypush.backend.http.app import application
from platypush.context import get_or_create_event_loop
from platypush.utils import get_ssl_server_context, set_thread_name


class HttpBackend(Backend):
    """
    The HTTP backend is a general-purpose web server that you can leverage:

        * To execute Platypush commands via HTTP calls. Example::

            curl -XPOST -H 'Content-Type: application/json' -H "X-Token: your_token" \\
                -d '{
                    "type":"request",
                    "target":"nodename",
                    "action":"tts.say",
                    "args": {"phrase":"This is a test"}
                }' \\
                http://localhost:8008/execute

        * To interact with your system (and control plugins and backends) through the Platypush web panel, by default available on your web root document. Any plugin that you have configured and available as a panel plugin will appear on the web panel as well as a tab.

        * To display a fullscreen dashboard with your configured widgets, by default available under ``/dashboard``

        * To stream media over HTTP through the ``/media`` endpoint

    Any plugin can register custom routes under ``platypush/backend/http/app/routes/plugins``.
    Any additional route is managed as a Flask blueprint template and the `.py`
    module can expose lists of routes to the main webapp through the
    ``__routes__`` object (a list of Flask blueprints).

    Note that if you set up a main token, it will be required for any HTTP
    interaction - either as ``X-Token`` HTTP header, on the query string
    (attribute name: ``token``), as part of the JSON payload root (attribute
    name: ``token``), or via HTTP basic auth (any username works).

    Requires:

        * **flask** (``pip install flask``)
        * **redis** (``pip install redis``)
        * **websockets** (``pip install websockets``)
        * **python-dateutil** (``pip install python-dateutil``)
        * **magic** (``pip install python-magic``), optional, for MIME type
            support if you want to enable media streaming
    """

    _DEFAULT_HTTP_PORT = 8008
    _DEFAULT_WEBSOCKET_PORT = 8009

    def __init__(self, port=_DEFAULT_HTTP_PORT,
                 websocket_port=_DEFAULT_WEBSOCKET_PORT,
                 disable_websocket=False, dashboard={}, resource_dirs={},
                 ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None,
                 maps={}, **kwargs):
        """
        :param port: Listen port for the web server (default: 8008)
        :type port: int

        :param websocket_port: Listen port for the websocket server (default: 8009)
        :type websocket_port: int

        :param disable_websocket: Disable the websocket interface (default: False)
        :type disable_websocket: bool

        :param ssl_cert: Set it to the path of your certificate file if you want to enable HTTPS (default: None)
        :type ssl_cert: str

        :param ssl_key: Set it to the path of your key file if you want to enable HTTPS (default: None)
        :type ssl_key: str

        :param ssl_cafile: Set it to the path of your certificate authority file if you want to enable HTTPS (default: None)
        :type ssl_cafile: str

        :param ssl_capath: Set it to the path of your certificate authority directory if you want to enable HTTPS (default: None)
        :type ssl_capath: str

        :param resource_dirs: Static resources directories that will be
            accessible through ``/resources/<path>``. It is expressed as a map
            where the key is the relative path under ``/resources`` to expose and
            the value is the absolute path to expose.
        :type resource_dirs: dict[str, str]

        :param dashboard: Set it if you want to use the dashboard service. It will contain the configuration for the widgets to be used (look under ``platypush/backend/http/templates/widgets/`` for the available widgets).

        Example configuration::

            dashboard:
                background_image: https://site/image.png
                widgets:                # Each row of the dashboard will have 6 columns
                    -
                        widget: calendar           # Calendar widget
                        columns: 6
                    -
                        widget: music              # Music widget
                        columns: 3
                    -
                        widget: date-time-weather  # Date, time and weather widget
                        columns: 3
                    -
                        widget: image-carousel     # Image carousel
                        columns: 6
                        images_path: ~/Dropbox/Photos/carousel  # Absolute path (valid as long as it's a subdirectory of one of the available `resource_dirs`)
                        refresh_seconds: 15
                    -
                        widget: rss-news           # RSS feeds widget
                        # Requires backend.http.poll to be enabled with some RSS sources and write them to sqlite db
                        columns: 6
                        limit: 25
                        db: "sqlite:////home/blacklight/.local/share/platypush/feeds/rss.db"

        :type dashboard: dict
        """

        super().__init__(**kwargs)

        self.port = port
        self.websocket_port = websocket_port
        self.dashboard = dashboard
        self.maps = maps
        self.server_proc = None
        self.disable_websocket = disable_websocket
        self.websocket_thread = None
        self.resource_dirs = { name: os.path.abspath(
            os.path.expanduser(d)) for name, d in resource_dirs.items() }
        self.active_websockets = set()
        self.ssl_context = get_ssl_server_context(ssl_cert=ssl_cert,
                                                  ssl_key=ssl_key,
                                                  ssl_cafile=ssl_cafile,
                                                  ssl_capath=ssl_capath) \
            if ssl_cert else None


    def send_message(self, msg):
        self.logger.warning('Use cURL or any HTTP client to query the HTTP backend')


    def on_stop(self):
        """ On backend stop """
        self.logger.info('Received STOP event on HttpBackend')

        if self.server_proc:
            self.server_proc.terminate()
            self.server_proc.join()

    def notify_web_clients(self, event):
        """ Notify all the connected web clients (over websocket) of a new event """
        import websockets

        async def send_event(websocket):
            try:
                await websocket.send(str(event))
            except Exception as e:
                self.logger.warning('Error on websocket send_event: {}'.format(e))

        loop = get_or_create_event_loop()

        for websocket in self.active_websockets:
            try:
                loop.run_until_complete(send_event(websocket))
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('Client connection lost')
                self.active_websockets.remove(websocket)


    def websocket(self):
        """ Websocket main server """
        import websockets
        set_thread_name('WebsocketServer')

        async def register_websocket(websocket, path):
            address = websocket.remote_address[0] if websocket.remote_address \
                else '<unknown client>'

            self.logger.info('New websocket connection from {}'.format(address))
            self.active_websockets.add(websocket)

            try:
                await websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('Websocket client {} closed connection'.format(address))
                self.active_websockets.remove(websocket)

        websocket_args = {}
        if self.ssl_context:
            websocket_args['ssl'] = self.ssl_context

        loop = get_or_create_event_loop()
        loop.run_until_complete(
            websockets.serve(register_websocket, '0.0.0.0', self.websocket_port,
                             **websocket_args))
        loop.run_forever()

    def _start_web_server(self):
        def proc():
            kwargs = {
                'host': '0.0.0.0',
                'port': self.port,
                'use_reloader': False,
                'debug': False,
            }

            if self.ssl_context:
                kwargs['ssl_context'] = self.ssl_context

            application.run(**kwargs)

        return proc


    def run(self):
        super().run()

        self.server_proc = Process(target=self._start_web_server(),
                                   name='WebServer')
        self.server_proc.start()

        if not self.disable_websocket:
            self.websocket_thread = threading.Thread(target=self.websocket)
            self.websocket_thread.start()

        self.logger.info('Initialized HTTP backend on port {}'.format(self.port))
        self.server_proc.join()


# vim:sw=4:ts=4:et:
