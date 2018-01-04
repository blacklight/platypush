import sys

from platypush import Daemon, __version__

print('Starting platypush v.{}'.format(__version__))
app = Daemon.build_from_cmdline(sys.argv[1:])
app.start()


# vim:sw=4:ts=4:et:

