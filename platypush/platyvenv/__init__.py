"""
Platyvenv is a helper script that allows you to automatically create a
virtual environment for Platypush starting from a configuration file.
"""

from contextlib import contextmanager
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from typing import Generator, Sequence
import venv

from platypush.builder import BaseBuilder
from platypush.config import Config
from platypush.utils.manifest import (
    Dependencies,
    InstallContext,
)

logger = logging.getLogger()


class VenvBuilder(BaseBuilder):
    """
    Build a virtual environment from on a configuration file.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs['install_context'] = InstallContext.DOCKER
        super().__init__(*args, **kwargs)

    @classmethod
    def get_name(cls):
        return "platyvenv"

    @classmethod
    def get_description(cls):
        return "Build a Platypush virtual environment from a configuration file."

    @property
    def _pip_cmd(self) -> Sequence[str]:
        """
        :return: The pip install command to use for the selected environment.
        """
        return (
            os.path.join(self.output, 'bin', 'python'),
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
            logger.info('Installing system packages: %s', cmd)
            subprocess.run(cmd, shell=True, check=True)

    def _run_before_commands(self, deps: Dependencies):
        """
        Runs any commands that should be executed before the installation.
        """
        for cmd in deps.before:
            logger.info('Running: %s', cmd)
            subprocess.run(cmd, shell=True, check=True)

    def _run_after_commands(self, deps: Dependencies):
        """
        Runs any commands that should be executed after the installation.
        """
        for cmd in deps.after:
            logger.info('Running: %s', cmd)
            subprocess.run(cmd, shell=True, check=True)

    @contextmanager
    def _prepare_src_dir(self) -> Generator[str, None, None]:
        """
        Prepare the source directory used to install the virtual enviornment.

        If platyvenv is launched from a local checkout of the Platypush source
        code, then that checkout will be used.

        Otherwise, the source directory will be cloned from git into a
        temporary folder.
        """
        if os.path.isfile(os.path.join(os.getcwd(), 'pyproject.toml')):
            logger.info('Using local checkout of the Platypush source code')
            yield os.getcwd()
        else:
            checkout_dir = tempfile.mkdtemp(prefix='platypush-', suffix='.git')
            logger.info('Cloning Platypush source code from git into %s', checkout_dir)
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
            logger.info('Cleaning up %s', checkout_dir)
            shutil.rmtree(checkout_dir, ignore_errors=True)

    def _prepare_venv(self) -> None:
        """
        Install the virtual environment under the configured output.
        """
        logger.info('Creating virtual environment under %s...', self.output)

        venv.create(
            self.output,
            symlinks=True,
            with_pip=True,
            upgrade_deps=True,
        )

        logger.info('Installing base Python dependencies under %s...', self.output)
        subprocess.call([*self._pip_cmd, 'pip', '.'])

        # Add <output>/bin to the PATH
        os.environ['PATH'] = os.path.join(self.output, 'bin') + ':' + os.environ['PATH']

    def _install_extra_pip_packages(self, deps: Dependencies):
        """
        Install the extra pip dependencies inferred from the configured
        extensions.
        """
        pip_deps = list(deps.to_pip_install_commands(full_command=False))
        if not pip_deps:
            return

        logger.info(
            'Installing extra pip dependencies under %s: %s',
            self.output,
            ' '.join(pip_deps),
        )

        subprocess.call([*self._pip_cmd, *pip_deps])

    def build(self):
        """
        Build a Dockerfile based on a configuration file.
        """
        Config.init(self.cfgfile)

        deps = Dependencies.from_config(
            self.cfgfile,
            install_context=InstallContext.VENV,
        )

        self._run_before_commands(deps)
        self._install_system_packages(deps)

        with self._prepare_src_dir():
            self._prepare_venv()

        self._install_extra_pip_packages(deps)
        self._run_after_commands(deps)

        self._print_instructions(
            textwrap.dedent(
                f"""
                Virtual environment created under {self.output}.
                To run the application:

                    source {self.output}/bin/activate
                    platypush -c {self.cfgfile} {
                        "--device_id " + self.device_id if self.device_id else ""
                    }

                Platypush requires a Redis instance. If you don't want to use a
                stand-alone server, you can pass the --start-redis option to
                the executable (optionally with --redis-port).

                Platypush will then start its own local instance and it will
                terminate it once the application is stopped.
                """
            )
        )


def main():
    """
    Generates a virtual environment based on the configuration file.
    """
    VenvBuilder.from_cmdline(sys.argv[1:]).build()
    return 0


if __name__ == '__main__':
    sys.exit(main())


# vim:sw=4:ts=4:et:
