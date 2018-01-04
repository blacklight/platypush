import sys

from . import Pusher

opts = Pusher.parse_build_args(sys.argv[1:])
pusher = Pusher(config_file=opts.config, backend=opts.backend)

if opts.type == 'event':
    pusher.send_event(target=opts.target, type=opts.event, **opts.args)
else:
    pusher.send_request(target=opts.target, action=opts.action, timeout=opts.timeout, **opts.args)


# vim:sw=4:ts=4:et:

