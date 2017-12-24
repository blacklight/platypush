import argparse
import logging
import re
import sys

from platypush.bus import Bus
from platypush.config import Config
from platypush.context import register_backends
from platypush.message.request import Request


class Pusher(object):
    """
    Main class to send messages and events to a node
    """

    """ Configuration file path """
    config_file = None

    """ Default backend name """
    backend = None

    """ Pusher local bus. The response will be processed here """
    bus = None

    """ Configured backends as a name => object map """
    backends = {}

    """ Default response_wait timeout """
    default_response_wait_timeout = 5


    def __init__(self, config_file=None, backend=None, on_response=None):
        """
        Constructor.
        Params:
            config_file -- Path to the configuration file - default:
                           ~/.config/platypush/config.yaml or
                           /etc/platypush/config.yaml)
            backend     -- Name of the backend where pusher will send the
                           request and wait for the response (kafka
                           or pushbullet). Default: whatever is specified
                           with pusher=true in your configuration file
            on_response -- Method that will be invoked upon response receipt.
                           Takes a platypush.message.response.Response as arg.
                           Default: print the response and exit.
        """

        # Initialize the configuration
        self.config_file = config_file
        Config.init(config_file)
        logging.basicConfig(level=Config.get('logging'), stream=sys.stdout)

        self.on_response = on_response or self.default_on_response()
        self.backend = backend or Config.get_default_pusher_backend()
        self.bus = Bus()


    @classmethod
    def parse_build_args(cls, args):
        """ Parse the recognized options from a list of cmdline arguments """
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', '-c', dest='config', required=False,
                            default=None, help="Configuration file path (default: " +
                            "~/.config/platypush/config.yaml or " +
                            "/etc/platypush/config.yaml")

        parser.add_argument('--target', '-t', dest='target', required=True,
                            help="Destination of the command")

        parser.add_argument('--action', '-a', dest='action', required=True,
                            help="Action to execute, as package.method")

        parser.add_argument('--backend', '-b', dest='backend', required=False,
                            default=None, help="Backend to deliver the message " +
                            "[pushbullet|kafka] (default: whatever " +
                            "specified in your config with pusher=True)")

        parser.add_argument('--timeout', '-T', dest='timeout', required=False,
                            default=cls.default_response_wait_timeout, help="The application " +
                            "will wait for a response for this number of seconds " +
                            "(default: " + str(cls.default_response_wait_timeout) + " seconds. "
                            "A zero value means that the application " +
                            " will exit without waiting for a response)")

        opts, args = parser.parse_known_args(args)

        if len(args) % 2 != 0:
            raise RuntimeError('Odd number of key-value options passed: {}'.format(args))

        opts.args = {}
        for i in range(0, len(args), 2):
            opts.args[re.sub('^-+', '', args[i])] = args[i+1]

        return opts

    def get_backend(self, name):
        # Lazy init
        if not self.backends:
            self.backends = register_backends(bus=self.bus)

        if name not in self.backends:
            raise RuntimeError('No such backend configured: {}'.format(name))
        return self.backends[name]

    def default_on_response(self):
        def _f(response):
            logging.info('Received response: {}'.format(response))
            # self.backend_instance.stop()
        return _f

    def push(self, target, action, backend=None, config_file=None,
            timeout=default_response_wait_timeout, **kwargs):
        """
        Sends a message on a backend and optionally waits for an answer.
        Params:
            target  -- Target node
            action  -- Action to be executed in the form plugin.path.method
                    (e.g. shell.exec or music.mpd.play)
            backend -- Name of the backend that will process the request and get
                    the response (e.g. 'pushbullet' or 'kafka') (default: whichever
                    backend marked as pusher=true in your config.yaml)
            timeout -- Response receive timeout in seconds
                    - Pusher Default: 5 seconds
                    - If timeout == 0 or None: Pusher exits without waiting for a response
            config_file -- Path to the configuration file to be used (default:
                        ~/.config/platypush/config.yaml or
                        /etc/platypush/config.yaml)
            **kwargs    -- Optional key-valued arguments for the action method
                        (e.g. cmd='echo ping' or groups="['Living Room']")
        """

        def _timeout_hndl(signum, frame):
            """ Default response timeout handle: raise RuntimeError and exit """

        if not backend: backend = self.backend

        req = Request.build({
            'target' : target,
            'action' : action,
            'args'   : kwargs,
        })

        self.backend_instance = self.get_backend(backend)
        self.backend_instance.send_request(req, on_response=self.on_response,
                                           response_timeout=timeout)


def main(args=sys.argv[1:]):
    opts = Pusher.parse_build_args(args)

    pusher = Pusher(config_file=opts.config, backend=opts.backend)

    pusher.push(opts.target, action=opts.action, timeout=opts.timeout,
                **opts.args)


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:

