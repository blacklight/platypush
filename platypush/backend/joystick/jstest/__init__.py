import json
import os
import re
import subprocess
import time
from typing import Optional, List

from platypush.backend import Backend
from platypush.message.event.joystick import JoystickConnectedEvent, JoystickDisconnectedEvent, JoystickStateEvent, \
    JoystickButtonPressedEvent, JoystickButtonReleasedEvent, JoystickAxisEvent


class JoystickState:
    def __init__(self, axes: List[int], buttons: List[bool]):
        self.axes = axes
        self.buttons = buttons

    def __str__(self):
        return json.dumps(self.__dict__)

    def __eq__(self, obj):
        return obj.axes == self.axes and obj.buttons == self.buttons

    def __sub__(self, obj) -> dict:
        if len(obj.axes) < len(self.axes) or len(obj.buttons) < len(self.buttons):
            return {}

        diff = {
            'axes': {
                axis: obj.axes[axis]
                for axis in range(len(self.axes))
                if self.axes[axis] != obj.axes[axis]
            },
            'buttons': {
                button: obj.buttons[button]
                for button in range(len(self.buttons))
                if self.buttons[button] != obj.buttons[button]
            },
        }

        return {
            k: v for k, v in diff.items() if v
        }


class JoystickJstestBackend(Backend):
    """
    This backend can be used to intercept events from a joystick device if the device does not work with the standard
    :class:`platypush.backend.joystick.JoystickBackend` backend (this may especially happen with some Bluetooth
    joysticks that don't support the ``ioctl`` requests used by ``inputs``).

    This backend only works on Linux and it requires the ``joystick`` package to be installed.

    **NOTE**: This backend can be quite slow, since it has to run another program (``jstest``) and parse its output.
    Consider it as a last resort if your joystick works with neither :class:`platypush.backend.joystick.JoystickBackend`
    nor :class:`platypush.backend.joystick.JoystickLinuxBackend`.

    Instructions on Debian-based distros::

        # apt-get install joystick

    Instructions on Arch-based distros::

        # pacman -S joyutils

    To test if your joystick is compatible, connect it to your device, check for its path (usually under
    ``/dev/input/js*``) and run::

        $ jstest /dev/input/js[n]

    Triggers:

        * :class:`platypush.message.event.joystick.JoystickConnectedEvent` when the joystick is connected.
        * :class:`platypush.message.event.joystick.JoystickDisconnectedEvent` when the joystick is disconnected.
        * :class:`platypush.message.event.joystick.JoystickStateEvent` when the state of the joystick (i.e. some of its
            axes or buttons values) changes.
        * :class:`platypush.message.event.joystick.JoystickButtonPressedEvent` when a joystick button is pressed.
        * :class:`platypush.message.event.joystick.JoystickButtonReleasedEvent` when a joystick button is released.
        * :class:`platypush.message.event.joystick.JoystickAxisEvent` when an axis value of the joystick changes.

    """

    js_axes_regex = re.compile(r'Axes:\s+(((\d+):\s*([\-\d]+)\s*)+)')
    js_buttons_regex = re.compile(r'Buttons:\s+(((\d+):\s*(on|off)\s*)+)')
    js_axis_regex = re.compile(r'^\s*(\d+):\s*([\-\d]+)\s*(.*)')
    js_button_regex = re.compile(r'^\s*(\d+):\s*(on|off)\s*(.*)')

    def __init__(self,
                 device: str = '/dev/input/js0',
                 jstest_path: str = '/usr/bin/jstest',
                 **kwargs):
        """
        :param device: Path to the joystick device (default: ``/dev/input/js0``).
        :param jstest_path: Path to the ``jstest`` executable that comes with the ``joystick`` system package
            (default: ``/usr/bin/jstest``).
        """
        super().__init__(device=device, **kwargs)

        self.device = device
        self.jstest_path = jstest_path
        self._process: Optional[subprocess.Popen] = None
        self._state: Optional[JoystickState] = None

    def _wait_ready(self):
        self.logger.info(f'Waiting for joystick device on {self.device}')

        while not self.should_stop():
            if not os.path.exists(self.device):
                time.sleep(1)

            try:
                with open(self.device, 'rb'):
                    break
            except Exception as e:
                self.logger.debug(e)
                time.sleep(0.1)
                continue

        self.bus.post(JoystickConnectedEvent(device=self.device))

    def _read_states(self):
        while not self.should_stop():
            yield self._get_state()

    def _get_state(self) -> JoystickState:
        axes = []
        buttons = []
        line = ''

        while os.path.exists(self.device) and not self.should_stop():
            ch = self._process.stdout.read(1).decode()
            if not ch:
                continue

            if ch in ['\r', '\n']:
                line = ''
                continue

            line += ch
            if line.endswith('Axes:  '):
                break

        while os.path.exists(self.device) and not self.should_stop() and len(axes) < len(self._state.axes):
            ch = ' '
            while ch == ' ':
                ch = self._process.stdout.read(1).decode()

            self._process.stdout.read(len(f'{len(axes)}'))
            value = ''

            while os.path.exists(self.device) and not self.should_stop():
                ch = self._process.stdout.read(1).decode()
                if ch == ' ':
                    if not value:
                        continue
                    break

                if ch == ':':
                    break

                value += ch

            if value:
                axes.append(int(value))

        line = ''

        while os.path.exists(self.device) and not self.should_stop():
            ch = self._process.stdout.read(1).decode()
            if not ch:
                continue

            line += ch
            if line.endswith('Buttons:  '):
                break

        while os.path.exists(self.device) and not self.should_stop() and len(buttons) < len(self._state.buttons):
            ch = ' '
            while ch == ' ':
                ch = self._process.stdout.read(1).decode()

            self._process.stdout.read(len(f'{len(buttons)}'))
            value = ''

            while os.path.exists(self.device) and not self.should_stop():
                ch = self._process.stdout.read(1).decode()
                if ch == ' ':
                    continue

                value += ch
                if value in ['on', 'off']:
                    buttons.append(value == 'on')
                    break

        return JoystickState(axes=axes, buttons=buttons)

    def _initialize(self):
        while self._process.poll() is None and \
                os.path.exists(self.device) and \
                not self.should_stop() and \
                not self._state:
            line = b''
            ch = None

            while ch not in [b'\r', b'\n']:
                ch = self._process.stdout.read(1)
                line += ch

            line = line.decode().strip()
            if not (line and line.startswith('Axes:')):
                continue

            re_axes = self.js_axes_regex.search(line)
            re_buttons = self.js_buttons_regex.search(line)

            if not (re_axes and re_buttons):
                return

            state = {
                'axes': [],
                'buttons': [],
            }

            axes = re_axes.group(1)
            while axes:
                m = self.js_axis_regex.search(axes)
                state['axes'].append(int(m.group(2)))
                axes = m.group(3)

            buttons = re_buttons.group(1)
            while buttons:
                m = self.js_button_regex.search(buttons)
                state['buttons'].append(m.group(2) == 'on')
                buttons = m.group(3)

            self._state = JoystickState(**state)

    def _process_state(self, state: JoystickState):
        diff = self._state - state
        if not diff:
            return

        self.bus.post(JoystickStateEvent(device=self.device, **state.__dict__))

        for button, pressed in diff.get('buttons', {}).items():
            evt_class = JoystickButtonPressedEvent if pressed else JoystickButtonReleasedEvent
            self.bus.post(evt_class(device=self.device, button=button))

        for axis, value in diff.get('axes', {}).items():
            self.bus.post(JoystickAxisEvent(device=self.device, axis=axis, value=value))

        self._state = state

    def run(self):
        super().run()

        try:
            while not self.should_stop():
                self._wait_ready()

                with subprocess.Popen(
                        [self.jstest_path, '--normal', self.device],
                        stdout=subprocess.PIPE) as self._process:
                    self.logger.info('Device opened')
                    self._initialize()

                    if self._process.poll() is not None:
                        break

                    for state in self._read_states():
                        if self._process.poll() is not None or not os.path.exists(self.device):
                            self.logger.warning(f'Connection to {self.device} lost')
                            self.bus.post(JoystickDisconnectedEvent(self.device))
                            break

                        self._process_state(state)
        finally:
            self._process = None


# vim:sw=4:ts=4:et:
