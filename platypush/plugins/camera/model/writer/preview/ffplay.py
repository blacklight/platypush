import logging
import subprocess
import threading

from platypush.plugins.camera.model.writer.image import MJPEGStreamWriter
from platypush.plugins.camera.model.writer.preview import PreviewWriter


class FFplayPreviewWriter(PreviewWriter, MJPEGStreamWriter):
    """
    General class for managing previews from camera devices or generic sources of images over ffplay.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ffplay = subprocess.Popen(['ffplay', '-'], stdin=subprocess.PIPE)
        self._preview_thread = threading.Thread(target=self._ffplay_thread)
        self._preview_thread.start()

    def _ffplay_thread(self):
        while not self.closed and self.ffplay.poll() is None:
            with self.ready:
                self.ready.wait(1.)
                if not self.frame:
                    continue

                try:
                    self.ffplay.stdin.write(self.frame)
                except Exception as e:
                    self.logger.warning('ffplay write error: {}'.format(str(e)))
                    self.close()
                    break

    def close(self):
        if self.ffplay and self.ffplay.poll() is None:
            self.ffplay.terminate()

        self.camera = None
        super().close()
        if self._preview_thread and self._preview_thread.is_alive() and \
                threading.get_ident() != self._preview_thread.ident:
            self._preview_thread.join(timeout=5.0)
            self._preview_thread = None


# vim:sw=4:ts=4:et:
