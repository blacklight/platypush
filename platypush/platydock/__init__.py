"""
Platydock is a helper script that allows you to automatically create a
Dockerfile for Platypush starting from a configuration file.
"""

import argparse
from contextlib import contextmanager
import inspect
import logging
import os
import pathlib
import re
import subprocess
import sys
import textwrap
from typing import IO, Generator, Iterable

from platypush.builder import BaseBuilder
from platypush.config import Config
from platypush.utils.manifest import (
    BaseImage,
    Dependencies,
    InstallContext,
    PackageManagers,
)

logger = logging.getLogger()


class DockerBuilder(BaseBuilder):
    """
    Creates a Platypush Docker image from a configuration file.
    """

    _pkg_manager_by_base_image = {
        BaseImage.ALPINE: PackageManagers.APK,
        BaseImage.DEBIAN: PackageManagers.APT,
        BaseImage.UBUNTU: PackageManagers.APT,
    }

    _header = textwrap.dedent(
        """
        # This Dockerfile was automatically generated by Platydock.
        #
        # You can build a Platypush image from it by running
        # `docker build -t platypush .` in the same folder as this file,
        # or copy it to the root a Platypush source folder to install the
        # checked out version instead of downloading it first.
        #
        # You can then run your new image through:
        #   docker run --rm --name platypush \\
        #       -v /path/to/your/config/dir:/etc/platypush \\
        #       -v /path/to/your/workdir:/var/lib/platypush \\
        #       -p 8008:8008 \\
        #       platypush\n
        """
    )

    _footer = textwrap.dedent(
        """
        # You can customize the name of your installation by passing
        # --device-id=... to the launched command.
        """
    )

    def __init__(
        self, *args, image: BaseImage, tag: str, print_only: bool = False, **kwargs
    ):
        kwargs['install_context'] = InstallContext.DOCKER
        super().__init__(*args, **kwargs)
        self.image = image
        self.tag = tag
        self.print_only = print_only  # TODO

    @classmethod
    def get_name(cls):
        return "platydock"

    @classmethod
    def get_description(cls):
        return "Build a Platypush Docker image from a configuration file."

    @property
    def dockerfile_dir(self) -> str:
        """
        Proxy property for the output Dockerfile directory.
        """
        output = self.output
        parent = os.path.dirname(output)

        if os.path.isfile(output):
            return parent

        if os.path.isdir(output):
            return output

        logger.info('%s directory does not exist, creating it', output)
        pathlib.Path(output).mkdir(mode=0o750, parents=True, exist_ok=True)
        return output

    @property
    def dockerfile(self) -> str:
        """
        Proxy property for the output Dockerfile.
        """
        return os.path.join(self.dockerfile_dir, 'Dockerfile')

    @property
    def pkg_manager(self) -> PackageManagers:
        """
        Proxy property for the package manager to use.
        """
        return self._pkg_manager_by_base_image[self.image]

    def _read_base_dockerfile_lines(self) -> Generator[str, None, None]:
        """
        :return: The lines of the base Dockerfile.
        """
        import platypush

        base_file = os.path.join(
            str(pathlib.Path(inspect.getfile(platypush)).parent),
            'install',
            'docker',
            f'{self.image}.Dockerfile',
        )

        with open(base_file, 'r') as f:
            for line in f:
                yield line.rstrip()

    @property
    def deps(self) -> Dependencies:
        return Dependencies.from_config(
            self.cfgfile,
            pkg_manager=self.pkg_manager,
            install_context=InstallContext.DOCKER,
            base_image=self.image,
        )

    def _create_dockerfile_parser(self):
        """
        Closure for a context-aware parser for the default Dockerfile.
        """
        is_after_expose_cmd = False
        deps = self.deps
        ports = self._get_exposed_ports()

        def parser():
            nonlocal is_after_expose_cmd

            for line in self._read_base_dockerfile_lines():
                if re.match(
                    r'RUN /install/platypush/install/scripts/[A-Za-z0-9_-]+/install.sh',
                    line.strip(),
                ):
                    yield self._generate_git_clone_command()
                elif line.startswith('RUN cd /install '):
                    for new_line in deps.before:
                        yield 'RUN ' + new_line

                    for new_line in deps.to_pkg_install_commands():
                        yield 'RUN ' + new_line
                elif line == 'RUN rm -rf /install':
                    for new_line in deps.to_pip_install_commands():
                        yield 'RUN ' + new_line

                    for new_line in deps.after:
                        yield 'RUN' + new_line
                elif line.startswith('EXPOSE ') and ports:
                    if not is_after_expose_cmd:
                        yield from [f'EXPOSE {port}' for port in ports]
                        is_after_expose_cmd = True

                    continue
                elif line.startswith('CMD'):
                    yield from self._footer.split('\n')

                yield line

                if line.startswith('CMD') and self.device_id:
                    yield f'\t--device-id {self.device_id} \\'

        return parser

    def build(self):
        """
        Build a Dockerfile based on a configuration file.

        :return: The content of the generated Dockerfile.
        """

        # Set the DOCKER_CTX environment variable so any downstream logic knows
        # that we're running in a Docker build context.
        os.environ['DOCKER_CTX'] = '1'

        self._generate_dockerfile()
        if self.print_only:
            return

        self._build_image()
        self._print_instructions(
            textwrap.dedent(
                f"""
                A Docker image has been built from the configuration file {self.cfgfile}.
                The Dockerfile is available under {self.dockerfile}.
                You can run the Docker image with the following command:

                    docker run \\
                        --rm --name platypush \\
                        -v {os.path.dirname(self.cfgfile)}:/etc/platypush \\
                        -v /path/to/your/workdir:/var/lib/platypush \\
                        -p 8008:8008 \\
                        platypush
                """
            )
        )

    def _build_image(self):
        """
        Build a Platypush Docker image from the generated Dockerfile.
        """
        logger.info('Building Docker image...')
        cmd = [
            'docker',
            'build',
            '-f',
            self.dockerfile,
            '-t',
            self.tag,
            '.',
        ]

        subprocess.run(cmd, check=True)

    def _generate_dockerfile(self):
        """
        Parses the configuration file and generates a Dockerfile based on it.
        """

        @contextmanager
        def open_writer() -> Generator[IO, None, None]:
            # flake8: noqa
            f = sys.stdout if self.print_only else open(self.dockerfile, 'w')

            try:
                yield f
            finally:
                if f is not sys.stdout:
                    f.close()

        if not self.print_only:
            logger.info('Parsing configuration file %s...', self.cfgfile)

        Config.init(self.cfgfile)

        if not self.print_only:
            logger.info('Generating Dockerfile %s...', self.dockerfile)

        parser = self._create_dockerfile_parser()

        with open_writer() as f:
            f.write(self._header + '\n')
            for line in parser():
                f.write(line + '\n')

    def _generate_git_clone_command(self) -> str:
        """
        Generates a git clone command in Dockerfile that checks out the repo
        and the right git reference, if the application sources aren't already
        available under /install.
        """
        install_cmd = ' '.join(self.pkg_manager.value.install)
        uninstall_cmd = ' '.join(self.pkg_manager.value.uninstall)
        return textwrap.dedent(
            f"""
            RUN if [ ! -f "/install/setup.py" ]; then \\
              echo "Platypush source not found under the current directory, downloading it" && \\
                  {install_cmd} git && \\
                  rm -rf /install && \\
                  git clone --recursive https://github.com/BlackLight/platypush.git /install && \\
                  cd /install && \\
                  git checkout {self.gitref} && \\
                  {uninstall_cmd} git; \\
            fi
            """
        )

    @classmethod
    def _get_arg_parser(cls) -> argparse.ArgumentParser:
        parser = super()._get_arg_parser()

        parser.add_argument(
            '-i',
            '--image',
            dest='image',
            required=False,
            type=BaseImage,
            choices=list(BaseImage),
            default=BaseImage.ALPINE,
            help='Base image to use for the Dockerfile (default: alpine).',
        )

        parser.add_argument(
            '-t',
            '--tag',
            dest='tag',
            required=False,
            type=str,
            default='platypush:latest',
            help='Tag name to be used for the built image '
            '(default: "platypush:latest").',
        )

        parser.add_argument(
            '--print',
            dest='print_only',
            action='store_true',
            help='Use this flag if you only want to print the Dockerfile to '
            'stdout instead of generating an image.',
        )

        return parser

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
    DockerBuilder.from_cmdline(sys.argv[1:]).build()
    return 0


if __name__ == '__main__':
    sys.exit(main())


# vim:sw=4:ts=4:et:
