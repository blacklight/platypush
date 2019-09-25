import os
import subprocess
import time

from platypush.plugins import Plugin, action


class CameraIrMlx90640Plugin(Plugin):
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

    """

    _img_size = (24, 32)

    def __init__(self, fps=16, skip_frames=2, scale_factor=10, rawrgb_path=None, **kwargs):
        """
        :param fps: Frames per seconds (default: 16)
        :param skip_frames: Number of frames to be skipped on sensor initialization/warmup (default: 2)
        :param scale_factor: The camera outputs 24x32 pixels artifacts. Use scale_factor to scale them up to a larger image (default: 10)
        :param rawrgb_path: Specify it if the rawrgb executable compiled from
            https://github.com/pimoroni/mlx90640-library is in another folder than
            `<directory of this file>/lib/examples`.
        """
        super().__init__(**kwargs)

        if not rawrgb_path:
            rawrgb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'examples', 'rawrgb')

        assert fps > 0
        assert skip_frames >= 0
        assert os.path.isfile(rawrgb_path)

        self.fps = fps
        self.skip_frames = skip_frames
        self.scale_factor = scale_factor
        self.rawrgb_path = rawrgb_path

    @action
    def capture(self, frames=1, skip_frames=None):
        """
        Capture one or multiple frames and return them as raw RGB

        :param frames: Number of frames to be captured (default: 1)
        :param skip_frames: If set it overrides the skip_frames parameter specified on the object (default: None)
        """

        if skip_frames is None:
            skip_frames = self.skip_frames

        input_size = self._img_size[0] * self._img_size[1] * 3
        sleep_time = 1.0 / self.fps
        captured_frames = []

        with subprocess.Popen([self.rawrgb_path, '{}'.format(self.fps)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as camera:
            while len(captured_frames) < frames:
                frame = camera.stdout.read(input_size)
                size = len(frame)

                if skip_frames > 0:
                    time.sleep(sleep_time)
                    skip_frames -= 1
                    continue

                captured_frames.append(frame)

        return frames


# vim:sw=4:ts=4:et:
