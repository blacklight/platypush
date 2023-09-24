import os
import re

import yaml

from sphinx.application import Sphinx


def add_events(source: list[str], manifest: dict, idx: int) -> int:
    events = manifest.get('events', [])
    if not events:
        return idx

    source.insert(
        idx,
        'Triggered events\n----------------\n\n'
        + '\n'.join(f'\t- :class:`{event}`' for event in events)
        + '\n\n',
    )

    return idx + 1


def add_install_deps(source: list[str], manifest: dict, idx: int) -> int:
    install_deps = manifest.get('install', {})
    install_cmds = {
        'pip': 'pip install',
        'Alpine': 'apk add',
        'Arch Linux': 'pacman -S',
        'Debian': 'apt install',
        'Fedora': 'yum install',
    }

    parsed_deps = {
        'pip': install_deps.get('pip', []),
        'Alpine': install_deps.get('apk', []),
        'Arch Linux': install_deps.get('pacman', []),
        'Debian': install_deps.get('apt', []),
        'Fedora': install_deps.get('dnf', install_deps.get('yum', [])),
    }

    if not any(parsed_deps.values()):
        return idx

    source.insert(idx, 'Dependencies\n^^^^^^^^^^^^\n\n')
    idx += 1

    for env, deps in parsed_deps.items():
        if deps:
            install_cmd = install_cmds[env]
            source.insert(
                idx,
                f'**{env}**\n\n'
                + '.. code-block:: bash\n\n\t'
                + f'{install_cmd} '
                + ' '.join(deps)
                + '\n\n',
            )

            idx += 1

    return idx


def parse_dependencies(_: Sphinx, doc: str, source: list[str]):
    if not (source and re.match(r'^platypush/(backend|plugins)/.*', doc)):
        return

    src = [src.split('\n') for src in source][0]
    if len(src) < 3:
        return

    base_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.relpath(__file__)), '..', '..', '..')
    )
    manifest_file = os.path.join(
        base_path,
        *doc.split(os.sep)[:-1],
        *doc.split(os.sep)[-1].split('.'),
        'manifest.yaml',
    )
    if not os.path.isfile(manifest_file):
        return

    with open(manifest_file) as f:
        manifest: dict = yaml.safe_load(f).get('manifest', {})

    idx = add_install_deps(src, manifest, idx=3)
    add_events(src, manifest, idx=idx)
    source[0] = '\n'.join(src)


def setup(app: Sphinx):
    app.connect('source-read', parse_dependencies)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
