import argparse
import sys

from . import Driver
from . import Scanner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', '-s', dest='scan', required=False, default=False, action='store_true',
                        help="Run Switchbot in scan mode - scan devices to control")

    parser.add_argument('--scan-timeout', dest='scan_timeout', required=False, default=None,
                        help="Device scan timeout (default: 2 seconds)")

    parser.add_argument('--connect-timeout', dest='connect_timeout', required=False, default=None,
                        help="Device connection timeout (default: 5 seconds)")

    parser.add_argument('--device', '-d', dest='device', required=False, default=None,
                        help="Specify the address of a device to control")

    parser.add_argument('--interface', '-i', dest='interface', required=False, default=None,
                        help="Name of the bluetooth adapter (default: hci0 or whichever is the default)")

    parser.add_argument('--press', '-p', dest='press', required=False, default=None, action='store_true',
                        help="Send a press command (default)")

    parser.add_argument('--on', dest='on', required=False, default=None, action='store_true',
                        help="Send a press on command")

    parser.add_argument('--off', dest='off', required=False, default=None, action='store_true',
                        help="Send a press on command")

    opts, args = parser.parse_known_args(sys.argv[1:])

    if opts.scan:
        scanner = Scanner(opts.interface, int(opts.scan_timeout))
        devices = scanner.scan()

        if not devices:
            print('No Switchbots found')
            sys.exit(1)

        print('Found {} devices: {}'.format(len(devices), devices))
        print('Enter the number of the device you want to control:')

        for i in range(0, len(devices)):
            print('\t{}\t{}'.format(i, devices[i]))

        i = int(input())
        bt_addr = devices[i]
    elif opts.device:
        bt_addr = opts.device
    else:
        raise RuntimeError('Please specify at least one mode between --scan and --device')

    driver = Driver(device=bt_addr, bt_interface=opts.interface, timeout_secs=int(opts.connect_timeout))
    driver.connect()
    print('Connected!')

    if opts.on:
        driver.run_command('on')
    elif opts.off:
        driver.run_command('off')
    else:
        driver.run_command('press')

    print('Command execution successful')


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:

