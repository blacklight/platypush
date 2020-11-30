import json

from platypush import Config
from platypush.message import Message
from platypush.plugins import Plugin, action


class ConfigPlugin(Plugin):
    @action
    def get(self) -> dict:
        return Config.get()

    @action
    def get_plugins(self) -> dict:
        return Config.get_plugins()

    @action
    def get_backends(self) -> dict:
        return Config.get_backends()

    @action
    def get_procedures(self) -> dict:
        return json.loads(json.dumps(Config.get_procedures(), cls=Message.Encoder))

    @action
    def dashboards(self) -> dict:
        return Config.get_dashboards()

    @action
    def get_dashboard(self, name: str) -> str:
        return Config.get_dashboard(name)

    @action
    def get_device_id(self) -> str:
        return Config.get('device_id')


# vim:sw=4:ts=4:et:
