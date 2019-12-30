import os

from platypush.context import get_plugin


def get_all_plugins():
    return get_plugin('inspect').get_all_plugins().output


def get_all_backends():
    return get_plugin('inspect').get_all_backends().output


# noinspection DuplicatedCode
def generate_plugins_doc():
    plugins_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'plugins.rst')
    plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'source', 'platypush', 'plugins')
    all_plugins = sorted(plugin for plugin in get_all_plugins().keys())

    for plugin in all_plugins:
        plugin_file = os.path.join(plugins_dir, plugin + '.rst')
        if not os.path.exists(plugin_file):
            plugin = 'platypush.plugins.' + plugin
            header = '``{}``'.format(plugin)
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
            header = '``{}``'.format(backend)
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


generate_plugins_doc()
generate_backends_doc()


# vim:sw=4:ts=4:et:
