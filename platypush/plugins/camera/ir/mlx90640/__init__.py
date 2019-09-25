import base64
import math
import os
import subprocess
import time

from PIL import Image, ImageCms

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

    Requires:

        * **mlx90640-library** installation (see instructions above)
        * **PIL** image library (``pip install Pillow``)
    """

    _img_size = (24, 32)

    def __init__(self, fps=16, skip_frames=2, scale_factor=10, rotate=0, rawrgb_path=None, **kwargs):
        """
        :param fps: Frames per seconds (default: 16)
        :param skip_frames: Number of frames to be skipped on sensor initialization/warmup (default: 2)
        :param scale_factor: The camera outputs 24x32 pixels artifacts. Use scale_factor to scale them up to a larger image (default: 10)
        :param rotate: Rotation angle in degrees (default: 0)
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
        self.rotate = rotate
        self.skip_frames = skip_frames
        self.scale_factor = scale_factor
        self.rawrgb_path = rawrgb_path

    @action
    def capture(self, frames=1, fps=None, skip_frames=None):
        """
        Capture one or multiple frames and return them as raw RGB

        :param frames: Number of frames to be captured (default: 1)
        :param fps: If set it overrides the fps parameter specified on the object (default: None)
        :param skip_frames: If set it overrides the skip_frames parameter specified on the object (default: None)
        :returns: list[str]. Each item is a base64 encoded raw RGB representation of a frame
        """

        if fps is None:
            fps = self.fps

        if skip_frames is None:
            skip_frames = self.skip_frames

        input_size = self._img_size[0] * self._img_size[1] * 3
        sleep_time = 1.0 / self.fps
        captured_frames = []

        with subprocess.Popen([self.rawrgb_path, '{}'.format(self.fps)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as camera:
            while len(captured_frames) < frames:
                frame = camera.stdout.read(input_size)

                if skip_frames > 0:
                    time.sleep(sleep_time)
                    skip_frames -= 1
                    continue

                frame = base64.encodebytes(frame).decode()
                captured_frames.append(frame)
                time.sleep(sleep_time)

            camera.terminate()

        return captured_frames

    @action
    def capture_to_file(self, output_image, frames=1, grayscale=False, fps=None, skip_frames=None, scale_factor=None, rotate=None):
        """
        Capture one or multiple frames to one or multiple image files.

        :param output_image: Can be either the path to a single image file or a format string (e.g. 'snapshots/image-{:04d}') in case of multiple frames
        :param fps: If set it overrides the fps parameter specified on the object (default: None)
        :param frames: Number of frames to be captured (default: 1)
        :param grayscale: Save the image as grayscale - black pixels will be colder, white pixels warmer (default: False)
        :param skip_frames: If set it overrides the skip_frames parameter specified on the object (default: None)
        :param scale_factor: If set it overrides the scale_factor parameter specified on the object (default: None)
        :param rotate: If set it overrides the rotate parameter specified on the object (default: None)
        :returns: list[str] containing the saved image file names
        """

        if scale_factor is None:
            scale_factor = self.scale_factor

        if rotate is None:
            rotate = self.rotate

        files = []

        for i in range(0, frames):
            encoded_frame = self.capture(frames=1, fps=fps, skip_frames=skip_frames).output[0]
            frame = base64.decodebytes(encoded_frame.encode())
            size = (self._img_size[1], self._img_size[0])
            image = Image.frombytes('RGB', size, frame)
            new_image = Image.new('L', image.size)

            if grayscale:
                for i in range(0, image.size[0]):
                    for j in range(0, image.size[1]):
                        r, g, b = image.getpixel((i, j))
                        value = int(2.0*r - 0.5*g - 1.5*b)

                        if value > 255:
                            value = 255
                        if value < 0:
                            value = 0

                        new_image.putpixel((i, j), value)

                image = new_image

            if rotate:
                image = image.rotate(rotate)

            if scale_factor != 1:
                size = tuple(i*scale_factor for i in size)
                image = image.resize(size, Image.ANTIALIAS)

            filename = os.path.abspath(os.path.expanduser(output_image.format(i)))
            image.save(filename)
            files.append(filename)

        return files


# vim:sw=4:ts=4:et:
