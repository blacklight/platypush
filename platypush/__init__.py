import logging
import sys
import traceback

from threading import Thread
from getopt import getopt

from .bus import Bus
from .config import Config
from .utils import get_or_load_plugin, init_backends
from .message.request import Request
from .message.response import Response

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'
__version__ = '0.3.3'

#-----------#

def _execute_request(request, retry=True):
    tokens = request.action.split('.')
    module_name = str.join('.', tokens[:-1])
    method_name = tokens[-1:][0]

    try:
        plugin = get_or_load_plugin(module_name)
    except RuntimeError as e:  # Module/class not found
        logging.exception(e)
        return

    try:
        response = plugin.run(method=method_name, **request.args)
        if response and response.is_error():
            logging.warn('Response processed with errors: {}'.format(response))
        else:
            logging.info('Processed response: {}'.format(response))
    except Exception as e:
        response = Response(output=None, errors=[str(e), traceback.format_exc()])
        logging.exception(e)
        if retry:
            logging.info('Reloading plugin {} and retrying'.format(module_name))
            get_or_load_plugin(module_name, reload=True)
            _execute_request(request, retry=False)
    finally:
        # Send the response on the backend that received the request
        if request.backend and request.origin:
            response.target = request.origin
            request.backend.send_response(response)


def on_msg(msg):
    if isinstance(msg, Request):
        logging.info('Processing request: {}'.format(msg))
        Thread(target=_execute_request, args=(msg,)).start()
    elif isinstance(msg, Response):
        logging.info('Received response: {}'.format(msg))


def main():
    print('Starting platypush v.{}'.format(__version__))
    config_file = None

    optlist, args = getopt(sys.argv[1:], 'vh')
    for opt, arg in optlist:
        if opt == '-c':
            config_file = arg
        elif opt == '-h':
            print('''
Usage: {} [-h] [-c <config_file>]
    -h  Show this help
    -c  Path to the configuration file (default: ./config.yaml)
'''.format(sys.argv[0]))
            return

    Config.init(config_file)
    logging.basicConfig(level=Config.get('logging'), stream=sys.stdout)

    bus = Bus(on_msg=on_msg)
    backends = init_backends(bus)

    for backend in backends.values():
        backend.start()

    bus.loop_forever()

if __name__ == '__main__':
    main()

# vim:sw=4:ts=4:et:

