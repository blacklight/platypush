import time

from platypush.backend import Backend
from platypush.message.event.joystick import JoystickEvent


class JoystickBackend(Backend):
    """
    This backend will listen for events from a joystick device and post a
    JoystickEvent whenever a new event is captured.

    Triggers:

        * :class:`platypush.message.event.joystick.JoystickEvent` when a new joystick event is received

    Requires:

        * **inputs** (``pip install inputs``)
    """

    def __init__(self, device, *args, **kwargs):
        """
        :param device: Path to the joystick device (e.g. `/dev/input/js0`)
        :type device_name: str
        """

        super().__init__(*args, **kwargs)

        self.device = device

    def run(self):
        import inputs

        super().run()
        self.logger.info('Initialized joystick backend on device {}'.format(self.device))

        while not self.should_stop():
            try:
                events = inputs.get_gamepad()
                for event in events:
                    if event.ev_type == 'Key' or event.ev_type == 'Absolute':
                        self.bus.post(JoystickEvent(code=event.code, state=event.state))
            except Exception as e:
                self.logger.exception(e)
                time.sleep(1)


# vim:sw=4:ts=4:et:
