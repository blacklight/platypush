from typing import List

from platypush.config import Config
from platypush.context import get_plugin
from platypush.plugins.media import MediaPlugin


def get_default_media_plugin() -> MediaPlugin:
    """
    Get the default media plugin based on the current configuration.
    """

    enabled_plugins: List[MediaPlugin] = []
    cfg = Config.get() or {}

    for plugin_name in MediaPlugin.supported_media_plugins:
        try:
            plugin = get_plugin(plugin_name)
            if plugin and plugin_name in cfg and not cfg[plugin_name].get('disabled'):
                enabled_plugins.append(plugin)
        except Exception:
            pass

    local_plugins = [plugin for plugin in enabled_plugins if plugin.is_local()]

    if local_plugins:
        return local_plugins[0]

    assert (
        enabled_plugins
    ), f'No media plugin is enabled. Supported plugins: {MediaPlugin.supported_media_plugins}'

    return enabled_plugins[0]
