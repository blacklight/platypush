import os
import subprocess
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

        * To interact with your system (and control plugins and backends) through the Platypush web panel,
          by default available on your web root document. Any plugin that you have configured and available as a panel
          plugin will appear on the web panel as well as a tab.

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
        * **uwsgi** (``pip install uwsgi`` plus uwsgi server installed on your
            system if required) - optional but recommended. By default the
            Platypush web server will run in a process spawned on the fly by
            the HTTP backend. However, being a Flask app, it will serve clients
            in a single thread and won't support many features of a full-blown
            web server.

    Base command to run the web server over uwsgi::

        uwsgi --http :8008 --module platypush.backend.http.uwsgi --master --processes 4 --threads 4

    Bear in mind that the main webapp is defined in ``platypush.backend.http.app:application``
    and the WSGI startup script is stored under ``platypush/backend/http/uwsgi.py``.
    """

    _DEFAULT_HTTP_PORT = 8008
    _DEFAULT_WEBSOCKET_PORT = 8009

    def __init__(self, port=_DEFAULT_HTTP_PORT,
                 websocket_port=_DEFAULT_WEBSOCKET_PORT,
                 disable_websocket=False, dashboard=None, resource_dirs=None,
                 ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None,
                 maps=None, run_externally=False, uwsgi_args=None, **kwargs):
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

        :param ssl_cafile: Set it to the path of your certificate authority file if you want to enable HTTPS
            (default: None)
        :type ssl_cafile: str

        :param ssl_capath: Set it to the path of your certificate authority directory if you want to enable HTTPS
            (default: None)
        :type ssl_capath: str

        :param resource_dirs: Static resources directories that will be
            accessible through ``/resources/<path>``. It is expressed as a map
            where the key is the relative path under ``/resources`` to expose and
            the value is the absolute path to expose.
        :type resource_dirs: dict[str, str]

        :param dashboard: Set it if you want to use the dashboard service. It will contain the configuration for the
            widgets to be used (look under ``platypush/backend/http/templates/widgets/`` for the available widgets).

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
                        # Absolute path (valid as long as it's a subdirectory of one of the available `resource_dirs`)
                        images_path: ~/Dropbox/Photos/carousel
                        refresh_seconds: 15
                    -
                        widget: rss-news           # RSS feeds widget
                        # Requires backend.http.poll to be enabled with some RSS sources and write them to sqlite db
                        columns: 6
                        limit: 25
                        db: "sqlite:////home/user/.local/share/platypush/feeds/rss.db"

        :type dashboard: dict

        :param run_externally: If set, then the HTTP backend will not directly
            spawn the web server. Set this option if you plan to run the webapp
            in a separate web server (recommended), like uwsgi or uwsgi+nginx.
        :type run_externally: bool

        :param uwsgi_args: If ``run_externally`` is set and you would like the
            HTTP backend to directly spawn and control the uWSGI application
            server instance, then pass the list of uWSGI arguments through
            this parameter. Some examples include::

                # Start uWSGI instance listening on HTTP port 8008 with 4
                # processes
                ['--plugin', 'python', '--http-socket', ':8008', '--master', '--processes', '4']

                # Start uWSGI instance listening on uWSGI socket on port 3031.
                # You can then use another full-blown web server, like nginx
                # or Apache, to communicate with the uWSGI instance
                ['--plugin', 'python', '--socket', '127.0.0.1:3031', '--master', '--processes', '4']
        :type uwsgi_args: list[str]
        """

        super().__init__(**kwargs)

        self.port = port
        self.websocket_port = websocket_port
        self.dashboard = dashboard or {}
        self.maps = maps or {}
        self.server_proc = None
        self.disable_websocket = disable_websocket
        self.websocket_thread = None

        if resource_dirs:
            self.resource_dirs = {name: os.path.abspath(
                os.path.expanduser(d)) for name, d in resource_dirs.items()}
        else:
            self.resource_dirs = {}

        self.active_websockets = set()
        self.run_externally = run_externally
        self.uwsgi_args = uwsgi_args or []
        self.ssl_context = get_ssl_server_context(ssl_cert=ssl_cert,
                                                  ssl_key=ssl_key,
                                                  ssl_cafile=ssl_cafile,
                                                  ssl_capath=ssl_capath) \
            if ssl_cert else None

        if self.uwsgi_args:
            self.uwsgi_args = [str(_) for _ in self.uwsgi_args] + \
                ['--module', 'platypush.backend.http.uwsgi', '--enable-threads']

        self.local_base_url = '{proto}://localhost:{port}'.\
            format(proto=('https' if ssl_cert else 'http'), port=self.port)

        self._websocket_lock_timeout = 10
        self._websocket_lock = threading.RLock()
        self._websocket_locks = {}

    def send_message(self, msg, **kwargs):
        self.logger.warning('Use cURL or any HTTP client to query the HTTP backend')

    def on_stop(self):
        """ On backend stop """
        super().on_stop()
        self.logger.info('Received STOP event on HttpBackend')

        if self.server_proc:
            if isinstance(self.server_proc, subprocess.Popen):
                self.server_proc.kill()
                self.server_proc.wait()
            else:
                self.server_proc.terminate()
                self.server_proc.join()

    def _acquire_websocket_lock(self, ws):
        try:
            acquire_ok = self._websocket_lock.acquire(timeout=self._websocket_lock_timeout)
            if not acquire_ok:
                raise TimeoutError('Websocket lock acquire timeout')

            addr = ws.remote_address
            if addr not in self._websocket_locks:
                self._websocket_locks[addr] = threading.RLock()
        finally:
            self._websocket_lock.release()

        acquire_ok = self._websocket_locks[addr].acquire(timeout=self._websocket_lock_timeout)
        if not acquire_ok:
            raise TimeoutError('Websocket on address {} not ready to receive data'.format(addr))

    def _release_websocket_lock(self, ws):
        try:
            acquire_ok = self._websocket_lock.acquire(timeout=self._websocket_lock_timeout)
            if not acquire_ok:
                raise TimeoutError('Websocket lock acquire timeout')

            addr = ws.remote_address
            if addr in self._websocket_locks:
                self._websocket_locks[addr].release()
        except Exception as e:
            self.logger.warning('Unhandled exception while releasing websocket lock: {}'.format(str(e)))
        finally:
            self._websocket_lock.release()

    def notify_web_clients(self, event):
        """ Notify all the connected web clients (over websocket) of a new event """
        import websockets

        async def send_event(ws):
            try:
                self._acquire_websocket_lock(ws)
                await ws.send(str(event))
            except Exception as e:
                self.logger.warning('Error on websocket send_event: {}'.format(e))
            finally:
                self._release_websocket_lock(ws)

        loop = get_or_create_event_loop()
        wss = self.active_websockets.copy()

        for _ws in wss:
            try:
                loop.run_until_complete(send_event(_ws))
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning('Websocket client {} connection lost'.format(_ws.remote_address))
                self.active_websockets.remove(_ws)
                if _ws.remote_address in self._websocket_locks:
                    del self._websocket_locks[_ws.remote_address]

    def websocket(self):
        """ Websocket main server """
        import websockets
        set_thread_name('WebsocketServer')

        async def register_websocket(websocket, path):
            address = websocket.remote_address if websocket.remote_address \
                else '<unknown client>'

            self.logger.info('New websocket connection from {} on path {}'.format(address, path))
            self.active_websockets.add(websocket)

            try:
                await websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('Websocket client {} closed connection'.format(address))
                self.active_websockets.remove(websocket)
                if address in self._websocket_locks:
                    del self._websocket_locks[address]

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
            self.logger.info('Starting local web server on port {}'.format(self.port))
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
        self.register_service(port=self.port)

        if not self.disable_websocket:
            self.logger.info('Initializing websocket interface')
            self.websocket_thread = threading.Thread(target=self.websocket)
            self.websocket_thread.start()

        if not self.run_externally:
            self.server_proc = Process(target=self._start_web_server(),
                                       name='WebServer')
            self.server_proc.start()
            self.server_proc.join()
        elif self.uwsgi_args:
            uwsgi_cmd = ['uwsgi'] + self.uwsgi_args
            self.logger.info('Starting uWSGI with arguments {}'.format(uwsgi_cmd))
            self.server_proc = subprocess.Popen(uwsgi_cmd)
        else:
            self.logger.info('The web server is configured to be launched externally but ' +
                             'no uwsgi_args were provided. Make sure that you run another external service' +
                             'for the webserver (e.g. nginx)')


# vim:sw=4:ts=4:et:
