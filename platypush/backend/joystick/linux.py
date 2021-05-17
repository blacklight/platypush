import array
import struct
import time
from fcntl import ioctl
from typing import IO

from platypush.backend import Backend
from platypush.message.event.joystick import JoystickConnectedEvent, JoystickDisconnectedEvent, \
    JoystickButtonPressedEvent, JoystickButtonReleasedEvent, JoystickAxisEvent


class JoystickLinuxBackend(Backend):
    """
    This backend intercepts events from joystick devices through the native Linux API implementation.

    It is loosely based on https://gist.github.com/rdb/8864666, which itself uses the
    `Linux kernel joystick API <https://www.kernel.org/doc/Documentation/input/joystick-api.txt>`_ to interact with
    the devices.

    Triggers:

        * :class:`platypush.message.event.joystick.JoystickConnectedEvent` when the joystick is connected.
        * :class:`platypush.message.event.joystick.JoystickDisconnectedEvent` when the joystick is disconnected.
        * :class:`platypush.message.event.joystick.JoystickButtonPressedEvent` when a joystick button is pressed.
        * :class:`platypush.message.event.joystick.JoystickButtonReleasedEvent` when a joystick button is released.
        * :class:`platypush.message.event.joystick.JoystickAxisEvent` when an axis value of the joystick changes.

    """

    # These constants were borrowed from linux/input.h
    axis_names = {
        0x00: 'x',
        0x01: 'y',
        0x02: 'z',
        0x03: 'rx',
        0x04: 'ry',
        0x05: 'rz',
        0x06: 'throttle',
        0x07: 'rudder',
        0x08: 'wheel',
        0x09: 'gas',
        0x0a: 'brake',
        0x10: 'hat0x',
        0x11: 'hat0y',
        0x12: 'hat1x',
        0x13: 'hat1y',
        0x14: 'hat2x',
        0x15: 'hat2y',
        0x16: 'hat3x',
        0x17: 'hat3y',
        0x18: 'pressure',
        0x19: 'distance',
        0x1a: 'tilt_x',
        0x1b: 'tilt_y',
        0x1c: 'tool_width',
        0x20: 'volume',
        0x28: 'misc',
    }

    button_names = {
        0x120: 'trigger',
        0x121: 'thumb',
        0x122: 'thumb2',
        0x123: 'top',
        0x124: 'top2',
        0x125: 'pinkie',
        0x126: 'base',
        0x127: 'base2',
        0x128: 'base3',
        0x129: 'base4',
        0x12a: 'base5',
        0x12b: 'base6',
        0x12f: 'dead',
        0x130: 'a',
        0x131: 'b',
        0x132: 'c',
        0x133: 'x',
        0x134: 'y',
        0x135: 'z',
        0x136: 'tl',
        0x137: 'tr',
        0x138: 'tl2',
        0x139: 'tr2',
        0x13a: 'select',
        0x13b: 'start',
        0x13c: 'mode',
        0x13d: 'thumbl',
        0x13e: 'thumbr',
        0x220: 'dpad_up',
        0x221: 'dpad_down',
        0x222: 'dpad_left',
        0x223: 'dpad_right',
        # XBox 360 controller uses these codes.
        0x2c0: 'dpad_left',
        0x2c1: 'dpad_right',
        0x2c2: 'dpad_up',
        0x2c3: 'dpad_down',
    }

    def __init__(self, device: str = '/dev/input/js0', *args, **kwargs):
        """
        :param device: Joystick device to monitor (default: ``/dev/input/js0``).
        """
        super().__init__(*args, **kwargs)
        self.device = device
        self._axis_states = {}
        self._button_states = {}
        self._axis_map = []
        self._button_map = []

    def _init_joystick(self, dev: IO):
        # Get the device name.
        buf = array.array('B', [0] * 64)
        ioctl(dev, 0x80006a13 + (0x10000 * len(buf)), buf)  # JSIOCGNAME(len)
        js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(dev, 0x80016a11, buf)  # JSIOCGAXES
        num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(dev, 0x80016a12, buf)  # JSIOCGBUTTONS
        num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(dev, 0x80406a32, buf)  # JSIOCGAXMAP

        for axis in buf[:num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self._axis_map.append(axis_name)
            self._axis_states[axis_name] = 0.0

        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(dev, 0x80406a34, buf)  # JSIOCGBTNMAP

        for btn in buf[:num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self._button_map.append(btn_name)
            self._button_states[btn_name] = 0

        self.bus.post(JoystickConnectedEvent(device=self.device, name=js_name, axes=self._axis_map,
                                             buttons=self._button_map))

    def run(self):
        super().run()
        self.logger.info(f'Opening {self.device}...')

        while not self.should_stop():
            # Open the joystick device.
            try:
                jsdev = open(self.device, 'rb')
                self._init_joystick(jsdev)
            except Exception as e:
                self.logger.debug(f'Joystick device on {self.device} not available: {e}')
                time.sleep(5)
                continue

            # Joystick event loop
            while not self.should_stop():
                try:
                    evbuf = jsdev.read(8)
                    if evbuf:
                        _, value, evt_type, number = struct.unpack('IhBB', evbuf)

                        if evt_type & 0x80:  # Initial state notification
                            continue

                        if evt_type & 0x01:
                            button = self._button_map[number]
                            if button:
                                self._button_states[button] = value
                                evt_class = JoystickButtonPressedEvent if value else JoystickButtonReleasedEvent
                                # noinspection PyTypeChecker
                                self.bus.post(evt_class(device=self.device, button=button))

                        if evt_type & 0x02:
                            axis = self._axis_map[number]
                            if axis:
                                fvalue = value / 32767.0
                                self._axis_states[axis] = fvalue
                                # noinspection PyTypeChecker
                                self.bus.post(JoystickAxisEvent(device=self.device, axis=axis, value=fvalue))
                except OSError as e:
                    self.logger.warning(f'Connection to {self.device} lost: {e}')
                    self.bus.post(JoystickDisconnectedEvent(device=self.device))
                    break
