import numpy as np
from PIL.Image import Image as ImageType

from platypush.plugins.camera.model.writer import FileVideoWriter


class CvFileWriter(FileVideoWriter):
    """
    Write camera frames to a file using OpenCV.
    """
    def __init__(self, *args, **kwargs):
        import cv2
        super(CvFileWriter, self).__init__(*args, **kwargs)

        video_type = cv2.VideoWriter_fourcc(*(self.camera.info.output_format or 'xvid').upper())
        resolution = (
            int(self.camera.info.resolution[0] * (self.camera.info.scale_x or 1.)),
            int(self.camera.info.resolution[1] * (self.camera.info.scale_y or 1.)),
        )

        self.writer = cv2.VideoWriter(self.output_file, video_type, self.camera.info.fps, resolution, False)

    def write(self, img):
        if not self.writer:
            return

        # noinspection PyBroadException
        try:
            if isinstance(img, ImageType):
                # noinspection PyTypeChecker
                img = np.array(img)
        except:
            pass

        self.writer.write(img)

    def close(self):
        if not self.writer:
            return

        self.writer.release()
        self.writer = None
        super().close()


# vim:sw=4:ts=4:et:
