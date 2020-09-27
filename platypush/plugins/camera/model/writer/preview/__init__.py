import logging

from abc import ABC

from platypush.plugins.camera.model.writer import VideoWriter

logger = logging.getLogger('platypush')


class PreviewWriter(VideoWriter, ABC):
    """
    Abstract class for camera previews.
    """


class PreviewWriterFactory:
    @staticmethod
    def get(*args, **kwargs) -> PreviewWriter:
        try:
            import wx
            # noinspection PyUnresolvedReferences
            from platypush.plugins.camera.model.writer.preview.wx import WxPreviewWriter
            return WxPreviewWriter(*args, **kwargs)
        except ImportError:
            logger.warning('wxPython not available, using ffplay as a fallback for camera previews')

        from platypush.plugins.camera.model.writer.preview.ffplay import FFplayPreviewWriter
        return FFplayPreviewWriter(*args, **kwargs)


# vim:sw=4:ts=4:et:
