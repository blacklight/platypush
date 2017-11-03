import json
import os
import sys
import yaml

from getopt import getopt
from pushbullet import Pushbullet

def get_config():
    curdir = os.path.dirname(os.path.realpath(__file__))
    config_file = curdir + os.sep + 'config.yaml'
    config = {}

    with open(config_file,'r') as f:
        config = yaml.load(f)

    return config

def print_usage():
    print ('''Usage: {} [-h|--help] <-t|--target <target name>> <-p|--plugin <plugin name>> payload
    -h, --help:\t\tShow this help and exit
    -t, --target:\tName of the target device/host
    -p, --plugin:\tPlugin to use (e.g. shell or music.mpd)
    payload:\t\tArguments to the plugin
'''.format(sys.argv[0]))

def main():
    config = get_config()
    API_KEY = config['pushbullet']['token']
    pb = Pushbullet(API_KEY)

    devices = [
        _ for _ in pb.devices if _.nickname == config['pushbullet']['device']
    ]

    if len(devices) > 0:
        device = devices[0]
    else:
        print('Device {} not found - please create a virtual device on ' +
              'your PushBullet account'.format(config['pushbullet']['device']))
        return

    optlist, args = getopt(sys.argv[1:], 'ht:p:',
                           ['help', 'target=', 'plugin='])

    target = None
    plugin = None
    payload = {}

    for opt, arg in optlist:
        if opt == 'h' or opt == '--help':
            print_usage()
            return
        elif opt == 't' or opt == '--target':
            target = arg
        elif opt == 'p' or opt == '--plugin':
            plugin = arg

    if len(args):
        payload = json.loads(args[0])
    else:
        payload = sys.stdin.read()

    if not (target and plugin):
        print_usage()
        return

    msg = {
        'target': target,
        'plugin': plugin,
        'args': payload,
    }

    pb.push_note('', json.dumps(msg), device)


if __name__ == '__main__':
    main()

# vim:sw=4:ts=4:et:

