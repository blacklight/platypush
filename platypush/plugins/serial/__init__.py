import json
import serial
import threading
import time

from platypush.plugins import Plugin, action
from platypush.plugins.gpio.sensor import GpioSensorPlugin


class SerialPlugin(GpioSensorPlugin):
    """
    The serial plugin can read data from a serial device, as long as the serial
    device returns a JSON. You can use this plugin to interact for example with
    some sensors connected through an Arduino. Just make sure that the code on
    your serial device returns JSON values. If you're using an Arduino or any
    ATMega compatible device, take a look at
    https://github.com/bblanchon/ArduinoJson.
    """

    def __init__(self, device, baud_rate=9600, *args, **kwargs):
        """
        :param device: Device path (e.g. ``/dev/ttyUSB0`` or ``/dev/ttyACM0``)
        :type device: str

        :param baud_rate: Serial baud rate (default: 9600)
        :type baud_rate: int
        """

        super().__init__(*args, **kwargs)

        self.device = device
        self.baud_rate = baud_rate
        self.serial = None
        self.serial_lock = threading.Lock()
        self.last_measurement = None


    def _read_json(self, serial_port):
        n_brackets = 0
        is_escaped_ch = False
        parse_start = False
        output = bytes()

        while True:
            ch = serial_port.read()
            if not ch:
                break

            if ch.decode() == '{' and not is_escaped_ch:
                parse_start = True
                n_brackets += 1

            if not parse_start:
                continue

            output += ch

            if ch.decode() == '}' and not is_escaped_ch:
                n_brackets -= 1
                if n_brackets == 0:
                    break

            is_escaped_ch = ch.decode() == '\\'

        return output.decode().strip()

    def _get_serial(self, reset=False):
        if self.serial:
            if not reset:
                return self.serial

            self._close_serial()

        self.serial = serial.Serial(self.device, self.baud_rate)
        return self.serial

    def _close_serial(self):
        if self.serial:
            try:
                self.serial.close()
                self.serial = None
            except Exception as e:
                self.logger.warning('Error while closing serial communication: {}')
                self.logger.exception(e)

    @action
    def get_measurement(self):
        """
        Reads JSON data from the serial device and returns it as a message
        """

        data = None

        try:
            serial_available = self.serial_lock.acquire(timeout=2)
            if serial_available:
                try:
                    ser = self._get_serial()
                except:
                    time.sleep(1)
                    ser = self._get_serial(reset=True)

                data = self._read_json(ser)

                try:
                    data = json.loads(data)
                except:
                    self.logger.warning('Invalid JSON message from {}: {}'.
                                        format(self.device, data))
            else:
                data = self.last_measurement
        finally:
            self.serial_lock.release()

        if data:
            self.last_measurement = data

        return data


# vim:sw=4:ts=4:et:

