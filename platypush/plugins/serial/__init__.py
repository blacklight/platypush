import base64
import json
import serial
import threading
import time

from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


# noinspection PyBroadException
class SerialPlugin(SensorPlugin):
    """
    The serial plugin can read data from a serial device, as long as the serial
    device returns a JSON. You can use this plugin to interact for example with
    some sensors connected through an Arduino. Just make sure that the code on
    your serial device returns JSON values. If you're using an Arduino or any
    ATMega compatible device, take a look at
    https://github.com/bblanchon/ArduinoJson.
    """

    def __init__(self, device=None, baud_rate=9600, **kwargs):
        """
        :param device: Device path (e.g. ``/dev/ttyUSB0`` or ``/dev/ttyACM0``)
        :type device: str

        :param baud_rate: Serial baud rate (default: 9600)
        :type baud_rate: int
        """

        super().__init__(**kwargs)

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

            try:
                ch.decode()
            except Exception as e:
                self.logger.warning('Could not decode character: {}'.format(str(e)))
                output = bytes()

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

    def _get_serial(self, device=None, baud_rate=None, reset=False):
        if not device:
            if not self.device:
                raise RuntimeError('No device specified nor default device configured')
            device = self.device

        if baud_rate is None:
            if self.baud_rate is None:
                raise RuntimeError('No baud_rate specified nor default configured')
            baud_rate = self.baud_rate

        if self.serial:
            if not reset:
                return self.serial

            self._close_serial()

        self.serial = serial.Serial(device, baud_rate)
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
    def get_measurement(self, device=None, baud_rate=None):
        """
        Reads JSON data from the serial device and returns it as a message

        :param device: Device path (default: default configured device)
        :type device: str

        :param baud_rate: Baud rate (default: default configured baud_rate)
        :type baud_rate: int
        """

        if not device:
            if not self.device:
                raise RuntimeError('No device specified nor default device configured')
            device = self.device

        if baud_rate is None:
            if self.baud_rate is None:
                raise RuntimeError('No baud_rate specified nor default configured')
            baud_rate = self.baud_rate

        data = None

        try:
            serial_available = self.serial_lock.acquire(timeout=2)
            if serial_available:
                try:
                    ser = self._get_serial(device=device, baud_rate=baud_rate)
                except:
                    time.sleep(1)
                    ser = self._get_serial(device=device, baud_rate=baud_rate, reset=True)

                data = self._read_json(ser)

                try:
                    data = json.loads(data)
                except:
                    self.logger.warning('Invalid JSON message from {}: {}'.
                                        format(self.device, data))
            else:
                data = self.last_measurement
        finally:
            try:
                self.serial_lock.release()
            except:
                pass

        if data:
            self.last_measurement = data

        return data

    @action
    def read(self, device=None, baud_rate=None, size=None, end=None):
        """
        Reads raw data from the serial device

        :param device: Device to read (default: default configured device)
        :type device: str

        :param baud_rate: Baud rate (default: default configured baud_rate)
        :type baud_rate: int

        :param size: Number of bytes to read
        :type size: int

        :param end: End of message byte or character
        :type end: int, bytes or str
        """

        if not device:
            if not self.device:
                raise RuntimeError('No device specified nor default device configured')
            device = self.device

        if baud_rate is None:
            if self.baud_rate is None:
                raise RuntimeError('No baud_rate specified nor default configured')
            baud_rate = self.baud_rate

        if (size is None and end is None) or (size is not None and end is not None):
            raise RuntimeError('Either size or end must be specified')

        if end and isinstance(end, str) and len(end) > 1:
            raise RuntimeError('The serial end must be a single character, not a string')

        data = bytes()

        try:
            serial_available = self.serial_lock.acquire(timeout=2)
            if serial_available:
                try:
                    ser = self._get_serial(device=device, baud_rate=baud_rate)
                except:
                    time.sleep(1)
                    ser = self._get_serial(device=device, baud_rate=baud_rate, reset=True)

                if size is not None:
                    for _ in range(0, size):
                        data += ser.read()
                elif end is not None:
                    if isinstance(end, str):
                        end = end.encode()

                    ch = None
                    while ch != end:
                        ch = ser.read()

                        if ch != end:
                            data += ch
            else:
                self.logger.warning('Serial read timeout')
        finally:
            try:
                self.serial_lock.release()
            except:
                pass

        try:
            data = data.decode()
        except:
            data = base64.encodebytes(data)

        return data

    @action
    def write(self, data, device=None, baud_rate=None):
        """
        Writes data to the serial device.

        :param device: Device to write (default: default configured device)
        :type device: str

        :param baud_rate: Baud rate (default: default configured baud_rate)
        :type baud_rate: int

        :param data: Data to send to the serial device
        :type data: str, bytes or dict. If dict, it will be serialized as JSON.
        """

        if not device:
            if not self.device:
                raise RuntimeError('No device specified nor default device configured')
            device = self.device

        if baud_rate is None:
            if self.baud_rate is None:
                raise RuntimeError('No baud_rate specified nor default configured')
            baud_rate = self.baud_rate

        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode('utf-8')

        try:
            serial_available = self.serial_lock.acquire(timeout=2)
            if serial_available:
                try:
                    ser = self._get_serial(device=device, baud_rate=baud_rate)
                except:
                    time.sleep(1)
                    ser = self._get_serial(device=device, baud_rate=baud_rate, reset=True)

                self.logger.info('Writing {} to {}'.format(data, self.device))
                ser.write(data)
        finally:
            try:
                self.serial_lock.release()
            except:
                pass


# vim:sw=4:ts=4:et:
