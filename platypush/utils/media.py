from typing import List

from platypush.config import Config
from platypush.context import get_plugin
from platypush.plugins.media import MediaPlugin


audio_plugins = [
    'sound',
    'music.mpd',
]


def get_default_media_plugin(video: bool = False) -> MediaPlugin:
    """
    Get the default media plugin based on the current configuration.

    :param video: If True then the plugin must support video playback.
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

    if enabled_plugins:
        return enabled_plugins[0]

    assert not video, (
        'No media plugin with video support is enabled. '
        f'Supported plugins: {MediaPlugin.supported_media_plugins}'
    )

    for plugin_name in audio_plugins:
        try:
            plugin = get_plugin(plugin_name)
            if plugin and plugin_name in cfg and not cfg[plugin_name].get('disabled'):
                return plugin
        except Exception:
            pass

    raise AssertionError('No media plugin is enabled')
