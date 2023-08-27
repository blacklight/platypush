"""
Platyvenv is a helper script that allows you to automatically create a
virtual environment for Platypush starting from a configuration file.
"""

import argparse
from contextlib import contextmanager
import inspect
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from typing import Generator, Sequence
import venv

from platypush.config import Config
from platypush.utils.manifest import (
    Dependencies,
    InstallContext,
)


# pylint: disable=too-few-public-methods
class VenvBuilder:
    """
    Build a virtual environment from on a configuration file.

    :param cfgfile: Path to the configuration file.
    :param image: The base image to use.
    """

    def __init__(self, cfgfile: str, gitref: str, output_dir: str) -> None:
        self.cfgfile = os.path.abspath(os.path.expanduser(cfgfile))
        self.output_dir = os.path.abspath(os.path.expanduser(output_dir))
        self.gitref = gitref

    @property
    def _pip_cmd(self) -> Sequence[str]:
        """
        :return: The pip install command to use for the selected environment.
        """
        return (
            os.path.join(self.output_dir, 'bin', 'python'),
            '-m',
            'pip',
            'install',
            '-U',
            '--no-cache-dir',
            '--no-input',
        )

    def _install_system_packages(self, deps: Dependencies):
        """
        Install the required system packages.
        """
        for cmd in deps.to_pkg_install_commands():
            print(f'Installing system packages: {cmd}')
            subprocess.call(re.split(r'\s+', cmd.strip()))

    @contextmanager
    def _prepare_src_dir(self) -> Generator[str, None, None]:
        """
        Prepare the source directory used to install the virtual enviornment.

        If platyvenv is launched from a local checkout of the Platypush source
        code, then that checkout will be used.

        Otherwise, the source directory will be cloned from git into a
        temporary folder.
        """
        setup_py_path = os.path.join(os.getcwd(), 'setup.py')
        if os.path.isfile(setup_py_path):
            print('Using local checkout of the Platypush source code')
            yield os.getcwd()
        else:
            checkout_dir = tempfile.mkdtemp(prefix='platypush-', suffix='.git')
            print(f'Cloning Platypush source code from git into {checkout_dir}')
            subprocess.call(
                [
                    'git',
                    'clone',
                    '--recursive',
                    'https://github.com/BlackLight/platypush.git',
                    checkout_dir,
                ]
            )

            pwd = os.getcwd()
            os.chdir(checkout_dir)
            subprocess.call(['git', 'checkout', self.gitref])
            yield checkout_dir

            os.chdir(pwd)
            print(f'Cleaning up {checkout_dir}')
            shutil.rmtree(checkout_dir, ignore_errors=True)

    def _prepare_venv(self) -> None:
        """
        Installs the virtual environment under the configured output_dir.
        """
        print(f'Creating virtual environment under {self.output_dir}...')

        venv.create(
            self.output_dir,
            symlinks=True,
            with_pip=True,
            upgrade_deps=True,
        )

        print(
            f'Installing base Python dependencies under {self.output_dir}...',
        )

        subprocess.call([*self._pip_cmd, 'pip', '.'])

    def _install_extra_pip_packages(self, deps: Dependencies):
        """
        Install the extra pip dependencies parsed through the
        """
        pip_deps = list(deps.to_pip_install_commands(full_command=False))
        if not pip_deps:
            return

        print(
            f'Installing extra pip dependencies under {self.output_dir}: '
            + ' '.join(pip_deps)
        )

        subprocess.call([*self._pip_cmd, *pip_deps])

    def _generate_run_sh(self) -> str:
        """
        Generate a ``run.sh`` script to run the application from a newly built
        virtual environment.

        :return: The location of the generated ``run.sh`` script.
        """
        run_sh_path = os.path.join(self.output_dir, 'bin', 'run.sh')
        with open(run_sh_path, 'w') as run_sh:
            run_sh.write(
                textwrap.dedent(
                    f"""
                    #!/bin/bash

                    cd {self.output_dir}

                    # Activate the virtual environment
                    source bin/activate

                    # Run the application with the configuration file passed
                    # during build
                    platypush -c {self.cfgfile} $*
                    """
                )
            )

        os.chmod(run_sh_path, 0o750)
        return run_sh_path

    def build(self):
        """
        Build a Dockerfile based on a configuration file.
        """
        Config.init(self.cfgfile)

        deps = Dependencies.from_config(
            self.cfgfile,
            install_context=InstallContext.VENV,
        )

        self._install_system_packages(deps)

        with self._prepare_src_dir():
            self._prepare_venv()

        self._install_extra_pip_packages(deps)
        run_sh_path = self._generate_run_sh()
        print(
            f'\nVirtual environment created under {self.output_dir}.\n'
            f'You can run the application through the {run_sh_path} script.\n'
        )

    @classmethod
    def from_cmdline(cls, args: Sequence[str]) -> 'VenvBuilder':
        """
        Create a DockerfileGenerator instance from command line arguments.

        :param args: Command line arguments.
        :return: A DockerfileGenerator instance.
        """
        parser = argparse.ArgumentParser(
            prog='platyvenv',
            add_help=False,
            description='Create a Platypush virtual environment from a config.yaml.',
        )

        parser.add_argument(
            '-h', '--help', dest='show_usage', action='store_true', help='Show usage'
        )

        parser.add_argument(
            'cfgfile',
            type=str,
            nargs='?',
            help='The path to the configuration file. If not specified a minimal '
            'virtual environment only with the base dependencies will be '
            'generated.',
        )

        parser.add_argument(
            '-o',
            '--output',
            dest='output_dir',
            type=str,
            required=False,
            default='venv',
            help='Target directory for the virtual environment (default: ./venv)',
        )

        parser.add_argument(
            '--ref',
            '-r',
            dest='gitref',
            required=False,
            type=str,
            default='master',
            help='If platyvenv is not run from a Platypush installation directory, '
            'it will clone the sources via git. You can specify through this '
            'option which branch, tag or commit hash to use. Defaults to master.',
        )

        opts, _ = parser.parse_known_args(args)
        if opts.show_usage:
            parser.print_help()
            sys.exit(0)

        if not opts.cfgfile:
            opts.cfgfile = os.path.join(
                str(pathlib.Path(inspect.getfile(Config)).parent),
                'config.auto.yaml',
            )

            print(
                f'No configuration file specified. Using {opts.cfgfile}.',
                file=sys.stderr,
            )

        return cls(opts.cfgfile, gitref=opts.gitref, output_dir=opts.output_dir)


def main():
    """
    Generates a virtual environment based on the configuration file.
    """
    VenvBuilder.from_cmdline(sys.argv[1:]).build()


if __name__ == '__main__':
    sys.exit(main())


# vim:sw=4:ts=4:et:
