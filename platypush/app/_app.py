from contextlib import contextmanager
import logging
import pathlib
import os
import signal
import subprocess
import sys
from textwrap import dedent
from typing import Optional, Sequence

from platypush.bus import Bus
from platypush.bus.redis import RedisBus
from platypush.cli import parse_cmdline
from platypush.commands import CommandStream
from platypush.config import Config
from platypush.context import register_backends, register_plugins
from platypush.cron.scheduler import CronScheduler
from platypush.entities import init_entities_engine, EntitiesEngine
from platypush.event.processor import EventProcessor
from platypush.logger import Logger
from platypush.message.event import Event
from platypush.message.request import Request
from platypush.message.response import Response
from platypush.utils import get_enabled_plugins, get_redis_conf

log = logging.getLogger('platypush')


class Application:
    """Main class for the Platypush application."""

    # Default Redis port
    _default_redis_port = 6379

    # Default Redis binary, if --start-redis is set
    _default_redis_bin = 'redis-server'

    # backend_name => backend_obj map
    backends = None

    # number of executions retries before a request fails
    n_tries = 2

    def __init__(
        self,
        config_file: Optional[str] = None,
        workdir: Optional[str] = None,
        db: Optional[str] = None,
        logsdir: Optional[str] = None,
        cachedir: Optional[str] = None,
        device_id: Optional[str] = None,
        pidfile: Optional[str] = None,
        requests_to_process: Optional[int] = None,
        no_capture_stdout: bool = False,
        no_capture_stderr: bool = False,
        redis_queue: Optional[str] = None,
        verbose: bool = False,
        start_redis: bool = False,
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
        redis_bin: Optional[str] = None,
        ctrl_sock: Optional[str] = None,
    ):
        """
        :param config_file: Configuration file. The order of precedence is:

            - The ``config_file`` parameter (or the ``-c``/``--config`` command
              line argument).
            - The ``PLATYPUSH_CONFIG`` environment variable.
            - ``./config.yaml``
            - ``~/.config/platypush/config.yaml``
            - ``/etc/platypush/config.yaml``

        :param workdir: Working directory where the application will store its
            data and integration plugins will store their data. The order of
            precedence is:

                - The ``workdir`` parameter (or the ``-w``/``--workdir`` command
                  line argument).
                - The ``PLATYPUSH_WORKDIR`` environment variable.
                - The ``workdir`` field in the configuration file.
                - ``~/.local/share/platypush``

        :param db: Main database engine for the application. Supports SQLAlchemy
            engine strings. The order of precedence is:

                - The ``db`` parameter (or the ``--main-db``/``--db`` command
                  line argument).
                - The ``PLATYPUSH_DB`` environment variable.
                - The ``db`` field in the configuration file.
                - ``sqlite:///<workdir>/main.db``

        :param logsdir: Logs directory where the application will store its logs.
            The order of precedence is:

                - The ``logsdir`` parameter (or the ``-l``/``--logsdir`` command
                  line argument).
                - The ``PLATYPUSH_LOGSDIR`` environment variable.
                - The ``logging`` -> ``filename`` field in the configuration
                  file (the ``format`` and ``level`` fields can be set as well
                  using Python logging configuration).
                - stdout and stderr

        :param cachedir: Directory where the application and the plugins will store
            their cache data. The order of precedence is:

                - The ``cachedir`` parameter (or the ``--cachedir`` command line
                  argument).
                - The ``PLATYPUSH_CACHEDIR`` environment variable.
                - The ``cachedir`` field in the configuration file.
                - ``~/.cache/platypush``

        :param device_id: Device ID used to identify this instance. The order
            of precedence is:

              - The ``device_id`` parameter (or the ``--device-id`` command
                line argument).
              - The ``PLATYPUSH_DEVICE_ID`` environment variable.
              - The ``device_id`` field in the configuration file.
              - The hostname of the machine.

        :param pidfile: File where platypush will store its PID upon launch,
           useful if you're planning to integrate the application within a
           service or a launcher script. Order of precedence:

               - The ``pidfile`` parameter (or the ``-P``/``--pidfile`` command
                 line argument).
               - The ``PLATYPUSH_PIDFILE`` environment variable.
               - No PID file.

        :param requests_to_process: Exit after processing the specified
            number of requests (default: None, loop forever). This is usually
            useful for testing purposes.
        :param no_capture_stdout: Set to true if you want to disable the
            stdout capture by the logging system (default: False).
        :param no_capture_stderr: Set to true if you want to disable the
            stderr capture by the logging system (default: False).
        :param redis_queue: Name of the (Redis) queue used for dispatching
            messages. Order of precedence:

                - The ``redis_queue`` parameter (or the ``--redis-queue`` command
                  line argument).
                - The ``PLATYPUSH_REDIS_QUEUE`` environment variable.
                - ``platypush/bus``

        :param verbose: Enable debug/verbose logging, overriding the stored
            configuration (default: False).
        :param start_redis: If set, it starts a managed Redis instance upon
            boot (it requires Redis installed on the server, see
            ``redis_bin``). This is particularly useful when running the
            application inside of Docker containers, without relying on
            ``docker-compose`` to start multiple containers, and in tests
            (default: False).
        :param redis_host: Host of the Redis server to be used. The order of
            precedence is:

                - The ``redis_host`` parameter (or the ``--redis-host`` command
                  line argument).
                - The ``PLATYPUSH_REDIS_HOST`` environment variable.
                - The ``redis`` -> ``host`` field in the configuration file.
                - The ``backend.redis`` -> ``redis_args`` -> ``host`` field in
                  the configuration file.
                - ``localhost``

        :param redis_port: Port of the Redis server to be used. The order of
            precedence is:

                - The ``redis_port`` parameter (or the ``--redis-port`` command
                  line argument).
                - The ``PLATYPUSH_REDIS_PORT`` environment variable.
                - The ``redis`` -> ``port`` field in the configuration file.
                - The ``backend.redis`` -> ``redis_args`` -> ``port`` field in
                  the configuration file.
                - ``6379``

        :param redis_bin: Path to the Redis server executable, if ``start_redis``
            is set. Alternative drop-in Redis implementations such as
            ``keydb-server``, ``valkey``, ``redict`` can be used. The order of
            precedence is:

                - The ``redis_bin`` parameter (or the ``--redis-bin`` command
                  line argument).
                - The ``PLATYPUSH_REDIS_BIN`` environment variable.
                - ``redis-server``

        :param ctrl_sock: If set, it identifies a path to a UNIX domain socket
            that the application can use to send control messages (e.g. STOP
            and RESTART) to its parent.
        """

        self.pidfile = pidfile or os.environ.get('PLATYPUSH_PIDFILE')
        self.bus: Optional[Bus] = None
        self.redis_queue = (
            redis_queue
            or os.environ.get('PLATYPUSH_REDIS_QUEUE')
            or RedisBus.DEFAULT_REDIS_QUEUE
        )

        os.environ['PLATYPUSH_REDIS_QUEUE'] = self.redis_queue
        self.config_file = config_file or os.environ.get('PLATYPUSH_CONFIG')
        self.verbose = verbose
        self.db_engine = db or os.environ.get('PLATYPUSH_DB')
        self.device_id = device_id or os.environ.get('PLATYPUSH_DEVICE_ID')

        self.logsdir = self.expand_path(logsdir or os.environ.get('PLATYPUSH_LOGSDIR'))
        self.workdir = self.expand_path(workdir or os.environ.get('PLATYPUSH_WORKDIR'))
        self.cachedir = self.expand_path(
            cachedir or os.environ.get('PLATYPUSH_CACHEDIR')
        )
        Config.init(
            self.config_file,
            device_id=self.device_id,
            workdir=self.workdir,
            db=self.db_engine,
            cachedir=self.cachedir,
            ctrl_sock=self.expand_path(ctrl_sock),
        )

        self.no_capture_stdout = no_capture_stdout
        self.no_capture_stderr = no_capture_stderr
        self.event_processor = EventProcessor()
        self.entities_engine: Optional[EntitiesEngine] = None
        self.requests_to_process = requests_to_process
        self.processed_requests = 0
        self.cron_scheduler = None
        self.start_redis = start_redis
        self.redis_host = redis_host or os.environ.get('PLATYPUSH_REDIS_HOST')
        self.redis_port = redis_port or os.environ.get('PLATYPUSH_REDIS_PORT')
        self.redis_bin = (
            redis_bin
            or os.environ.get('PLATYPUSH_REDIS_BIN')
            or self._default_redis_bin
        )
        self._redis_conf = {
            'host': self.redis_host or 'localhost',
            'port': self.redis_port or self._default_redis_port,
        }

        self._redis_proc: Optional[subprocess.Popen] = None
        self.cmd_stream = CommandStream(ctrl_sock)

        self._init_bus()
        self._init_logging()

    @staticmethod
    def expand_path(path: Optional[str]) -> Optional[str]:
        return os.path.abspath(os.path.expanduser(path)) if path else None

    def _init_bus(self):
        self._redis_conf = {**self._redis_conf, **get_redis_conf()}
        Config.set('redis', self._redis_conf)
        self.bus = RedisBus(
            redis_queue=self.redis_queue,
            on_message=self.on_message(),
            **self._redis_conf,
        )

    def _init_logging(self):
        logging_conf = Config.get('logging') or {}
        if self.verbose:
            logging_conf['level'] = logging.DEBUG

        if self.logsdir:
            logging_conf['filename'] = os.path.join(self.logsdir, 'platypush.log')
            logging_conf.pop('stream', None)

        if logging_conf.get('filename'):
            pathlib.Path(os.path.dirname(logging_conf['filename'])).mkdir(
                parents=True, exist_ok=True
            )

        Config.set('logging', logging_conf)
        logging.basicConfig(**logging_conf)

    def _start_redis(self):
        if self._redis_proc and self._redis_proc.poll() is None:
            log.warning(
                'A local Redis instance is already running, refusing to start it again'
            )
            return

        port = self._redis_conf['port']
        log.info('Starting local Redis instance on %s', port)
        redis_cmd_args = [
            self.redis_bin,
            '--bind',
            'localhost',
            '--port',
            str(port),
        ]

        try:
            self._redis_proc = subprocess.Popen(  # pylint: disable=consider-using-with
                redis_cmd_args,
                stdout=subprocess.PIPE,
            )
        except Exception as e:
            log.error(
                'Failed to start local Redis instance: "%s": %s',
                ' '.join(redis_cmd_args),
                e,
            )

            sys.exit(1)

        log.info('Waiting for Redis to start')
        for line in self._redis_proc.stdout:  # type: ignore
            if b'Ready to accept connections' in line:
                break

    def _stop_redis(self):
        if self._redis_proc and self._redis_proc.poll() is None:
            log.info('Stopping local Redis instance')
            self._redis_proc.kill()
            self._redis_proc = None

    @classmethod
    def from_cmdline(cls, args: Sequence[str]) -> "Application":
        """
        Build the app from command line arguments.
        """
        opts = parse_cmdline(args)
        return cls(
            config_file=opts.config,
            workdir=opts.workdir,
            cachedir=opts.cachedir,
            logsdir=opts.logsdir,
            db=opts.db_engine,
            device_id=opts.device_id,
            pidfile=opts.pidfile,
            no_capture_stdout=opts.no_capture_stdout,
            no_capture_stderr=opts.no_capture_stderr,
            redis_queue=opts.redis_queue,
            verbose=opts.verbose,
            start_redis=opts.start_redis,
            redis_host=opts.redis_host,
            redis_port=opts.redis_port,
            ctrl_sock=opts.ctrl_sock,
        )

    def on_message(self):
        """
        Default message handler.
        """

        def _f(msg):
            """
            on_message closure
            Params:
                msg -- platypush.message.Message instance
            """

            if isinstance(msg, Request):
                try:
                    msg.execute(n_tries=self.n_tries)
                except PermissionError:
                    log.info('Dropped unauthorized request: %s', msg)

                self.processed_requests += 1
                if (
                    self.requests_to_process
                    and self.processed_requests >= self.requests_to_process
                ):
                    self.stop()
            elif isinstance(msg, Response):
                msg.log()
            elif isinstance(msg, Event):
                msg.log()
                self.event_processor.process_event(msg)

        return _f

    def stop(self):
        """Stops the backends and the bus."""
        from platypush.plugins import RunnablePlugin

        log.info('Stopping the application')
        backends = (self.backends or {}).copy().values()
        runnable_plugins = [
            plugin
            for plugin in get_enabled_plugins().values()
            if isinstance(plugin, RunnablePlugin)
        ]

        for backend in backends:
            backend.stop()

        for plugin in runnable_plugins:
            # This is required because some plugins may redefine the `stop` method.
            # In that case, at the very least the _should_stop event should be
            # set to notify the plugin to stop.
            plugin._should_stop.set()  # pylint: disable=protected-access
            plugin.stop()

        for backend in backends:
            backend.wait_stop()

        for plugin in runnable_plugins:
            plugin.wait_stop()

        if self.entities_engine:
            self.entities_engine.stop()
            self.entities_engine.wait_stop()
            self.entities_engine = None

        if self.cron_scheduler:
            self.cron_scheduler.stop()
            self.cron_scheduler.wait_stop()
            self.cron_scheduler = None

        if self.bus:
            self.bus.stop()
            self.bus = None

        if self.start_redis:
            self._stop_redis()

        log.info('Exiting application')

    @contextmanager
    def _open_pidfile(self):
        if self.pidfile:
            try:
                with open(self.pidfile, 'w') as f:
                    f.write(str(os.getpid()))
            except OSError as e:
                log.warning('Failed to create PID file %s: %s', self.pidfile, e)

        yield

        if self.pidfile:
            try:
                os.remove(self.pidfile)
            except OSError as e:
                log.warning('Failed to remove PID file %s: %s', self.pidfile, e)

    def _run(self):
        from platypush import __version__

        if not self.no_capture_stdout:
            sys.stdout = Logger(log.info)
        if not self.no_capture_stderr:
            sys.stderr = Logger(log.warning)

        log.info(
            dedent(
                r'''
                  _____  _       _                         _
                 |  __ \| |     | |                       | |
                 | |__) | | __ _| |_ _   _ _ __  _   _ ___| |__
                 |  ___/| |/ _` | __| | | | '_ \| | | / __| '_ \
                 | |    | | (_| | |_| |_| | |_) | |_| \__ \ | | |
                 |_|    |_|\__,_|\__|\__, | .__/ \__,_|___/_| |_|
                                      __/ | |
                                     |___/|_|
                        '''
            )
        )
        log.info('---- Starting Platypush v.%s', __version__)

        # Start the local Redis service if required
        if self.start_redis:
            self._start_redis()

        # Initialize the backends and link them to the bus
        self.backends = register_backends(bus=self.bus, global_scope=True)

        # Start the backend threads
        for backend in self.backends.values():
            backend.start()

        # Initialize the plugins
        register_plugins(bus=self.bus)

        # Initialize the entities engine
        self.entities_engine = init_entities_engine()

        # Start the cron scheduler
        if Config.get_cronjobs():
            self.cron_scheduler = CronScheduler(jobs=Config.get_cronjobs())
            self.cron_scheduler.start()

        assert self.bus, 'The bus is not running'

        # Poll for messages on the bus
        try:
            self.bus.poll()
        except KeyboardInterrupt:
            log.info('SIGINT received, terminating application')
            # Ignore other SIGINT signals
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        finally:
            self.stop()

    def run(self):
        """Run the application."""

        with self._open_pidfile():
            self._run()


app: Optional[Application] = None


def main(*args: str):
    """
    Application entry point.
    """
    global app

    app = Application.from_cmdline(args)

    try:
        app.run()
    except KeyboardInterrupt:
        pass

    return 0


# vim:sw=4:ts=4:et:
