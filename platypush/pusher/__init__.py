import argparse
import os
import re
import signal
import sys

from platypush.bus import Bus
from platypush.config import Config
from platypush.message.request import Request
from platypush.message.response import Response
from platypush.utils import init_backends

def print_usage():
    print ('''Usage: {} [-h|--help] <-t|--target <target name>> <-a|--action <action name>> payload
    -h, --help:\t\tShow this help and exit
    -c, --config:\tPath to the platypush config.yaml (default: ~/.config/platypush/config.yaml or /etc/platypush/config.yaml)
    -b, --backend:\tBackend to deliver the message [pushbullet|kafka] (default: whatever specified in your config with pusher=True)
    -t, --target:\tName of the target device/host
    -T, --timeout:\tThe application will wait for a response for this number of seconds (default: 5 seconds. A zero value means that the application will exit without waiting for a response)
    -a, --action\tAction to run, it includes both the package name and the method (e.g. shell.exec or music.mpd.play)
    payload:\t\tArguments to the action
'''.format(sys.argv[0]))


_DEFAULT_TIMEOUT_SEC=5

def pusher(target, action, backend=None, config=None,
           timeout=_DEFAULT_TIMEOUT_SEC, **kwargs):
    def on_timeout(signum, frame):
        raise RuntimeError('Response timed out after {} seconds'.format(
            timeout))

    Config.init(config)

    if target == 'localhost':
        backend = 'local'
    elif not backend:
        backend = Config.get_default_pusher_backend()

    req = Request.build({
        'target' : target,
        'action' : action,
        'args'   : kwargs,
    })

    bus = Bus()
    backends = init_backends(bus=bus)
    if backend not in backends:
        raise RuntimeError('No such backend configured: {}'.format(backend))

    b = backends[backend]
    b.start()
    b.send_request(req)

    if timeout:
        signal.signal(signal.SIGALRM, on_timeout)
        signal.alarm(timeout)

        response_received = False
        while not response_received:
            msg = bus.get()
            response_received = isinstance(msg, Response) and (
                hasattr(msg, 'id') and msg.id == req.id)

        signal.alarm(0)
        print('Response received!')

    os._exit(0)


def main():
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
                        "[pushbullet|kafka|local] (default: whatever " +
                        "specified in your config with pusher=True)")

    parser.add_argument('--timeout', '-T', dest='timeout', required=False,
                        default=_DEFAULT_TIMEOUT_SEC, help="The application " +
                        "will wait for a response for this number of seconds " +
                        "(default: " + str(_DEFAULT_TIMEOUT_SEC) + " seconds. "
                        "A zero value means that the application " +
                        " will exit without waiting for a response)")

    opts, args = parser.parse_known_args(sys.argv[1:])

    if len(args) % 2 != 0:
        raise RuntimeError('Odd number of key-value options passed: {}'.
                           format(args))

    payload = {}
    for i in range(0, len(args), 2):
        payload[re.sub('^-+', '', args[i])] = args[i+1]

    pusher(target=opts.target, action=opts.action,
           backend=opts.backend, config=opts.config, timeout=opts.timeout,
           **payload)


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:

