import sys

from . import Pusher

def main(args=sys.argv[1:]):
    opts = Pusher.parse_build_args(args)

    pusher = Pusher(config_file=opts.config, backend=opts.backend)

    if opts.type == 'event':
        delattr(opts, 'type')
        print(opts.args)
        pusher.send_event(target=opts.target, type=opts.event, **opts.args)
    else:
        pusher.push(target=opts.target, action=opts.action, timeout=opts.timeout, **opts.args)


main()

# vim:sw=4:ts=4:et:

