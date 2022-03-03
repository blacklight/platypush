import inspect
import os

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.plugins import Plugin
from platypush.utils.manifest import get_manifests


def _get_inspect_plugin():
    p = get_plugin('inspect')
    assert p, 'Could not load the `inspect` plugin'
    return p


def get_all_plugins():
    manifests = {mf.component_name for mf in get_manifests(Plugin)}
    return {
        plugin_name: plugin_info
        for plugin_name, plugin_info in _get_inspect_plugin().get_all_plugins().output.items()
        if plugin_name in manifests
    }


def get_all_backends():
    manifests = {mf.component_name for mf in get_manifests(Backend)}
    return {
        backend_name: backend_info
        for backend_name, backend_info in _get_inspect_plugin().get_all_backends().output.items()
        if backend_name in manifests
    }


def get_all_events():
    return _get_inspect_plugin().get_all_events().output


def get_all_responses():
    return _get_inspect_plugin().get_all_responses().output


# noinspection DuplicatedCode
def generate_plugins_doc():
    plugins_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'plugins.rst')
    plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'platypush', 'plugins')
    all_plugins = sorted(plugin for plugin in get_all_plugins().keys())

    for plugin in all_plugins:
        plugin_file = os.path.join(plugins_dir, plugin + '.rst')
        if not os.path.exists(plugin_file):
            plugin = 'platypush.plugins.' + plugin
            header = '``{}``'.format('.'.join(plugin.split('.')[2:]))
            divider = '=' * len(header)
            body = '\n.. automodule:: {}\n    :members:\n'.format(plugin)
            out = '\n'.join([header, divider, body])

            with open(plugin_file, 'w') as f:
                f.write(out)

    with open(plugins_index, 'w') as f:
        f.write('''
Plugins
=======

.. toctree::
    :maxdepth: 2
    :caption: Plugins:

''')

        for plugin in all_plugins:
            f.write('    platypush/plugins/' + plugin + '.rst\n')


# noinspection DuplicatedCode
def generate_backends_doc():
    backends_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'backends.rst')
    backends_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'platypush', 'backend')
    all_backends = sorted(backend for backend in get_all_backends().keys())

    for backend in all_backends:
        backend_file = os.path.join(backends_dir, backend + '.rst')
        if not os.path.exists(backend_file):
            backend = 'platypush.backend.' + backend
            header = '``{}``'.format('.'.join(backend.split('.')[2:]))
            divider = '=' * len(header)
            body = '\n.. automodule:: {}\n    :members:\n'.format(backend)
            out = '\n'.join([header, divider, body])

            with open(backend_file, 'w') as f:
                f.write(out)

    with open(backends_index, 'w') as f:
        f.write('''
Backends
========

.. toctree::
    :maxdepth: 2
    :caption: Backends:

''')

        for backend in all_backends:
            f.write('    platypush/backend/' + backend + '.rst\n')


# noinspection DuplicatedCode
def generate_events_doc():
    from platypush.message import event as event_module
    events_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'events.rst')
    events_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'platypush', 'events')
    all_events = sorted(event for event in get_all_events().keys() if event)

    for event in all_events:
        event_file = os.path.join(events_dir, event + '.rst')
        if not os.path.exists(event_file):
            header = '``{}``'.format(event)
            divider = '=' * len(header)
            body = '\n.. automodule:: {}.{}\n    :members:\n'.format(event_module.__name__, event)
            out = '\n'.join([header, divider, body])

            with open(event_file, 'w') as f:
                f.write(out)

    with open(events_index, 'w') as f:
        f.write('''
Events
======

.. toctree::
    :maxdepth: 2
    :caption: Events:

''')

        for event in all_events:
            f.write('    platypush/events/' + event + '.rst\n')


# noinspection DuplicatedCode
def generate_responses_doc():
    from platypush.message import response as response_module
    responses_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'responses.rst')
    responses_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'platypush', 'responses')
    all_responses = sorted(response for response in get_all_responses().keys() if response)

    for response in all_responses:
        response_file = os.path.join(responses_dir, response + '.rst')
        if not os.path.exists(response_file):
            header = '``{}``'.format(response)
            divider = '=' * len(header)
            body = '\n.. automodule:: {}.{}\n    :members:\n'.format(response_module.__name__, response)
            out = '\n'.join([header, divider, body])

            with open(response_file, 'w') as f:
                f.write(out)

    with open(responses_index, 'w') as f:
        f.write('''
Responses
=========

.. toctree::
    :maxdepth: 2
    :caption: Responses:

''')

        for response in all_responses:
            f.write('    platypush/responses/' + response + '.rst\n')


generate_plugins_doc()
generate_backends_doc()
generate_events_doc()
generate_responses_doc()


# vim:sw=4:ts=4:et:
