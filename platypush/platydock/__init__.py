"""
Platydock is a helper script that allows you to automatically create a
Dockerfile for Platypush starting from a configuration file.
"""

import argparse
import inspect
import os
import pathlib
import sys
from typing import Iterable

from platypush.config import Config
from platypush.utils.manifest import Dependencies

ERR_PREFIX = '\n\033[6;31;47mERROR\033[0;91m '
ERR_SUFFIX = '\033[0m'


def generate_dockerfile(cfgfile: str) -> str:
    """
    Generate a Dockerfile based on a configuration file.

    :param cfgfile: Path to the configuration file.
    :return: The content of the generated Dockerfile.
    """
    Config.init(cfgfile)
    new_file_lines = []
    ports = _get_exposed_ports()
    deps = Dependencies.from_config(cfgfile, pkg_manager='apk')
    is_after_expose_cmd = False
    base_file = os.path.join(
        str(pathlib.Path(inspect.getfile(Config)).parent), 'docker', 'base.Dockerfile'
    )

    with open(base_file, 'r') as f:
        file_lines = [line.rstrip() for line in f.readlines()]

    for line in file_lines:
        if line.startswith('RUN cd /install '):
            for new_line in deps.before:
                new_file_lines.append('RUN ' + new_line)

            for new_line in deps.to_pkg_install_commands(
                pkg_manager='apk', skip_sudo=True
            ):
                new_file_lines.append('RUN ' + new_line)
        elif line == 'RUN rm -rf /install':
            for new_line in deps.to_pip_install_commands():
                new_file_lines.append('RUN ' + new_line)

            for new_line in deps.after:
                new_file_lines.append('RUN' + new_line)
        elif line.startswith('EXPOSE ') and ports:
            if not is_after_expose_cmd:
                new_file_lines.extend([f'EXPOSE {port}' for port in ports])
                is_after_expose_cmd = True

            continue

        new_file_lines.append(line)

    return '\n'.join(new_file_lines)


def _get_exposed_ports() -> Iterable[int]:
    """
    :return: The listen ports used by the backends enabled in the configuration
        file.
    """
    backends_config = Config.get_backends()
    return {
        int(port)
        for port in (
            backends_config.get('http', {}).get('port'),
            backends_config.get('tcp', {}).get('port'),
        )
        if port
    }


def main():
    """
    Generates a Dockerfile based on the configuration file.
    """
    parser = argparse.ArgumentParser(
        prog='platydock',
        add_help=False,
        description='Create a Platypush Dockerfile from a config.yaml.',
        epilog='Use platydock <action> --help to get additional help.',
    )

    parser.add_argument('-h', '--help', action='store_true', help='Show usage')
    parser.add_argument(
        'cfgfile', type=str, nargs=1, help='The path to the configuration file.'
    )

    opts, _ = parser.parse_known_args(sys.argv[1:])
    cfgfile = os.path.abspath(os.path.expanduser(opts.cfgfile[0]))
    dockerfile = generate_dockerfile(cfgfile)
    print(dockerfile)


if __name__ == '__main__':
    main()


# vim:sw=4:ts=4:et:
