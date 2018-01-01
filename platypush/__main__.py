import sys

from . import Daemon, __version__

def main(args=sys.argv[1:]):
    print('Starting platypush v.{}'.format(__version__))
    app = Daemon.build_from_cmdline(args)
    app.start()

if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:

