from queue import Empty
import wx

from platypush.plugins.camera.model.writer.preview import PreviewWriter


class Panel(wx.Panel):
    def __init__(self, parent, process, width: int, height: int):
        import wx
        super().__init__(parent, -1)

        self.process: PreviewWriter = process
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetSize(width, height)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.update()

    @staticmethod
    def img_to_bitmap(image) -> wx.Bitmap:
        import wx
        return wx.Bitmap.FromBuffer(image.width, image.height, image.tobytes())

    def get_bitmap(self):
        try:
            return self.process.bitmap_queue.get(block=True, timeout=1.0)
        except Empty:
            return None

    def update(self):
        import wx
        self.Refresh()
        self.Update()
        wx.CallLater(15, self.update)

    def create_bitmap(self):
        image = self.get_bitmap()
        if image is None:
            return

        return self.img_to_bitmap(image)

    def on_paint(self, *_, **__):
        import wx
        bitmap = self.create_bitmap()
        if not bitmap:
            return

        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(bitmap, 0, 0)


class Frame(wx.Frame):
    def __init__(self, process):
        import wx
        style = wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX
        self.process = process
        image = self.process.bitmap_queue.get()

        super().__init__(None, -1, process.camera.info.device or 'Camera Preview', style=style)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_close)
        self.panel = Panel(self, process, width=image.width, height=image.height)
        self.Fit()

    def on_close(self, *_, **__):
        self.process.close()


# vim:sw=4:ts=4:et:
