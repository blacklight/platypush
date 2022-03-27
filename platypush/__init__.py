"""
Platypush

.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
.. license: MIT
"""

import argparse
import logging
import os
import sys

from .bus.redis import RedisBus
from .config import Config
from .context import register_backends, register_plugins
from .cron.scheduler import CronScheduler
from .event.processor import EventProcessor
from .logger import Logger
from .message.event import Event
from .message.event.application import ApplicationStartedEvent
from .message.request import Request
from .message.response import Response
from .utils import set_thread_name, get_enabled_plugins

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'
__version__ = '0.23.2'

logger = logging.getLogger('platypush')


class Daemon:
    """ Main class for the Platypush daemon """

    # Configuration file (default: either ~/.config/platypush/config.yaml or
    # /etc/platypush/config.yaml
    config_file = None

    # Application bus. It's an internal queue where:
    # - backends will post the messages they receive
    # - plugins will post the responses they process
    bus = None

    # Default bus queue name
    _default_redis_queue = 'platypush/bus'

    pidfile = None

    # backend_name => backend_obj map
    backends = None

    # number of executions retries before a request fails
    n_tries = 2

    def __init__(self, config_file=None, pidfile=None, requests_to_process=None,
                 no_capture_stdout=False, no_capture_stderr=False, redis_queue=None):
        """
        Constructor
        Params:
            config_file -- Configuration file override (default: None)
            pidfile -- File where platypush will store its PID upon launch,
                       useful if you're planning to integrate the application
                       within a service or a launcher script (default: None)
            requests_to_process -- Exit after processing the specified number
                                   of requests (default: None, loop forever)
            no_capture_stdout -- Set to true if you want to disable the stdout
                                 capture by the logging system
            no_capture_stderr -- Set to true if you want to disable the stderr
                                 capture by the logging system
            redis_queue -- Name of the (Redis) queue used for dispatching messages (default: platypush/bus).
        """

        if pidfile:
            self.pidfile = pidfile
            with open(self.pidfile, 'w') as f:
                f.write(str(os.getpid()))

        self.redis_queue = redis_queue or self._default_redis_queue
        self.config_file = config_file
        Config.init(self.config_file)
        logging.basicConfig(**Config.get('logging'))

        redis_conf = Config.get('backend.redis') or {}
        self.bus = RedisBus(redis_queue=self.redis_queue, on_message=self.on_message(),
                            **redis_conf.get('redis_args', {}))

        self.no_capture_stdout = no_capture_stdout
        self.no_capture_stderr = no_capture_stderr
        self.event_processor = EventProcessor()
        self.requests_to_process = requests_to_process
        self.processed_requests = 0
        self.cron_scheduler = None

    @classmethod
    def build_from_cmdline(cls, args):
        """
        Build the app from command line arguments.
        Params:
            args -- Your sys.argv[1:] [List of strings]
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', '-c', dest='config', required=False,
                            default=None, help=cls.config_file.__doc__)
        parser.add_argument('--pidfile', '-P', dest='pidfile', required=False,
                            default=None, help="File where platypush will " +
                            "store its PID, useful if you're planning to " +
                            "integrate it in a service")
        parser.add_argument('--no-capture-stdout', dest='no_capture_stdout',
                            required=False, action='store_true',
                            help="Set this flag if you have max stack depth " +
                            "exceeded errors so stdout won't be captured by " +
                            "the logging system")
        parser.add_argument('--no-capture-stderr', dest='no_capture_stderr',
                            required=False, action='store_true',
                            help="Set this flag if you have max stack depth " +
                            "exceeded errors so stderr won't be captured by " +
                            "the logging system")
        parser.add_argument('--redis-queue', dest='redis_queue',
                            required=False, action='store_true',
                            default=cls._default_redis_queue,
                            help="Name of the Redis queue to be used to internally deliver messages "
                                 "(default: platypush/bus)")

        opts, args = parser.parse_known_args(args)
        return cls(config_file=opts.config, pidfile=opts.pidfile,
                   no_capture_stdout=opts.no_capture_stdout,
                   no_capture_stderr=opts.no_capture_stderr,
                   redis_queue=opts.redis_queue)

    def on_message(self):
        """
        Default message handler
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
                    logger.info('Dropped unauthorized request: {}'.format(msg))

                self.processed_requests += 1
                if self.requests_to_process \
                        and self.processed_requests >= self.requests_to_process:
                    self.stop_app()
            elif isinstance(msg, Response):
                logger.info('Received response: {}'.format(msg))
            elif isinstance(msg, Event):
                if not msg.disable_logging:
                    logger.info('Received event: {}'.format(msg))
                self.event_processor.process_event(msg)

        return _f

    def stop_app(self):
        """ Stops the backends and the bus """
        from .plugins import RunnablePlugin

        for backend in self.backends.values():
            backend.stop()

        for plugin in get_enabled_plugins().values():
            if isinstance(plugin, RunnablePlugin):
                plugin.stop()

        self.bus.stop()
        if self.cron_scheduler:
            self.cron_scheduler.stop()

    def run(self):
        """ Start the daemon """
        if not self.no_capture_stdout:
            sys.stdout = Logger(logger.info)
        if not self.no_capture_stderr:
            sys.stderr = Logger(logger.warning)

        set_thread_name('platypush')
        logger.info('---- Starting platypush v.{}'.format(__version__))

        # Initialize the backends and link them to the bus
        self.backends = register_backends(bus=self.bus, global_scope=True)

        # Start the backend threads
        for backend in self.backends.values():
            backend.start()

        # Initialize the plugins
        register_plugins(bus=self.bus)

        # Start the cron scheduler
        if Config.get_cronjobs():
            self.cron_scheduler = CronScheduler(jobs=Config.get_cronjobs())
            self.cron_scheduler.start()

        self.bus.post(ApplicationStartedEvent())

        # Poll for messages on the bus
        try:
            self.bus.poll()
        except KeyboardInterrupt:
            logger.info('SIGINT received, terminating application')
        finally:
            self.stop_app()


def main():
    """
    Platypush daemon main
    """
    app = Daemon.build_from_cmdline(sys.argv[1:])
    app.run()


# vim:sw=4:ts=4:et:
