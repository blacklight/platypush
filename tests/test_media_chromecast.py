from platypush.plugins.media.chromecast import (
    CHROMECAST_YOUTUBE_FORMAT,
    MediaChromecastPlugin,
)


def test_chromecast_youtube_defaults_prefer_supported_codecs():
    plugin = MediaChromecastPlugin()

    assert plugin.youtube_format == CHROMECAST_YOUTUBE_FORMAT
    assert 'vcodec^=avc1' in plugin.youtube_format
    assert 'acodec^=mp4a' in plugin.youtube_format
    assert plugin.merge_output_format == 'mp4'
    assert plugin.ytdl_args == []
