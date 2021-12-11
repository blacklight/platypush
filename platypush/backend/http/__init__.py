import os
import subprocess
import threading

from multiprocessing import Process

try:
    from websockets.exceptions import ConnectionClosed
    from websockets import serve as websocket_serve
except ImportError:
    from websockets import ConnectionClosed, serve as websocket_serve

from platypush.backend import Backend
from platypush.backend.http.app import application
from platypush.context import get_or_create_event_loop
from platypush.utils import get_ssl_server_context, set_thread_name


class HttpBackend(Backend):
    """
    The HTTP backend is a general-purpose web server.

    Example configuration:

      .. code-block:: yaml

        backend.http:
            # Default HTTP listen port
            port: 8008
            # Default websocket port
            websocket_port: 8009
            # External folders that will be exposed over `/resources/<name>`
            resource_dirs:
                photos: /mnt/hd/photos
                videos: /mnt/hd/videos
                music: /mnt/hd/music

    You can leverage this backend:

        * To execute Platypush commands via HTTP calls. In order to do so:

            * Register a user to Platypush through the web panel (usually served on ``http://host:8008/``).

            * Generate a token for your user, either through the web panel (Settings -> Generate Token) or via API:

                .. code-block:: shell

                    curl -XPOST -H 'Content-Type: application/json' -d '
                      {
                        "username": "$YOUR_USER",
                        "password": "$YOUR_PASSWORD"
                      }' http://host:8008/auth

            * Execute actions through the ``/execute`` endpoint:

                .. code-block:: shell

                    curl -XPOST -H 'Content-Type: application/json' -H "Authorization: Bearer $YOUR_TOKEN" -d '
                      {
                        "type": "request",
                        "action": "tts.say",
                        "args": {
                          "text": "This is a test"
                        }
                      }' http://host:8008/execute

        * To interact with your system (and control plugins and backends) through the Platypush web panel,
          by default available on ``http://host:8008/``. Any configured plugin that has an available panel
          plugin will be automatically added to the web panel.

        * To display a fullscreen dashboard with custom widgets.

            * Widgets are available as Vue.js components under ``platypush/backend/http/webapp/src/components/widgets``.

            * Explore their options (some may require some plugins or backends to be configured in order to work) and
              create a new dashboard template under ``~/.config/platypush/dashboards``- e.g. ``main.xml``:

                .. code-block:: xml

                    <Dashboard>
                        <!-- Display the following widgets on the same row. Each row consists of 12 columns.
                             You can specify the width of each widget either through class name (e.g. col-6 means
                             6 columns out of 12, e.g. half the size of the row) or inline style
                             (e.g. `style="width: 50%"`). -->
                        <Row>
                            <!-- Show a calendar widget with the upcoming events. It requires the `calendar` plugin to
                                 be enabled and configured. -->
                            <Calendar class="col-6" />

                            <!-- Show the current track and other playback info. It requires `music.mpd` plugin or any
                                 other music plugin enabled. -->
                            <Music class="col-3" />

                            <!-- Show current date, time and weather. It requires a `weather` plugin or backend enabled -->
                            <DateTimeWeather class="col-3" />
                        </Row>

                        <!-- Display the following widgets on a second row -->
                        <Row>
                            <!-- Show a carousel of images from a local folder. For security reasons, the folder must be
                                 explicitly exposed as an HTTP resource through the backend `resource_dirs` attribute. -->
                            <ImageCarousel class="col-6" img-dir="/mnt/hd/photos/carousel" />

                            <!-- Show the news headlines parsed from a list of RSS feed and stored locally through the
                                 `http.poll` backend -->
                            <RssNews class="col-6" db="sqlite:////path/to/your/rss.db" />
                        </Row>
                    </Dashboard>

            * The dashboard will be accessible under ``http://host:8008/dashboard/<name>``, where ``name=main`` if for
              example you stored your template under ``~/.config/platypush/dashboards/main.xml``.

        * To expose custom endpoints that can be called as web hooks by other applications and run some custom logic.
          All you have to do in this case is to create a hook on a
          :class:`platypush.message.event.http.hook.WebhookEvent` with the endpoint that you want to expose and store
          it under e.g. ``~/.config/platypush/scripts/hooks.py``:

            .. code-block:: python

                from platypush.context import get_plugin
                from platypush.event.hook import hook
                from platypush.message.event.http.hook import WebhookEvent

                hook_token = 'abcdefabcdef'

                # Expose the hook under the /hook/lights_toggle endpoint
                @hook(WebhookEvent, hook='lights_toggle')
                def lights_toggle(event, **context):
                    # Do any checks on the request
                    assert event.headers.get('X-Token') == hook_token, 'Unauthorized'

                    # Run some actions
                    lights = get_plugin('light.hue')
                    lights.toggle()

    Any plugin can register custom routes under ``platypush/backend/http/app/routes/plugins``.
    Any additional route is managed as a Flask blueprint template and the `.py`
    module can expose lists of routes to the main webapp through the
    ``__routes__`` object (a list of Flask blueprints).

    Security: Access to the endpoints requires at least one user to be registered. Access to the endpoints is regulated
    in the following ways (with the exception of event hooks, whose logic is up to the user):

        * **Simple authentication** - i.e. registered username and password.
        * **JWT token** provided either over as ``Authorization: Bearer`` header or ``GET`` ``?token=<TOKEN>``
          parameter. A JWT token can be generated either through the web panel or over the ``/auth`` endpoint.
        * **Global platform token**, usually configured on the root of the ``config.yaml`` as ``token: <VALUE>``.
          It can provided either over on the ``X-Token`` header or as a ``GET`` ``?token=<TOKEN>`` parameter.
        * **Session token**, generated upon login, it can be used to authenticate requests through the ``Cookie`` header
          (cookie name: ``session_token``).

    Requires:

        * **flask** (``pip install flask``)
        * **bcrypt** (``pip install bcrypt``)
        * **magic** (``pip install python-magic``), optional, for MIME type
            support if you want to enable media streaming
        * **gunicorn** (``pip install gunicorn``) - optional but recommended.

    By default the Platypush web server will run in a
    process spawned on the fly by the HTTP backend. However, being a
    Flask app, it will serve clients in a single thread and it won't
    support many features of a full-blown web server. gunicorn allows
    you to easily spawn the web server in a uWSGI wrapper, separate
    from the main Platypush daemon, and the uWSGI layer can be easily
    exposed over an nginx/lighttpd web server.

    Command to run the web server over a gunicorn uWSGI wrapper::

        gunicorn -w <n_workers> -b <bind_address>:8008 platypush.backend.http.uwsgi

    """

    _DEFAULT_HTTP_PORT = 8008
    _DEFAULT_WEBSOCKET_PORT = 8009

    def __init__(self, port=_DEFAULT_HTTP_PORT,
                 websocket_port=_DEFAULT_WEBSOCKET_PORT,
                 bind_address='0.0.0.0',
                 disable_websocket=False, resource_dirs=None,
                 ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None,
                 maps=None, run_externally=False, uwsgi_args=None, **kwargs):
        """
        :param port: Listen port for the web server (default: 8008)
        :type port: int

        :param websocket_port: Listen port for the websocket server (default: 8009)
        :type websocket_port: int

        :param bind_address: Address/interface to bind to (default: 0.0.0.0, accept connection from any IP)
        :type bind_address: str

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
        self.maps = maps or {}
        self.server_proc = None
        self.disable_websocket = disable_websocket
        self.websocket_thread = None
        self._websocket_loop = None
        self.bind_address = bind_address

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
                self.server_proc.wait(timeout=10)
                if self.server_proc.poll() is not None:
                    self.logger.info('HTTP server process may be still alive at termination')
                else:
                    self.logger.info('HTTP server process terminated')
            else:
                self.server_proc.terminate()
                self.server_proc.join(timeout=10)
                if self.server_proc.is_alive():
                    self.server_proc.kill()
                if self.server_proc.is_alive():
                    self.logger.info('HTTP server process may be still alive at termination')
                else:
                    self.logger.info('HTTP server process terminated')

        if self.websocket_thread and self.websocket_thread.is_alive() and self._websocket_loop:
            self._websocket_loop.stop()
            self.logger.info('HTTP websocket service terminated')

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
            except ConnectionClosed:
                self.logger.warning('Websocket client {} connection lost'.format(_ws.remote_address))
                self.active_websockets.remove(_ws)
                if _ws.remote_address in self._websocket_locks:
                    del self._websocket_locks[_ws.remote_address]

    def websocket(self):
        """ Websocket main server """
        set_thread_name('WebsocketServer')

        async def register_websocket(websocket, path):
            address = websocket.remote_address if websocket.remote_address \
                else '<unknown client>'

            self.logger.info('New websocket connection from {} on path {}'.format(address, path))
            self.active_websockets.add(websocket)

            try:
                await websocket.recv()
            except ConnectionClosed:
                self.logger.info('Websocket client {} closed connection'.format(address))
                self.active_websockets.remove(websocket)
                if address in self._websocket_locks:
                    del self._websocket_locks[address]

        websocket_args = {}
        if self.ssl_context:
            websocket_args['ssl'] = self.ssl_context

        self._websocket_loop = get_or_create_event_loop()
        self._websocket_loop.run_until_complete(
            websocket_serve(register_websocket, self.bind_address, self.websocket_port,
                             **websocket_args))
        self._websocket_loop.run_forever()

    def _start_web_server(self):
        def proc():
            self.logger.info('Starting local web server on port {}'.format(self.port))
            kwargs = {
                'host': self.bind_address,
                'port': self.port,
                'use_reloader': False,
                'debug': False,
            }

            application.config['redis_queue'] = self.bus.redis_queue
            if self.ssl_context:
                kwargs['ssl_context'] = self.ssl_context

            application.run(**kwargs)

        return proc

    def run(self):
        super().run()
        try:
            self.register_service(port=self.port)
        except Exception as e:
            self.logger.warning('Could not register the Zeroconf service')
            self.logger.exception(e)

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
