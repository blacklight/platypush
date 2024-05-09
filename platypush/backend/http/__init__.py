import asyncio
import os
import pathlib
import secrets
import signal
import threading

from functools import partial
from multiprocessing import Process
from time import time
from typing import Mapping, Optional

import psutil

from tornado.httpserver import HTTPServer
from tornado.netutil import bind_sockets
from tornado.process import cpu_count, fork_processes
from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler

from platypush.backend import Backend
from platypush.backend.http.app import application
from platypush.backend.http.app.utils import get_streaming_routes, get_ws_routes
from platypush.backend.http.app.ws.events import WSEventProxy
from platypush.bus.redis import RedisBus
from platypush.config import Config
from platypush.utils import get_remaining_timeout


class HttpBackend(Backend):
    """
    The HTTP backend is a general-purpose web server.

    Example configuration:

      .. code-block:: yaml

        backend.http:
            # Default HTTP listen port
            port: 8008
            # External folders that will be exposed over `/resources/<name>`
            resource_dirs:
                photos: /mnt/hd/photos
                videos: /mnt/hd/videos
                music: /mnt/hd/music

    You can leverage this backend:

        * To execute Platypush commands via HTTP calls. In order to do so:

            * Register a user to Platypush through the web panel (usually
              served on ``http://host:8008/``).

            * Generate a token for your user, either through the web panel
              (Settings -> Generate Token) or via API:

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

        * To interact with your system (and control plugins and backends)
          through the Platypush web panel, by default available on
          ``http://host:8008/``. Any configured plugin that has an available
          panel plugin will be automatically added to the web panel.

        * To create asynchronous integrations with Platypush over websockets.
          Two routes are available:

            * ``/ws/events`` - Subscribe to this websocket to receive the
              events generated by the application.
            * ``/ws/requests`` - Subscribe to this websocket to send commands
              to Platypush and receive the response asynchronously.

          You will have to authenticate your connection to these websockets,
          just like the ``/execute`` endpoint. In both cases, you can pass the
          token either via ``Authorization: Bearer``, via the ``token`` query
          string or body parameter, or leverage ``Authorization: Basic`` with
          username and password (not advised), or use a valid ``session_token``
          cookie from an authenticated web panel session.

        * To display a fullscreen dashboard with custom widgets.

            * Widgets are available as Vue.js components under
              ``platypush/backend/http/webapp/src/components/widgets``.

            * Explore their options (some may require some plugins or backends
              to be configured in order to work) and create a new dashboard
              template under ``~/.config/platypush/dashboards``- e.g.
              ``main.xml``:

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

            * The dashboard will be accessible under
              ``http://host:8008/dashboard/<name>``, where ``name=main`` if for
              example you stored your template under
              ``~/.config/platypush/dashboards/main.xml``.

        * To expose custom endpoints that can be called as web hooks by other
          applications and run some custom logic. All you have to do in this case
          is to create a hook on a
          :class:`platypush.message.event.http.hook.WebhookEvent` with the
          endpoint that you want to expose and store it under e.g.
          ``~/.config/platypush/scripts/hooks.py``:

            .. code-block:: python

                from platypush import get_plugin, when
                from platypush.message.event.http.hook import WebhookEvent

                hook_token = 'abcdefabcdef'

                # Expose the hook under the /hook/lights_toggle endpoint
                @when(WebhookEvent, hook='lights_toggle')
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

    Security: Access to the endpoints requires at least one user to be
    registered. Access to the endpoints is regulated in the following ways
    (with the exception of event hooks, whose logic is up to the user):

        * **Simple authentication** - i.e. registered username and password.
        * **JWT token** provided either over as ``Authorization: Bearer``
          header or ``GET`` ``?token=<TOKEN>`` parameter. A JWT token can be
          generated either through the web panel or over the ``/auth``
          endpoint.
        * **Global platform token**, usually configured on the root of the
          ``config.yaml`` as ``token: <VALUE>``. It can provided either over on
          the ``X-Token`` header or as a ``GET`` ``?token=<TOKEN>`` parameter.
        * **Session token**, generated upon login, it can be used to
          authenticate requests through the ``Cookie`` header (cookie name:
          ``session_token``).

    """

    DEFAULT_HTTP_PORT = 8008
    """The default listen port for the webserver."""

    _STOP_TIMEOUT = 5
    """How long we should wait (in seconds) before killing the worker processes."""

    def __init__(
        self,
        port: int = DEFAULT_HTTP_PORT,
        bind_address: str = '0.0.0.0',
        resource_dirs: Optional[Mapping[str, str]] = None,
        secret_key_file: Optional[str] = None,
        num_workers: Optional[int] = None,
        use_werkzeug_server: bool = False,
        **kwargs,
    ):
        """
        :param port: Listen port for the web server (default: 8008)
        :param bind_address: Address/interface to bind to (default: 0.0.0.0, accept connection from any IP)
        :param resource_dirs: Static resources directories that will be
            accessible through ``/resources/<path>``. It is expressed as a map
            where the key is the relative path under ``/resources`` to expose and
            the value is the absolute path to expose.
        :param secret_key_file: Path to the file containing the secret key that will be used by Flask
            (default: ``~/.local/share/platypush/flask.secret.key``).
        :param num_workers: Number of worker processes to use (default: ``(cpu_count * 2) + 1``).
        :param use_werkzeug_server: Whether the backend should be served by a
            Werkzeug server (default: ``False``). Note that using the built-in
            Werkzeug server instead of Tornado is very inefficient, and it
            doesn't support websocket-based features either so the UI will
            probably be severely limited. You should only use this option if:

                - You are running tests.
                - You have issues with running a full Tornado server - for
                  example, you are running the application on a small embedded
                  device that doesn't support Tornado.
        """

        super().__init__(**kwargs)

        self.port = port
        self._server_proc: Optional[Process] = None
        self._service_registry_thread = None
        self.bind_address = bind_address

        if resource_dirs:
            self.resource_dirs = {
                name: os.path.abspath(os.path.expanduser(d))
                for name, d in resource_dirs.items()
            }
        else:
            self.resource_dirs = {}

        self.secret_key_file = os.path.expanduser(
            secret_key_file
            or os.path.join(Config.get('workdir'), 'flask.secret.key')  # type: ignore
        )
        self.local_base_url = f'http://localhost:{self.port}'
        self.num_workers = num_workers or (cpu_count() * 2) + 1
        self.use_werkzeug_server = use_werkzeug_server

    def send_message(self, *_, **__):
        self.logger.warning('Use cURL or any HTTP client to query the HTTP backend')

    def on_stop(self):
        """On backend stop"""
        super().on_stop()
        self.logger.info('Received STOP event on HttpBackend')
        start = time()
        remaining_time: partial[float] = partial(  # type: ignore
            get_remaining_timeout, timeout=self._STOP_TIMEOUT, start=start
        )

        if self._server_proc:
            if self._server_proc.pid:
                try:
                    os.kill(self._server_proc.pid, signal.SIGINT)
                except OSError:
                    pass

            if self._server_proc and self._server_proc.is_alive():
                self._server_proc.join(timeout=remaining_time() / 2)
                try:
                    self._server_proc.terminate()
                    self._server_proc.join(timeout=remaining_time() / 2)
                except AttributeError:
                    pass

        if self._server_proc and self._server_proc.is_alive():
            self._server_proc.kill()

        self._server_proc = None

        if self._service_registry_thread and self._service_registry_thread.is_alive():
            self._service_registry_thread.join(timeout=remaining_time())
            self._service_registry_thread = None

        self.logger.info('HTTP server terminated')

    def notify_web_clients(self, event):
        """Notify all the connected web clients (over websocket) of a new event"""
        WSEventProxy.publish(event)  # noqa: E1120

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

    def _register_service(self):
        try:
            self.register_service(port=self.port)
        except Exception as e:
            self.logger.warning('Could not register the Zeroconf service')
            self.logger.exception(e)

    def _start_zeroconf_service(self):
        self._service_registry_thread = threading.Thread(
            target=self._register_service,
            name='ZeroconfService',
        )
        self._service_registry_thread.start()

    async def _post_fork_main(self, sockets):
        assert isinstance(
            self.bus, RedisBus
        ), 'The HTTP backend only works if backed by a Redis bus'

        application.config['redis_queue'] = self.bus.redis_queue
        application.secret_key = self._get_secret_key()
        container = WSGIContainer(application)
        tornado_app = Application(
            [
                *[
                    (route.path(), route)
                    for route in [*get_ws_routes(), *get_streaming_routes()]
                ],
                (r'.*', FallbackHandler, {'fallback': container}),
            ]
        )

        server = HTTPServer(tornado_app)
        server.add_sockets(sockets)

        try:
            await asyncio.Event().wait()
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        finally:
            server.stop()
            await server.close_all_connections()

    def _web_server_proc(self):
        self.logger.info(
            'Starting local web server on port %s with %d service workers',
            self.port,
            self.num_workers,
        )

        if self.use_werkzeug_server:
            application.config['redis_queue'] = self.bus.redis_queue  # type: ignore
            application.run(
                host=self.bind_address,
                port=self.port,
                use_reloader=False,
                debug=True,
            )
        else:
            sockets = bind_sockets(
                self.port, address=self.bind_address, reuse_port=True
            )

            try:
                fork_processes(self.num_workers)
                future = self._post_fork_main(sockets)
                asyncio.run(future)
            except (asyncio.CancelledError, KeyboardInterrupt):
                pass
            finally:
                self._stop_workers()

    def _stop_workers(self):
        """
        Stop all the worker processes.

        We have to run this manually on server termination because of a
        long-standing issue with Tornado not being able to wind down the forked
        workers when the server terminates:
        https://github.com/tornadoweb/tornado/issues/1912.
        """
        parent_pid = (
            self._server_proc.pid
            if self._server_proc and self._server_proc.pid
            else None
        )

        if not parent_pid:
            return

        try:
            cur_proc = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return

        # Send a SIGTERM to all the children
        children = cur_proc.children()
        for child in children:
            if child.pid != parent_pid and child.is_running():
                try:
                    os.kill(child.pid, signal.SIGTERM)
                except OSError as e:
                    self.logger.warning(
                        'Could not send SIGTERM to PID %d: %s', child.pid, e
                    )

        # Initialize the timeout
        start = time()
        remaining_time: partial[int] = partial(  # type: ignore
            get_remaining_timeout, timeout=self._STOP_TIMEOUT, start=start, cls=int
        )

        # Wait for all children to terminate (with timeout)
        for child in children:
            if child.pid != parent_pid and child.is_running():
                try:
                    child.wait(timeout=remaining_time())
                except TimeoutError:
                    pass

        # Send a SIGKILL to any child process that is still running
        for child in children:
            if child.pid != parent_pid and child.is_running():
                try:
                    child.kill()
                except OSError:
                    pass

    def _start_web_server(self):
        self._server_proc = Process(target=self._web_server_proc)
        self._server_proc.start()
        self._server_proc.join()

    def run(self):
        super().run()

        self._start_zeroconf_service()
        self._start_web_server()


# vim:sw=4:ts=4:et:
