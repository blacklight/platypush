import argparse
import logging
import sys
import traceback

from threading import Thread

from .bus import Bus
from .config import Config
from .utils import get_or_load_plugin, init_backends, get_module_and_name_from_action
from .message.request import Request
from .message.response import Response

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'
__version__ = '0.5'

#-----------#

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
        self.requests_to_process = requests_to_process
        self.processed_requests = 0

        Config.init(self.config_file)
        logging.basicConfig(level=Config.get('logging'), stream=sys.stdout)

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
                logging.info('Processing request: {}'.format(msg))
                msg.execute(n_tries=self.n_tries)

                self.processed_requests += 1
                if self.requests_to_process \
                        and self.processed_requests >= self.requests_to_process:
                    self.stop_app()
            elif isinstance(msg, Response):
                logging.info('Received response: {}'.format(msg))

        return _f


    def stop_app(self):
        for backend in self.backends.values():
            backend.stop()
        self.bus.stop()


    def start(self):
        """ Start the daemon """
        self.bus = Bus(on_message=self.on_message())

        # Initialize the backends and link them to the bus
        self.backends = init_backends(bus=self.bus)

        # Start the backend threads
        for backend in self.backends.values():
            backend.start()

        # Poll for messages on the bus
        try:
            self.bus.poll()
        except KeyboardInterrupt as e:
            logging.info('SIGINT received, terminating application')
        finally:
            self.stop_app()


def main(args=sys.argv[1:]):
    print('Starting platypush v.{}'.format(__version__))
    app = Daemon.build_from_cmdline(args)
    app.start()

if __name__ == '__main__':
    main()

# vim:sw=4:ts=4:et:

