from abc import ABC, abstractmethod
import argparse
import inspect
import logging
import os
import pathlib
import sys
from typing import Optional, Sequence

from platypush.config import Config
from platypush.utils.manifest import (
    Dependencies,
    InstallContext,
)

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()


class BaseBuilder(ABC):
    """
    Base interface and utility methods for Platypush builders.

    A Platypush builder is a script/piece of logic that can build a Platypush
    installation, with all its base and required extra dependencies, given a
    configuration file.

    This class is currently implemented by the :module:`platypush.platyvenv`
    and :module:`platypush.platydock` modules/scripts.
    """

    REPO_URL: str = 'https://github.com/blacklight/platypush.git'
    """
    We use the Github URL here rather than the self-hosted Gitea URL to prevent
    too many requests to the Gitea server.
    """

    def __init__(
        self,
        cfgfile: str,
        gitref: str,
        output: str,
        install_context: InstallContext,
        *_,
        verbose: bool = False,
        device_id: Optional[str] = None,
        **__,
    ) -> None:
        """
        :param cfgfile: The path to the configuration file.
        :param gitref: The git reference to use. It can be a branch name, a tag
            name or a commit hash.
        :param output: The path to the output file or directory.
        :param install_context: The installation context for this builder.
        :param verbose: Whether to log debug traces.
        :param device_id: A device name that will be used to uniquely identify
            this installation.
        """
        self.cfgfile = os.path.abspath(os.path.expanduser(cfgfile))
        self.output = os.path.abspath(os.path.expanduser(output))
        self.gitref = gitref
        self.install_context = install_context
        self.device_id = device_id
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """
        :return: The name of the builder.
        """

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """
        :return: The description of the builder.
        """

    @property
    def deps(self) -> Dependencies:
        """
        :return: The dependencies for this builder, given the configuration
            file and the installation context.
        """
        return Dependencies.from_config(
            self.cfgfile,
            install_context=self.install_context,
        )

    def _print_instructions(self, s: str) -> None:
        GREEN = '\033[92m'
        NORM = '\033[0m'

        helper_lines = s.split('\n')
        wrapper_line = '=' * max(len(t) for t in helper_lines)
        helper = '\n' + '\n'.join([wrapper_line, *helper_lines, wrapper_line]) + '\n'
        print(GREEN + helper + NORM)

    @abstractmethod
    def build(self):
        """
        Builds the application. To be implemented by the subclasses.
        """

    @classmethod
    def _get_arg_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=cls.get_name(),
            add_help=False,
            description=cls.get_description(),
        )

        parser.add_argument(
            '-h', '--help', dest='show_usage', action='store_true', help='Show usage'
        )

        parser.add_argument(
            '-v',
            '--verbose',
            dest='verbose',
            action='store_true',
            help='Enable debug traces',
        )

        parser.add_argument(
            '-c',
            '--config',
            type=str,
            dest='cfgfile',
            required=False,
            default=None,
            help='The path to the configuration file. If not specified, a minimal '
            'installation including only the base dependencies will be generated.',
        )

        parser.add_argument(
            '-o',
            '--output',
            dest='output',
            type=str,
            required=False,
            default='.',
            help='Target directory (default: current directory). For Platydock, '
            'this is the directory where the Dockerfile will be generated. For '
            'Platyvenv, this is the base directory of the new virtual '
            'environment.',
        )

        parser.add_argument(
            '-d',
            '--device-id',
            dest='device_id',
            type=str,
            required=False,
            default=None,
            help='A name that will be used to uniquely identify this device. '
            'Default: a random name for Docker containers, and the '
            'hostname of the machine for virtual environments.',
        )

        parser.add_argument(
            '-r',
            '--ref',
            dest='gitref',
            required=False,
            type=str,
            default='master',
            help='If the script is not run from a Platypush installation directory, '
            'it will clone the sources via git. You can specify through this '
            'option which branch, tag or commit hash to use. Defaults to master.',
        )

        return parser

    @classmethod
    def from_cmdline(cls, args: Sequence[str]):
        """
        Create a builder instance from command line arguments.

        :param args: Command line arguments.
        :return: A builder instance.
        """
        parser = cls._get_arg_parser()
        opts, _ = parser.parse_known_args(args)
        if opts.show_usage:
            parser.print_help()
            sys.exit(0)

        if not opts.cfgfile:
            opts.cfgfile = os.path.join(
                str(pathlib.Path(inspect.getfile(Config)).parent),
                'config.yaml',
            )

            logger.info('No configuration file specified. Using %s.', opts.cfgfile)

        return cls(**vars(opts))
