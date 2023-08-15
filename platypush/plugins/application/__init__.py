from typing import Optional
from platypush.commands import CommandStream, RestartCommand, StopCommand
from platypush.config import Config
from platypush.plugins import Plugin, action


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
