from multiprocessing import Process, Queue, Event

from platypush.plugins.camera.model.writer import VideoWriter
from platypush.plugins.camera.model.writer.preview import PreviewWriter


class WxPreviewWriter(PreviewWriter, Process):
    """
    General class for managing previews from camera devices or sources of images.
    """

    def __init__(self, camera, plugin, *args, **kwargs):
        Process.__init__(self, *args, **kwargs)
        VideoWriter.__init__(self, camera=camera, plugin=plugin)
        self.app = None
        self.bitmap_queue = Queue()
        self.stopped_event = Event()

    def run(self) -> None:
        import wx
        from platypush.plugins.camera.model.writer.preview.wx.ui import Frame

        self.app = wx.App()
        frame = Frame(self)
        frame.Center()
        frame.Show()
        self.app.MainLoop()

    def close(self):
        if not self.app:
            return

        self.app.ExitMainLoop()
        self.app = None
        self.camera.preview = None
        self.bitmap_queue.close()
        self.bitmap_queue = None
        self.stopped_event.set()

    def write(self, image):
        if self.stopped_event.is_set():
            return

        try:
            self.bitmap_queue.put(image)
        except Exception as e:
            self.logger.warning('Could not add an image to the preview queue: {}'.format(str(e)))


# vim:sw=4:ts=4:et:
