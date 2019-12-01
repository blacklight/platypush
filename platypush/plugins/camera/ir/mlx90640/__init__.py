import base64
import io
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

    Requires:

        * **mlx90640-library** installation (see instructions above)
        * **PIL** image library (``pip install Pillow``)
    """

    _img_size = (32, 24)
    _rotate_values = {}

    def __init__(self, fps=16, skip_frames=2, scale_factor=1, rotate=0, rawrgb_path=None, **kwargs):
        """
        :param fps: Frames per seconds (default: 16)
        :param skip_frames: Number of frames to be skipped on sensor initialization/warmup (default: 2)
        :param scale_factor: The camera outputs 24x32 pixels artifacts. Use scale_factor to scale them up to a larger
            image (default: 1)
        :param rotate: Rotation angle in degrees (default: 0)
        :param rawrgb_path: Specify it if the rawrgb executable compiled from
            https://github.com/pimoroni/mlx90640-library is in another folder than
            `<directory of this file>/lib/examples`.
        """
        from PIL import Image
        super().__init__(**kwargs)

        self._rotate_values = {
            90: Image.ROTATE_90,
            180: Image.ROTATE_180,
            270: Image.ROTATE_270,
        }

        if not rawrgb_path:
            rawrgb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'examples', 'rawrgb')
        rawrgb_path = os.path.abspath(os.path.expanduser(rawrgb_path))

        assert fps > 0
        assert skip_frames >= 0
        assert os.path.isfile(rawrgb_path)

        self.fps = fps
        self.rotate = rotate
        self.skip_frames = skip_frames
        self.scale_factor = scale_factor
        self.rawrgb_path = rawrgb_path
        self._capture_proc = None

    def _is_capture_proc_running(self):
        return self._capture_proc is not None and self._capture_proc.poll() is None

    def _get_capture_proc(self, fps):
        if not self._is_capture_proc_running():
            fps = fps or self.fps
            self._capture_proc = subprocess.Popen([self.rawrgb_path, '{}'.format(fps)], stdin=subprocess.PIPE,
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return self._capture_proc

    # noinspection PyShadowingBuiltins
    @action
    def capture(self, output_file=None, frames=1, grayscale=False, fps=None, skip_frames=None, scale_factor=None,
                rotate=None, format='jpeg'):
        """
        Capture one or multiple frames and return them as raw RGB

        :param output_file: Can be either the path to a single image file or a format string
            (e.g. 'snapshots/image-{:04d}') in case of multiple frames. If not set the function will return a list of
            base64 encoded representations of the raw RGB frames, otherwise the list of captured files.
        :type output_file: str

        :param frames: Number of frames to be captured (default: 1). If None the capture process will proceed until
            `stop` is called.
        :type frames: int

        :param grayscale: Save the image as grayscale - black pixels will be colder, white pixels warmer
            (default: False)
        :type grayscale: bool

        :param fps: If set it overrides the fps parameter specified on the object (default: None)
        :type fps: int

        :param skip_frames: If set it overrides the skip_frames parameter specified on the object (default: None)
        :type skip_frames: int

        :param scale_factor: If set it overrides the scale_factor parameter specified on the object (default: None)
        :type scale_factor: float

        :param rotate: If set it overrides the rotate parameter specified on the object (default: None)
        :type rotate: int

        :param format: Output image format if output_file is not specified (default: jpeg).
            It can be jpg, png, gif or any format supported by PIL
        :type format: str

        :returns: list[str]. Each item is a base64 encoded representation of a frame in the specified format if
            output_file is not set, otherwise a list with the captured image files will be returned.
        """

        from PIL import Image
        fps = self.fps if fps is None else fps
        skip_frames = self.skip_frames if skip_frames is None else skip_frames
        scale_factor = self.scale_factor if scale_factor is None else scale_factor
        rotate = self._rotate_values.get(self.rotate if rotate is None else rotate, 0)

        size = self._img_size
        sleep_time = 1.0 / self.fps
        captured_frames = []
        n_captured_frames = 0
        files = set()
        camera = self._get_capture_proc(fps)

        while (frames is not None and n_captured_frames < frames) or (
                frames is None and self._is_capture_proc_running()):
            frame = camera.stdout.read(size[0] * size[1] * 3)

            if skip_frames > 0:
                time.sleep(sleep_time)
                skip_frames -= 1
                continue

            image = Image.frombytes('RGB', size, frame)

            if grayscale:
                image = self._convert_to_grayscale(image)
            if scale_factor != 1:
                size = tuple(i * scale_factor for i in size)
                image = image.resize(size, Image.ANTIALIAS)
            if rotate:
                image = image.transpose(rotate)

            if not output_file:
                temp = io.BytesIO()
                image.save(temp, format=format)
                frame = base64.encodebytes(temp.getvalue()).decode()
                captured_frames.append(frame)
            else:
                image_file = os.path.abspath(os.path.expanduser(output_file.format(n_captured_frames)))
                image.save(image_file)
                files.add(image_file)

            n_captured_frames += 1
            time.sleep(sleep_time)

        self.stop()
        return sorted([f for f in files]) if output_file else captured_frames

    @staticmethod
    def _convert_to_grayscale(image):
        from PIL import Image
        new_image = Image.new('L', image.size)

        for i in range(0, image.size[0]):
            for j in range(0, image.size[1]):
                r, g, b = image.getpixel((i, j))
                value = int(2.0 * r - 0.5 * g - 1.5 * b)

                if value > 255:
                    value = 255
                if value < 0:
                    value = 0

                new_image.putpixel((i, j), value)

        return new_image

    @action
    def stop(self):
        """
        Stop an ongoing capture session
        """
        if not self._is_capture_proc_running():
            return

        self._capture_proc.terminate()
        self._capture_proc.kill()
        self._capture_proc.wait()
        self._capture_proc = None

# vim:sw=4:ts=4:et:
