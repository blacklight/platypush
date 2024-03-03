import multiprocessing
import threading
from queue import Empty
from typing import Dict, List, Optional

from platypush.plugins import RunnablePlugin, action
from platypush.schemas.joystick import JoystickStatusSchema

from ._inputs import DeviceManager, GamePad
from ._manager import JoystickManager


class JoystickPlugin(RunnablePlugin):
    """
    A plugin to monitor joystick events.
    """

    def __init__(self, poll_interval: float = 0.025, **kwargs):
        """
        :param poll_interval: Polling interval in seconds (default: 0.025)
        """

        super().__init__(poll_interval=poll_interval, **kwargs)
        self._dev_managers: Dict[str, JoystickManager] = {}
        self._state_queue = multiprocessing.Queue()
        self._state_monitor_thread: Optional[threading.Thread] = None

    @staticmethod
    def _key(device: GamePad) -> str:
        return device.get_char_device_path()

    def _start_manager(self, device: GamePad):
        if device in self._dev_managers:
            return

        dev_manager = JoystickManager(
            device=device,
            poll_interval=self.poll_interval,
            state_queue=self._state_queue,
        )

        dev_manager.start()
        self._dev_managers[self._key(device)] = dev_manager

    def _stop_manager(self, device: str):
        dev_manager = self._dev_managers.get(device)
        if not dev_manager:
            return

        dev_manager.stop()
        dev_manager.join(1)
        if dev_manager.is_alive():
            dev_manager.kill()

        del self._dev_managers[device]

    def _state_monitor(self):
        while not self.should_stop():
            try:
                state = self._state_queue.get(timeout=0.5)
                device = state.device
                if device not in self._dev_managers:
                    continue

                self._dev_managers[device].state = state.state
            except Empty:
                pass
            except Exception as e:
                self.logger.exception(e)

    def main(self):
        if not self._state_monitor_thread:
            self._state_monitor_thread = threading.Thread(
                target=self._state_monitor, daemon=True
            )
            self._state_monitor_thread.start()

        while not self.should_stop():
            try:
                devices = DeviceManager().gamepads
                missing_devices_keys = set(self._dev_managers.keys()) - {
                    self._key(dev) for dev in devices
                }

                new_devices = {
                    dev for dev in devices if self._key(dev) not in self._dev_managers
                }

                # Stop managers for devices that are no longer connected
                for dev in missing_devices_keys:
                    self._stop_manager(dev)

                # Start managers for new devices
                for dev in new_devices:
                    self._start_manager(dev)
            except Exception as e:
                self.logger.exception(e)
            finally:
                self.wait_stop(max(0.5, min(10, (self.poll_interval or 0) * 10)))

    def stop(self):
        for dev in list(self._dev_managers.keys()):
            self._stop_manager(dev)

        super().stop()

    @action
    def status(self) -> List[dict]:
        """
        :return: .. schema:: joystick.JoystickStatusSchema(many=True)
        """
        return JoystickStatusSchema().dump(
            [
                {
                    'device': dev.device,
                    'state': dev.state,
                }
                for dev in self._dev_managers.values()
            ],
            many=True,
        )


# vim:sw=4:ts=4:et:
