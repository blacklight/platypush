import os
import pathlib
import secrets
import threading

from multiprocessing import Process, cpu_count

try:
    from websockets.exceptions import ConnectionClosed  # type: ignore
    from websockets import serve as websocket_serve  # type: ignore
except ImportError:
    from websockets import ConnectionClosed, serve as websocket_serve  # type: ignore

from platypush.backend import Backend
from platypush.backend.http.app import application
from platypush.backend.http.wsgi import WSGIApplicationWrapper
from platypush.bus.redis import RedisBus
from platypush.config import Config
from platypush.context import get_or_create_event_loop
from platypush.utils import get_ssl_server_context


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

                            <!-- Show current date, time and weather.
                                 It requires a `weather` plugin or backend enabled -->
                            <DateTimeWeather class="col-3" />
                        </Row>

                        <!-- Display the following widgets on a second row -->
                        <Row>
                            <!-- Show a carousel of images from a local folder. For security reasons, the folder must be
                                 explicitly exposed as an HTTP resource through the backend
                                 `resource_dirs` attribute. -->
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

    """

    _DEFAULT_HTTP_PORT = 8008
    _DEFAULT_WEBSOCKET_PORT = 8009

    def __init__(
        self,
        port=_DEFAULT_HTTP_PORT,
        websocket_port=_DEFAULT_WEBSOCKET_PORT,
        bind_address='0.0.0.0',
        disable_websocket=False,
        resource_dirs=None,
        ssl_cert=None,
        ssl_key=None,
        ssl_cafile=None,
        ssl_capath=None,
        maps=None,
        secret_key_file=None,
        **kwargs,
    ):
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

        :param secret_key_file: Path to the file containing the secret key that will be used by Flask
            (default: ``~/.local/share/platypush/flask.secret.key``).
        :type secret_key_file: str
        """

        super().__init__(**kwargs)

        self.port = port
        self.websocket_port = websocket_port
        self.maps = maps or {}
        self.server_proc = None
        self.disable_websocket = disable_websocket
        self.websocket_thread = None
        self._websocket_loop = None
        self._service_registry_thread = None
        self.bind_address = bind_address

        if resource_dirs:
            self.resource_dirs = {
                name: os.path.abspath(os.path.expanduser(d))
                for name, d in resource_dirs.items()
            }
        else:
            self.resource_dirs = {}

        self.active_websockets = set()
        self.ssl_context = (
            get_ssl_server_context(
                ssl_cert=ssl_cert,
                ssl_key=ssl_key,
                ssl_cafile=ssl_cafile,
                ssl_capath=ssl_capath,
            )
            if ssl_cert
            else None
        )

        self._workdir: str = Config.get('workdir')  # type: ignore
        assert self._workdir, 'The workdir is not set'

        self.secret_key_file = os.path.expanduser(
            secret_key_file
            or os.path.join(self._workdir, 'flask.secret.key')  # type: ignore
        )
        protocol = 'https' if ssl_cert else 'http'
        self.local_base_url = f'{protocol}://localhost:{self.port}'
        self._websocket_lock_timeout = 10
        self._websocket_lock = threading.RLock()
        self._websocket_locks = {}

    def send_message(self, *_, **__):
        self.logger.warning('Use cURL or any HTTP client to query the HTTP backend')

    def on_stop(self):
        """On backend stop"""
        super().on_stop()
        self.logger.info('Received STOP event on HttpBackend')

        if self.server_proc:
            self.server_proc.terminate()
            self.server_proc.join(timeout=10)
            if self.server_proc.is_alive():
                self.server_proc.kill()
            if self.server_proc.is_alive():
                self.logger.info(
                    'HTTP server process may be still alive at termination'
                )
            else:
                self.logger.info('HTTP server process terminated')

        if (
            self.websocket_thread
            and self.websocket_thread.is_alive()
            and self._websocket_loop
        ):
            self._websocket_loop.stop()
            self.logger.info('HTTP websocket service terminated')

        if self._service_registry_thread and self._service_registry_thread.is_alive():
            self._service_registry_thread.join(timeout=5)
            self._service_registry_thread = None

    def _acquire_websocket_lock(self, ws):
        try:
            acquire_ok = self._websocket_lock.acquire(
                timeout=self._websocket_lock_timeout
            )
            if not acquire_ok:
                raise TimeoutError('Websocket lock acquire timeout')

            addr = ws.remote_address
            if addr not in self._websocket_locks:
                self._websocket_locks[addr] = threading.RLock()
        finally:
            self._websocket_lock.release()

        acquire_ok = self._websocket_locks[addr].acquire(
            timeout=self._websocket_lock_timeout
        )
        if not acquire_ok:
            raise TimeoutError(f'Websocket on address {addr} not ready to receive data')

    def _release_websocket_lock(self, ws):
        try:
            acquire_ok = self._websocket_lock.acquire(
                timeout=self._websocket_lock_timeout
            )
            if not acquire_ok:
                raise TimeoutError('Websocket lock acquire timeout')

            addr = ws.remote_address
            if addr in self._websocket_locks:
                self._websocket_locks[addr].release()
        except Exception as e:
            self.logger.warning(
                'Unhandled exception while releasing websocket lock: %s', e
            )
        finally:
            self._websocket_lock.release()

    def notify_web_clients(self, event):
        """Notify all the connected web clients (over websocket) of a new event"""

        async def send_event(ws):
            try:
                self._acquire_websocket_lock(ws)
                await ws.send(str(event))
            except Exception as e:
                self.logger.warning('Error on websocket send_event: %s', e)
            finally:
                self._release_websocket_lock(ws)

        loop = get_or_create_event_loop()
        wss = self.active_websockets.copy()

        for _ws in wss:
            try:
                loop.run_until_complete(send_event(_ws))
            except ConnectionClosed:
                self.logger.warning(
                    'Websocket client %s connection lost', _ws.remote_address
                )
                self.active_websockets.remove(_ws)
                if _ws.remote_address in self._websocket_locks:
                    del self._websocket_locks[_ws.remote_address]

    def websocket(self):
        """Websocket main server"""

        async def register_websocket(websocket, path):
            address = (
                websocket.remote_address
                if websocket.remote_address
                else '<unknown client>'
            )

            self.logger.info(
                'New websocket connection from %s on path %s', address, path
            )
            self.active_websockets.add(websocket)

            try:
                await websocket.recv()
            except ConnectionClosed:
                self.logger.info('Websocket client %s closed connection', address)
                self.active_websockets.remove(websocket)
                if address in self._websocket_locks:
                    del self._websocket_locks[address]

        websocket_args = {}
        if self.ssl_context:
            websocket_args['ssl'] = self.ssl_context

        self._websocket_loop = get_or_create_event_loop()
        self._websocket_loop.run_until_complete(
            websocket_serve(
                register_websocket,
                self.bind_address,
                self.websocket_port,
                **websocket_args,
            )
        )
        self._websocket_loop.run_forever()

    def _get_secret_key(self, _create=False):
        if _create:
            self.logger.info('Creating web server secret key')
            pathlib.Path(self.secret_key_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.secret_key_file, 'w') as f:
                f.write(secrets.token_urlsafe(32))

            os.chmod(self.secret_key_file, 0o600)
            return secrets.token_urlsafe(32)

        try:
            with open(self.secret_key_file, 'r') as f:
                return f.read()
        except IOError as e:
            if not _create:
                return self._get_secret_key(_create=True)

            raise e

    def _web_server_proc(self):
        def proc():
            self.logger.info('Starting local web server on port %s', self.port)
            assert isinstance(
                self.bus, RedisBus
            ), 'The HTTP backend only works if backed by a Redis bus'

            application.config['redis_queue'] = self.bus.redis_queue
            application.secret_key = self._get_secret_key()
            kwargs = {
                'bind': f'{self.bind_address}:{self.port}',
                'workers': (cpu_count() * 2) + 1,
            }

            WSGIApplicationWrapper(f'{__package__}.app:application', kwargs).run()

        return proc

    def _register_service(self):
        try:
            self.register_service(port=self.port)
        except Exception as e:
            self.logger.warning('Could not register the Zeroconf service')
            self.logger.exception(e)

    def _start_websocket_server(self):
        if not self.disable_websocket:
            self.logger.info('Initializing websocket interface')
            self.websocket_thread = threading.Thread(
                target=self.websocket,
                name='WebsocketServer',
            )
            self.websocket_thread.start()

    def _start_zeroconf_service(self):
        self._service_registry_thread = threading.Thread(
            target=self._register_service,
            name='ZeroconfService',
        )
        self._service_registry_thread.start()

    def _run_web_server(self):
        self.server_proc = Process(target=self._web_server_proc(), name='WebServer')
        self.server_proc.start()
        self.server_proc.join()

    def run(self):
        super().run()

        self._start_websocket_server()
        self._start_zeroconf_service()
        self._run_web_server()


# vim:sw=4:ts=4:et:
