import json

from platypush import Config
from platypush.message import Message
from platypush.plugins import Plugin, action


class ConfigPlugin(Plugin):
    """
    This plugin can be used to programmatically access the application configuration.
    """

    @action
    def get(self) -> dict:
        """
        Get the current configuration.
        """
        return Config.get()

    @action
    def get_plugins(self) -> dict:
        """
        Get the configured plugins.
        """
        return Config.get_plugins()

    @action
    def get_backends(self) -> dict:
        """
        Get the configured backends.
        """
        return Config.get_backends()

    @action
    def get_procedures(self) -> dict:
        """
        Get the configured procedures.
        """
        return json.loads(json.dumps(Config.get_procedures(), cls=Message.Encoder))

    @action
    def dashboards(self) -> dict:
        """
        Get the configured dashboards.
        """
        return Config.get_dashboards()

    @action
    def get_dashboard(self, name: str) -> str:
        """
        Get a dashboard configuration by name.
        """
        return Config.get_dashboard(name)

    @action
    def get_device_id(self) -> str:
        """
        Get the configured ``device_id``.
        """
        return Config.get('device_id')


# vim:sw=4:ts=4:et:
