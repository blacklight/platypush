import json

from pynodered import node_red
from platypush.context import get_plugin


# noinspection PyUnusedLocal
@node_red(name='run', title='run', category='platypush', description='Run a platypush action')
def run(node, msg):
    msg = msg['payload']
    if isinstance(msg, bytes):
        msg = msg.decode()
    if isinstance(msg, str):
        msg = json.loads(msg)

    assert isinstance(msg, dict) and 'action' in msg

    if 'type' not in msg:
        msg['type'] = 'request'

    plugin_name = '.'.join(msg['action'].split('.')[:-1])
    action_name = msg['action'].split('.')[-1]
    plugin = get_plugin(plugin_name)
    action = getattr(plugin, action_name)
    args = msg.get('args', {})

    response = action(**args)
    if response.errors:
        raise response.errors[0]

    msg['payload'] = response.output
    return msg


# vim:sw=4:ts=4:et:
