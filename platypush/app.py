import logging
import os
import subprocess
import sys
from typing import Optional, Sequence

from .bus import Bus
from .bus.redis import RedisBus
from .cli import parse_cmdline
from .config import Config
from .context import register_backends, register_plugins
from .cron.scheduler import CronScheduler
from .entities import init_entities_engine, EntitiesEngine
from .event.processor import EventProcessor
from .logger import Logger
from .message.event import Event
from .message.event.application import ApplicationStartedEvent
from .message.request import Request
from .message.response import Response
from .utils import get_enabled_plugins, get_redis_conf

log = logging.getLogger('platypush')


class Application:
    """Main class for the Platypush application."""

    # Default Redis port
    _default_redis_port = 6379

    # backend_name => backend_obj map
    backends = None

    # number of executions retries before a request fails
    n_tries = 2

    def __init__(
        self,
        config_file: Optional[str] = None,
        workdir: Optional[str] = None,
        logsdir: Optional[str] = None,
        pidfile: Optional[str] = None,
        requests_to_process: Optional[int] = None,
        no_capture_stdout: bool = False,
        no_capture_stderr: bool = False,
        redis_queue: Optional[str] = None,
        verbose: bool = False,
        start_redis: bool = False,
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
    ):
        """
        :param config_file: Configuration file override (default: None).
        :param workdir: Overrides the ``workdir`` setting in the configuration
            file (default: None).
        :param logsdir: Set logging directory. If not specified, the
            ``filename`` setting under the ``logging`` section of the
            configuration file is used. If not set, logging will be sent to
            stdout and stderr.
        :param pidfile: File where platypush will store its PID upon launch,
           useful if you're planning to integrate the application within a
           service or a launcher script (default: None).
        :param requests_to_process: Exit after processing the specified
            number of requests (default: None, loop forever).
        :param no_capture_stdout: Set to true if you want to disable the
            stdout capture by the logging system (default: False).
        :param no_capture_stderr: Set to true if you want to disable the
            stderr capture by the logging system (default: False).
        :param redis_queue: Name of the (Redis) queue used for dispatching
            messages (default: platypush/bus).
        :param verbose: Enable debug/verbose logging, overriding the stored
            configuration (default: False).
        :param start_redis: If set, it starts a managed Redis instance upon
            boot (it requires the ``redis-server`` executable installed on the
            server). This is particularly useful when running the application
            inside of Docker containers, without relying on ``docker-compose``
            to start multiple containers, and in tests (default: False).
        :param redis_host: Host of the Redis server to be used. It overrides
            the settings in the ``redis`` section of the configuration file.
        :param redis_port: Port of the local Redis server. It overrides the
            settings in the ``redis`` section of the configuration file.
        """

        self.pidfile = pidfile
        if pidfile:
            with open(pidfile, 'w') as f:
                f.write(str(os.getpid()))

        self.bus: Optional[Bus] = None
        self.redis_queue = redis_queue or RedisBus.DEFAULT_REDIS_QUEUE
        self.config_file = config_file
        self._verbose = verbose
        self._logsdir = (
            os.path.abspath(os.path.expanduser(logsdir)) if logsdir else None
        )
        Config.init(self.config_file)

        if workdir:
            Config.set('workdir', os.path.abspath(os.path.expanduser(workdir)))

        self.no_capture_stdout = no_capture_stdout
        self.no_capture_stderr = no_capture_stderr
        self.event_processor = EventProcessor()
        self.entities_engine: Optional[EntitiesEngine] = None
        self.requests_to_process = requests_to_process
        self.processed_requests = 0
        self.cron_scheduler = None
        self.start_redis = start_redis
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_conf = {}
        self._redis_proc: Optional[subprocess.Popen] = None

        self._init_bus()
        self._init_logging()

    def _init_bus(self):
        self._redis_conf = get_redis_conf()
        self._redis_conf['port'] = self.redis_port or self._redis_conf.get(
            'port', self._default_redis_port
        )

        if self.redis_host:
            self._redis_conf['host'] = self.redis_host

        Config.set('redis', self._redis_conf)
        self.bus = RedisBus(
            redis_queue=self.redis_queue,
            on_message=self.on_message(),
            **self._redis_conf,
        )

    def _init_logging(self):
        logging_conf = Config.get('logging') or {}
        if self._verbose:
            logging_conf['level'] = logging.DEBUG
        if self._logsdir:
            logging_conf['filename'] = os.path.join(self._logsdir, 'platypush.log')
            logging_conf.pop('stream', None)

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
            'redis-server',
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
            logsdir=opts.logsdir,
            pidfile=opts.pidfile,
            no_capture_stdout=opts.no_capture_stdout,
            no_capture_stderr=opts.no_capture_stderr,
            redis_queue=opts.redis_queue,
            verbose=opts.verbose,
            start_redis=opts.start_redis,
            redis_host=opts.redis_host,
            redis_port=opts.redis_port,
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
        from .plugins import RunnablePlugin

        log.info('Stopping the application')

        if self.backends:
            for backend in self.backends.values():
                backend.stop()

        for plugin in get_enabled_plugins().values():
            if isinstance(plugin, RunnablePlugin):
                plugin.stop()

        if self.bus:
            self.bus.stop()
            self.bus = None

        if self.cron_scheduler:
            self.cron_scheduler.stop()
            self.cron_scheduler = None

        if self.entities_engine:
            self.entities_engine.stop()
            self.entities_engine = None

        if self.start_redis:
            self._stop_redis()

    def run(self):
        """Start the daemon."""
        from . import __version__

        if not self.no_capture_stdout:
            sys.stdout = Logger(log.info)
        if not self.no_capture_stderr:
            sys.stderr = Logger(log.warning)

        log.info('---- Starting platypush v.%s', __version__)

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
        self.bus.post(ApplicationStartedEvent())

        # Poll for messages on the bus
        try:
            self.bus.poll()
        except KeyboardInterrupt:
            log.info('SIGINT received, terminating application')
        finally:
            self.stop()


def main(*args: str):
    """
    Application entry point.
    """
    app = Application.from_cmdline(args)
    app.run()


# vim:sw=4:ts=4:et:
