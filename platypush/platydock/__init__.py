"""
Platydock is a helper script that allows you to automatically create a
Dockerfile for Platypush starting from a configuration file.
"""

import argparse
from enum import Enum
import inspect
import os
import pathlib
import sys
from typing import Iterable

from platypush.config import Config
from platypush.utils.manifest import Dependencies, InstallContext, PackageManagers


class BaseImage(Enum):
    """
    Supported base images for Dockerfiles.
    """

    ALPINE = 'alpine'
    DEBIAN = 'debian'
    UBUNTU = 'ubuntu'

    def __str__(self) -> str:
        """
        Explicit __str__ override for argparse purposes.
        """
        return self.value


# pylint: disable=too-few-public-methods
class DockerfileGenerator:
    """
    Generate a Dockerfile from on a configuration file.

    :param cfgfile: Path to the configuration file.
    :param image: The base image to use.
    """

    _pkg_manager_by_base_image = {
        BaseImage.ALPINE: PackageManagers.APK,
        BaseImage.DEBIAN: PackageManagers.APT,
        BaseImage.UBUNTU: PackageManagers.APT,
    }

    def __init__(self, cfgfile: str, image: BaseImage) -> None:
        self.cfgfile = os.path.abspath(os.path.expanduser(cfgfile))
        self.image = image

    def generate(self) -> str:
        """
        Generate a Dockerfile based on a configuration file.

        :param cfgfile: Path to the configuration file.
        :return: The content of the generated Dockerfile.
        """
        import platypush

        Config.init(self.cfgfile)
        new_file_lines = []
        ports = self._get_exposed_ports()
        pkg_manager = self._pkg_manager_by_base_image[self.image]
        deps = Dependencies.from_config(
            self.cfgfile,
            pkg_manager=pkg_manager,
            install_context=InstallContext.DOCKER,
        )

        is_after_expose_cmd = False
        base_file = os.path.join(
            str(pathlib.Path(inspect.getfile(platypush)).parent),
            'install',
            'docker',
            f'{self.image}.Dockerfile',
        )

        with open(base_file, 'r') as f:
            file_lines = [line.rstrip() for line in f.readlines()]

        for line in file_lines:
            if line.startswith('RUN cd /install '):
                for new_line in deps.before:
                    new_file_lines.append('RUN ' + new_line)

                for new_line in deps.to_pkg_install_commands():
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

    @staticmethod
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
    )

    parser.add_argument(
        '-h', '--help', dest='show_usage', action='store_true', help='Show usage'
    )
    parser.add_argument(
        'cfgfile', type=str, nargs='?', help='The path to the configuration file.'
    )
    parser.add_argument(
        '--image',
        '-i',
        dest='image',
        required=False,
        type=BaseImage,
        choices=list(BaseImage),
        default=BaseImage.ALPINE,
        help='Base image to use for the Dockerfile.',
    )

    opts, _ = parser.parse_known_args(sys.argv[1:])
    if opts.show_usage:
        parser.print_help()
        return 0

    if not opts.cfgfile:
        print(
            f'Please specify a configuration file.\nRun {sys.argv[0]} --help to get the available options.',
            file=sys.stderr,
        )
        return 1

    dockerfile = DockerfileGenerator(opts.cfgfile, image=opts.image).generate()
    print(dockerfile)
    return 0


if __name__ == '__main__':
    sys.exit(main())


# vim:sw=4:ts=4:et:
