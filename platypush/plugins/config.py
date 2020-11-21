from platypush import Config
from platypush.plugins import Plugin, action


class ConfigPlugin(Plugin):
    @action
    def get(self) -> dict:
        return Config.get()

    @action
    def dashboards(self) -> dict:
        return Config.get_dashboards()

    @action
    def get_dashboard(self, name: str) -> str:
        return Config.get_dashboard(name)


# vim:sw=4:ts=4:et:
