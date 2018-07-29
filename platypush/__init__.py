import argparse
import logging
import sys
import traceback

from threading import Thread

from .bus import Bus
from .config import Config
from .context import register_backends
from .cron.scheduler import CronScheduler
from .event.processor import EventProcessor
from .message.event import Event, StopEvent
from .message.request import Request
from .message.response import Response


__author__ = 'Fabio Manganiello <blacklight86@gmail.com>'
__version__ = '0.9'

#-----------#

logger = logging.getLogger(__name__)

class Daemon(object):
    """ Main class for the Platypush daemon """

    """ Configuration file (default: either ~/.config/platypush/config.yaml or
        /etc/platypush/config.yaml) """
    config_file = None

    """ Application bus. It's an internal queue where:
        - backends will post the messages they receive
        - plugins will post the responses they process """
    bus = None

    """ backend_name => backend_obj map """
    backends = None

    """ number of executions retries before a request fails """
    n_tries = 2

    def __init__(self, config_file=None, requests_to_process=None):
        """ Constructor
        Params:
            config_file -- Configuration file override (default: None)
            requests_to_process -- Exit after processing the specified number
                                   of requests (default: None, loop forever)
        """

        self.config_file = config_file
        self.event_processor = EventProcessor()
        self.requests_to_process = requests_to_process
        self.processed_requests = 0

        Config.init(self.config_file)
        logging.basicConfig(**Config.get('logging'))

    @classmethod
    def build_from_cmdline(cls, args):
        """ Build the app from command line arguments.
        Params:
            args -- Your sys.argv[1:] [List of strings]
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', '-c', dest='config', required=False,
                            default=None, help=cls.config_file.__doc__)

        opts, args = parser.parse_known_args(args)
        return cls(config_file=opts.config)

    def on_message(self):
        """ Default message handler """

        def _f(msg):
            """ on_message closure
            Params:
                msg -- platypush.message.Message instance """

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
            elif isinstance(msg, StopEvent) and msg.targets_me():
                logger.info('Received STOP event: {}'.format(msg))
                self.stop_app()
            elif isinstance(msg, Event):
                logger.info('Received event: {}'.format(msg))
                self.event_processor.process_event(msg)

        return _f


    def stop_app(self):
        """ Stops the backends and the bus """
        for backend in self.backends.values():
            backend.stop()
        self.bus.stop()


    def start(self):
        """ Start the daemon """
        self.bus = Bus(on_message=self.on_message())

        # Initialize the backends and link them to the bus
        self.backends = register_backends(bus=self.bus, global_scope=True)

        # Start the backend threads
        for backend in self.backends.values():
            backend.start()

        # Start the cron scheduler
        if Config.get_cronjobs():
            CronScheduler(jobs=Config.get_cronjobs()).start()

        # Poll for messages on the bus
        try:
            self.bus.poll()
        except KeyboardInterrupt as e:
            logger.info('SIGINT received, terminating application')
        finally:
            self.stop_app()


def main():
    print('Starting platypush v.{}'.format(__version__))
    app = Daemon.build_from_cmdline(sys.argv[1:])
    app.start()


# vim:sw=4:ts=4:et:

