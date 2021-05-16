import time
from typing import Optional, Dict

from platypush.plugins import Plugin, action


class PwmPca9685Plugin(Plugin):
    """
    This plugin interacts with an `Adafruit PCA9685 <https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all>`_
    circuit, a 16-channel PWM servo driver. You can leverage this plugin to control servos and motors through Platypush.

    Note that the driver for PCA9685 has been written for CircuitPython, and in order to use it on a Raspberry Pi or
    similar devices you need to
    `follow these steps <https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all#python-circuitpython>`_::

        # pip3 install --upgrade adafruit-python-shell
        $ wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
        # python3 raspi-blinka.py

    Then reboot and check that the following virtual devices are available::

        - /dev/i2c-1
        - /dev/spidev0.0
        - /dev/spidev0.1

    Finally, install the PCA9685 drivers::

        # pip3 install --upgrade adafruit-circuitpython-pca9685

    This plugin works with a PCA9685 circuit connected to the Platypush host over I2C interface.
    """

    MIN_PWM_VALUE = 0
    MAX_PWM_VALUE = 0xffff
    N_CHANNELS = 16

    def __init__(self, frequency: float, step_value: float = 0.1, step_duration: float = 0.05, **kwargs):
        """
        :param frequency: Default PWM frequency to use for the driver, in Hz.
        :param step_value: How much each channel value should be increased/decreased on each step.
        :param step_duration: Length of each step transient when writing PWM values (default: 0.05 seconds).
        """
        super().__init__(**kwargs)
        self.frequency = frequency
        self.step_value = step_value
        self.step_duration = step_duration
        self._pca = None

    @staticmethod
    def _convert_percent_to_duty_cycle(value: float) -> int:
        """
        Convert a duty cycle percentage value to a PCA9685 value between 0 and ``0xffff``.

        :param value: Duty cycle value, between 0 and 1.
        :return: Duty cycle 16-bit value, between 0 and ``0xffff``.
        """
        return int(value * 65535)

    @staticmethod
    def _convert_duty_cycle_to_percent(value: int) -> float:
        """
        Convert a PCA9685 duty cycle value value to a percentage value.

        :param value: Duty cycle 16-bit value, between 0 and ``0xffff``.
        :return: Duty cycle percentage, between 0 and 1.
        """
        return value / 65535

    @action
    def execute(self, channels: Dict[int, float], frequency: Optional[float] = None, step_value: Optional[float] = None,
                step_duration: Optional[float] = None):
        """
        Send PWM values to the specified channels.

        :param channels: Map of the values to be written, as ``channel_index -> value``, where value is a real number
            between 0.0 (minimum duty cycle) and 1.0 (maximum duty cycle).
        :param frequency: Override default frequency.
        :param step_value: Override default step value.
        :param step_duration: Override default step duration.
        """
        import busio
        from board import SCL, SDA
        from adafruit_pca9685 import PCA9685

        values = {k: self._convert_percent_to_duty_cycle(v) for k, v in channels.items()}
        step_value = self._convert_percent_to_duty_cycle(step_value if step_value is not None else self.step_value)
        step_duration = step_duration if step_duration is not None else self.step_duration
        i2c_bus = busio.I2C(SCL, SDA)
        pca = self._pca or PCA9685(i2c_bus)
        pca.frequency = frequency or self.frequency
        self._pca = pca
        done = False

        while not done:
            done = True

            for channel, value in values.items():
                if value == pca.channels[channel].duty_cycle:
                    continue

                done = False
                if value > pca.channels[channel].duty_cycle:
                    pca.channels[channel].duty_cycle = min(pca.channels[channel].duty_cycle + step_value,
                                                           self.MAX_PWM_VALUE)
                else:
                    pca.channels[channel].duty_cycle = max(pca.channels[channel].duty_cycle - step_value,
                                                           self.MIN_PWM_VALUE)

            time.sleep(step_duration)

    @action
    def get_channels(self) -> Dict[int, float]:
        """
        Get the current duty cycle value of the channels.

        :return: A map in the format ``channel_index -> value``, where ``value`` is the duty cycle of the associated
            channel, as a percentage value between 0 and 1.
        """
        if not self._pca:
            return {i: 0 for i in range(self.N_CHANNELS)}

        return {
            i: self._convert_duty_cycle_to_percent(channel.duty_cycle)
            for i, channel in enumerate(self._pca.channels)
        }

    @action
    def deinit(self):
        """
        De-initialize the PCA9685 if it was previously initialized.
        """
        if not self._pca:
            self.logger.warning('The PCA9685 driver is not initialized')
            return

        self._pca.deinit()
        self._pca = None

    @action
    def reset(self):
        """
        Reset the PCA9685 (set all the channels to zero).
        """
        if not self._pca:
            self.logger.warning('The PCA9685 driver is not initialized')
            return

        self._pca.reset()
