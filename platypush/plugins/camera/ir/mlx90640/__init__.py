import os
import subprocess
from typing import Optional, Tuple

from platypush.plugins import action
from platypush.plugins.camera import CameraPlugin, Camera


class CameraIrMlx90640Plugin(CameraPlugin):
    """
    Plugin to interact with a `ML90640 <https://shop.pimoroni.com/products/mlx90640-thermal-camera-breakout>`_
    infrared thermal camera.

    In order to use this plugin you'll need to download and compile the
    `mlx90640 <https://github.com/pimoroni/mlx90640-library>`_ C++ bindings and examples for the device.
    Instructions on Raspbian::

        # Install the dependencies
        $ [sudo] apt-get install libi2c-dev
        $ cd $PLATYPUSH_SRC_DIR
        $ git submodule init
        $ git submodule update
        $ cd platypush/plugins/camera/ir/mlx90640/lib
        $ make clean
        $ make bcm2835
        $ make examples/rawrgb I2C_MODE=LINUX

    Requires:

        * **mlx90640-library** installation (see instructions above)
        * **PIL** image library (``pip install Pillow``)

    """

    def __init__(self, rawrgb_path: Optional[str] = None, resolution: Tuple[int, int] = (32, 24),
                 warmup_frames: Optional[int] = 5, **kwargs):
        """
        :param rawrgb_path: Specify it if the rawrgb executable compiled from
            https://github.com/pimoroni/mlx90640-library is in another folder than
            `<directory of this file>/lib/examples`.
        :param resolution: Device resolution (default: 32x24).
        :param warmup_frames: Number of frames to be skipped on sensor initialization/warmup (default: 2).
        :param kwargs: Extra parameters to be passed to :class:`platypush.plugins.camera.CameraPlugin`.
        """
        super().__init__(device='mlx90640', resolution=resolution, warmup_frames=warmup_frames, **kwargs)

        if not rawrgb_path:
            rawrgb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'examples', 'rawrgb')
        rawrgb_path = os.path.abspath(os.path.expanduser(rawrgb_path))

        assert os.path.isfile(rawrgb_path),\
            'rawrgb executable not found. Please follow the documentation of this plugin to build it'

        self.rawrgb_path = rawrgb_path
        self._capture_proc = None

    def _is_capture_running(self):
        return self._capture_proc is not None and self._capture_proc.poll() is None

    def prepare_device(self, device: Camera):
        if not self._is_capture_running():
            self._capture_proc = subprocess.Popen([self.rawrgb_path, '{}'.format(device.info.fps)],
                                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        return self._capture_proc

    def release_device(self, device: Camera):
        if not self._is_capture_running():
            return

        self._capture_proc.terminate()
        self._capture_proc.kill()
        self._capture_proc.wait()
        self._capture_proc = None

    def capture_frame(self, device: Camera, *args, **kwargs):
        from PIL import Image

        camera = self.prepare_device(device)
        frame = camera.stdout.read(device.info.resolution[0] * device.info.resolution[1] * 3)
        return Image.frombytes('RGB', device.info.resolution, frame)

    def to_grayscale(self, image):
        from PIL import Image
        new_image = Image.new('L', image.size)

        for i in range(0, image.size[0]):
            for j in range(0, image.size[1]):
                r, g, b = image.getpixel((i, j))
                value = int(2.0 * r - 1.125 * g - 1.75 * b)

                if value > 255:
                    value = 255
                if value < 0:
                    value = 0

                new_image.putpixel((i, j), value)

        return new_image

    @action
    def capture(self, output_file=None, *args, **kwargs):
        """
        Back-compatibility alias for :meth:`.capture_image`.
        """
        return self.capture_image(image_file=output_file, *args, **kwargs)


# vim:sw=4:ts=4:et:
