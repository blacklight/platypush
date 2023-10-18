import inspect
import pathlib
import subprocess
from typing import Optional

from platypush.commands import CommandStream, RestartCommand, StopCommand
from platypush.common.db import override_definitions
from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.utils import get_backend_class_by_name, get_plugin_class_by_name
from platypush.utils.manifest import Manifest
from platypush.utils.mock import auto_mocks


class ApplicationPlugin(Plugin):
    """
    This plugin is used to control and inspect the application state.
    """

    @property
    def _ctrl_sock(self) -> Optional[str]:
        """
        :return: The path to the UNIX socket to control the application.
        """
        return Config.get('ctrl_sock')  # type: ignore

    @action
    def stop(self):
        """
        Stop the application.
        """
        CommandStream(self._ctrl_sock).write(StopCommand())

    @action
    def restart(self):
        """
        Restart the application.
        """
        CommandStream(self._ctrl_sock).write(RestartCommand())

    @action
    def install(self, extension: str):
        """
        Install the dependencies of an extension.

        :param extension: Extension name. For plugins, it will be the plugin
        name (e.g. ``light.hue`` or ``music.mpd``); for backend, the name will
        be prefixed by ``backend.`` (e.g. ``backend.http`` or ``backend.tcp``).
        """
        getter = get_plugin_class_by_name
        if extension.startswith('backend.'):
            extension = extension[len('backend.') :]
            getter = get_backend_class_by_name

        with auto_mocks(), override_definitions():
            ext = getter(extension)

        assert ext, f'Could not find extension {extension}'
        manifest_file = str(pathlib.Path(inspect.getfile(ext)).parent / 'manifest.yaml')
        install_cmds = list(
            Manifest.from_file(manifest_file).install.to_install_commands()
        )

        if not install_cmds:
            self.logger.info('No extra requirements found for extension %s', extension)
            return

        for cmd in install_cmds:
            self.logger.info('> %s', cmd)
            subprocess.check_call(cmd, shell=True)
