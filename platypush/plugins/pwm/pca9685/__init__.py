import time
from typing import Optional, Dict, Iterable

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

    Requires:

        - **adafruit-circuitpython-pca9685** (``pip install adafruit-circuitpython-pca9685``)

    """

    def __init__(self, frequency: float, min_duty_cycle: int = 0, max_duty_cycle: int = 0xffff, channels: Iterable[int] = tuple(range(16)), **kwargs):
        """
        :param frequency: Default PWM frequency to use for the driver, in Hz.
        :param min_duty_cycle: Minimum PWM duty cycle (you can often find it in the documentation of your device).
            Default: 0.
        :param max_duty_cycle: Maximum PWM duty cycle (you can often find it in the documentation of your device).
            Default: 0xffff.
        :param Indices of the default channels to be controlled (default: all channels,
            i.e. ``[0-15]``).
        """
        super().__init__(**kwargs)
        self.frequency = frequency
        self.min_duty_cycle = min_duty_cycle
        self.max_duty_cycle = max_duty_cycle
        self.channels = channels
        self._pca = None

    @action
    def write(self, value: Optional[int] = None, channels: Optional[Dict[int, float]] = None,
              frequency: Optional[float] = None, step: Optional[int] = None,
              step_duration: Optional[float] = None):
        """
        Send PWM values to the channels.

        :param value: Send the value to all the channels (or to all the configured default channels).
            ``value`` and ``channels`` are mutually exclusive.
        :param channels: Map of the values to be written, as a ``channel_index -> value``, where value is a real number.
            ``value`` and ``channels`` are mutually exclusive.
        :param frequency: Override default frequency.
        :param step: If set, then the PWM duty cycle will be increased/decreased by
            this much per cycle (i.e. 1/frequency). This is useful when dealing with PWM
            devices that require smooth transitions, arming sequences or ramping signals.
            If None (default) then the new PWM values will be directly written with no
            ramping logic.
        :param step_duration: If step is configured, this parameter identifies how long
            each step should last (default: ``1/frequency``).
        """
        import busio
        from board import SCL, SDA
        from adafruit_pca9685 import PCA9685

        if value is not None:
            assert self.channels, 'No default channels configured'
            channels = {i: value for i in self.channels}

        assert channels, 'Both value and channels are missing'

        i2c_bus = busio.I2C(SCL, SDA)
        pca = self._pca = self._pca or PCA9685(i2c_bus)
        pca.frequency = frequency or self.frequency
        step_duration = step_duration or 1/pca.frequency

        if not step:
            for i, val in channels.items():
                pca.channels[i].duty_cycle = val
            return

        done = False
        cur_values = {
            i: channel.duty_cycle
            for i, channel in enumerate(pca.channels)
        }

        while not done:
            done = True

            for i, val in channels.items():
                if val == cur_values[i]:
                    continue

                done = False
                val = min(cur_values[i] + step, val, self.max_duty_cycle) \
                        if val > pca.channels[i].duty_cycle \
                        else max(cur_values[i] - step, val, self.min_duty_cycle)

                pca.channels[i].duty_cycle = cur_values[i] = val

            time.sleep(step_duration)

    @action
    def get_channels(self) -> Dict[int, float]:
        """
        Get the current duty cycle value of the channels.

        :return: A map in the format ``channel_index -> value``, where ``value`` is the duty cycle of the associated
            channel, as a percentage value between 0 and 1.
        """
        if not self._pca:
            return {i: 0 for i in self.channels}

        return {
            i: channel.duty_cycle
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

