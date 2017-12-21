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
__version__ = '0.4'

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

    def __init__(self, config_file=None, message_handler=None):
        """ Constructor
        Params:
            config_file -- Configuration file override (default: None)
            message_handler -- Another function that will receive the messages.
                If set, Platypush will just act as a message proxy. Useful to
                embed into other projects, for tests, or for delegating events.
        """

        self.config_file = config_file
        self.message_handler = message_handler
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

            if self.message_handler:
                # Proxy the message
                self.message_handler(msg)
                return

            if isinstance(msg, Request):
                logging.info('Processing request: {}'.format(msg))
                Thread(target=self.run_request(), args=(msg,)).start()
            elif isinstance(msg, Response):
                logging.info('Received response: {}'.format(msg))

        return _f


    def run_request(self):
        """ Runs a request and returns the response """
        def _thread_func(request, n_tries=self.n_tries):
            """ Thread closure method
            Params:
                request - platypush.message.request.Request object """

            (module_name, method_name) = get_module_and_name_from_action(request.action)

            try:
                plugin = get_or_load_plugin(module_name)
            except RuntimeError as e:  # Module/class not found
                logging.exception(e)
                return

            try:
                # Run the action
                response = plugin.run(method=method_name, **request.args)
                if response and response.is_error():
                    raise RuntimeError('Response processed with errors: {}'.format(response))

                logging.info('Processed response from plugin {}: {}'.
                                format(plugin, response))
            except Exception as e:
                # Retry mechanism
                response = Response(output=None, errors=[str(e), traceback.format_exc()])
                logging.exception(e)
                if n_tries:
                    logging.info('Reloading plugin {} and retrying'.format(module_name))
                    get_or_load_plugin(module_name, reload=True)
                    _thread_func(request, n_tries=n_tries-1)
            finally:
                # Send the response on the backend
                if request.backend and request.origin:
                    request.backend.send_response(response=response, request=request)
                else:
                    logging.info('Dropping response whose request has no ' +
                                 'origin attached: {}'.format(request))

        return _thread_func

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

            for backend in self.backends.values():
                backend.stop()


def main(args=sys.argv[1:]):
    print('Starting platypush v.{}'.format(__version__))
    app = Daemon.build_from_cmdline(args)
    app.start()

if __name__ == '__main__':
    main()

# vim:sw=4:ts=4:et:

