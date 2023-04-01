import base64
from collections import namedtuple
import json
from typing import Dict, List, Optional, Union
import threading
from typing_extensions import override

from serial import Serial

from platypush.common.sensors import Numeric
from platypush.entities.devices import Device
from platypush.entities.sensors import RawSensor, NumericSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin
from platypush.utils import get_lock

_DeviceAndRate = namedtuple('_DeviceAndRate', ['device', 'baud_rate'])


class SerialPlugin(SensorPlugin):
    """
    The serial plugin can read data from a serial device.

    If the device returns a JSON string, then that string will be parsed for
    individual values. For example:

        .. code-block:: json

            {"temperature": 25.0, "humidity": 15.0}

    If the serial device returns such a value, then ``temperature`` and
    ``humidity`` will be parsed as separate entities with the same names as the
    keys provided on the payload.

    The JSON option is a good choice if you have an Arduino/ESP-like device
    whose code you can control, as it allows to easily send data to Platypush
    in a simple key-value format. The use-case would be that of an Arduino/ESP
    device that pushes data on the wire, and this integration would then listen
    for updates.

    Alternatively, you can also use this integration in a more traditional way
    through the :meth:`.read` and :meth:`.write` methods to read and write data
    to the device. In such a case, you may want to disable the "smart polling"
    by setting ``enable_polling`` to ``False`` in the configuration.

    If you want an out-of-the-box solution with a Firmata-compatible firmware,
    you may consider using the :class:`platypush.plugin.arduino.ArduinoPlugin`
    instead.

    Note that device paths on Linux may be subject to change. If you want to
    create static naming associations for your devices (e.g. make sure that
    your Arduino will always be symlinked to ``/dev/arduino`` instead of
    ``/dev/ttyUSB<n>``), you may consider creating `static mappings through
    udev
    <https://dev.to/enbis/how-udev-rules-can-help-us-to-recognize-a-usb-to-serial-device-over-dev-tty-interface-pbk>`_.

    Requires:

        * **pyserial** (``pip install pyserial``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    _default_lock_timeout: float = 2.0

    def __init__(
        self,
        device: Optional[str] = None,
        baud_rate: int = 9600,
        max_size: int = 1 << 19,
        timeout: float = _default_lock_timeout,
        enable_polling: bool = True,
        poll_interval: float = 0.1,
        **kwargs,
    ):
        """
        :param device: Device path (e.g. ``/dev/ttyUSB0`` or ``/dev/ttyACM0``)
        :param baud_rate: Serial baud rate (default: 9600)
        :param max_size: Maximum size of a JSON payload (default: 512 KB). The
            plugin will keep reading bytes from the wire until it can form a
            valid JSON payload, so this upper limit is required to prevent the
            integration from listening forever and dumping garbage in memory.
        :param timeout: This integration will ensure that only one
            reader/writer can access the serial device at the time, in order to
            prevent mixing up bytes in the response. This value specifies how
            long we should wait for a pending action to terminate when we try
            to run a new action. Default: 2 seconds.
        :param enable_polling: If ``False``, the plugin will not poll the
            device for updates. This can be the case if you want to
            programmatically interface with the device via the :meth:`.read`
            and :meth:`.write` methods instead of polling for updates in JSON
            format.
        :param poll_interval: How often (in seconds) we should poll the device
            for new data. Since we are reading JSON data from a serial
            interface whenever it's ready, the default here can be quite low
            (default: 0.1 seconds).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)

        self.device = device
        self.baud_rate = baud_rate
        self.serial = None
        self.serial_lock = threading.RLock()
        self.last_data: dict = {}
        self._max_size = max_size
        self._timeout = timeout
        self._enable_polling = enable_polling

    def _read_json(
        self,
        serial_port: Serial,
        max_size: Optional[int] = None,
    ) -> str:
        """
        Reads a JSON payload from the wire. It counts the number of curly
        brackets detected, ignoring everything before the first curly bracket,
        and it stops when the processed payload has balanced curly brackets -
        i.e. it can be mapped to JSON.

        :param serial_port: Serial connection.
        :param max_size: Default ``max_size`` override.
        """
        n_brackets = 0
        is_escaped_ch = False
        parse_start = False
        output = bytes()
        max_size = max_size or self._max_size

        while True:
            assert len(output) <= max_size, (
                'Maximum allowed size exceeded while reading from the device: '
                f'read {len(output)} bytes'
            )

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

    def __get_serial(
        self,
        device: Optional[str] = None,
        baud_rate: Optional[int] = None,
        reset: bool = False,
    ) -> Serial:
        """
        Return a ``Serial`` connection object to the given device.

        :param device: Default device path override.
        :param baud_rate: Default baud rate override.
        :param reset: By default, if a connection to the device is already open
            then the current object will be returned. If ``reset=True``, the
            connection will be reset and a new one will be created instead.
        """
        if not device:
            assert self.device, 'No device specified nor default device configured'
            device = self.device

        if baud_rate is None:
            assert self.baud_rate, 'No baud_rate specified nor default configured'
            baud_rate = self.baud_rate

        if self.serial:
            if not reset:
                return self.serial

            self._close_serial()

        self.serial = Serial(device, baud_rate)
        return self.serial

    def _get_serial(
        self,
        device: Optional[str] = None,
        baud_rate: Optional[int] = None,
    ) -> Serial:
        """
        Return a ``Serial`` connection object to the given device.

        :param device: Default device path override.
        :param baud_rate: Default baud rate override.
        :param reset: By default, if a connection to the device is already open
            then the current object will be returned. If ``reset=True``, the
            connection will be reset and a new one will be created instead.
        """
        try:
            return self.__get_serial(device, baud_rate)
        except AssertionError as e:
            raise e
        except Exception as e:
            self.logger.debug(e)
            self.wait_stop(1)
            return self.__get_serial(device=device, baud_rate=baud_rate, reset=True)

    def _close_serial(self):
        """
        Close the serial connection if it's currently open.
        """
        if self.serial:
            try:
                self.serial.close()
            except Exception as e:
                self.logger.warning('Error while closing serial communication: %s', e)
                self.logger.exception(e)

            self.serial = None

    def _get_device_and_baud_rate(
        self, device: Optional[str] = None, baud_rate: Optional[int] = None
    ) -> _DeviceAndRate:
        """
        Gets the device path and baud rate from the given device and baud rate
        if set, or it falls back on the default configured ones.

        :raise AssertionError: If neither ``device`` nor ``baud_rate`` is set
            nor configured.
        """

        if not device:
            assert (
                self.device
            ), 'No device specified and a default one is not configured'
            device = self.device

        if baud_rate is None:
            assert (
                self.baud_rate is not None
            ), 'No baud_rate specified nor a default value is configured'
            baud_rate = self.baud_rate

        return _DeviceAndRate(device, baud_rate)

    @override
    @action
    def get_measurement(
        self,
        *_,
        device: Optional[str] = None,
        baud_rate: Optional[int] = None,
        **__,
    ) -> Dict[str, Numeric]:
        """
        Reads JSON data from the serial device and returns it as a message

        :param device: Device path (default: default configured device).
        :param baud_rate: Baud rate (default: default configured baud_rate).
        """

        device, baud_rate = self._get_device_and_baud_rate(device, baud_rate)
        data = None

        with get_lock(self.serial_lock, timeout=self._timeout) as serial_available:
            if serial_available:
                ser = self._get_serial(device=device, baud_rate=baud_rate)
                data = self._read_json(ser)

                try:
                    data = dict(json.loads(data))
                except (ValueError, TypeError) as e:
                    raise AssertionError(
                        f'Invalid JSON message from {device}: {e}. Message: {data}'
                    ) from e
            else:
                data = self.last_data

        if data:
            self.last_data = data

        return data

    @action
    def read(
        self,
        device: Optional[str] = None,
        baud_rate: Optional[int] = None,
        size: Optional[int] = None,
        end: Optional[Union[int, str]] = None,
        binary: bool = False,
    ) -> str:
        """
        Reads raw data from the serial device

        :param device: Device to read (default: default configured device)
        :param baud_rate: Baud rate (default: default configured baud_rate)
        :param size: Number of bytes to read
        :param end: End of message, as a character or bytecode
        :param binary: If set to ``True``, then the serial output will be
            interpreted as binary data and a base64-encoded representation will
            be returned. Otherwise, the output will be interpreted as a UTF-8
            encoded string.
        :return: The read message as a UTF-8 string if ``binary=False``,
            otherwise as a base64-encoded string.
        """

        device, baud_rate = self._get_device_and_baud_rate(device, baud_rate)
        assert not (
            (size is None and end is None) or (size is not None and end is not None)
        ), 'Either size or end must be specified'

        assert not (
            end and isinstance(end, str) and len(end) > 1
        ), 'The serial end must be a single character, not a string'

        data = bytes()

        with get_lock(self.serial_lock, timeout=self._timeout) as serial_available:
            assert serial_available, 'Serial read timed out'

            ser = self._get_serial(device=device, baud_rate=baud_rate)
            if size is not None:
                for _ in range(0, size):
                    data += ser.read()
            elif end is not None:
                end_byte = end.encode() if isinstance(end, str) else bytes([end])
                ch = None

                while ch != end_byte:
                    ch = ser.read()
                    if ch != end:
                        data += ch

        return base64.b64encode(data).decode() if binary else data.decode('utf-8')

    @action
    def write(
        self,
        data: Union[str, dict, list, bytes, bytearray],
        device: Optional[str] = None,
        baud_rate: Optional[int] = None,
        binary: bool = False,
    ):
        """
        Writes data to the serial device.

        :param device: Device to write (default: default configured device).
        :param baud_rate: Baud rate (default: default configured baud_rate).
        :param data: Data to send to the serial device. It can be any of the following:

            - A UTF-8 string
            - A base64-encoded string (if ``binary=True``)
            - A dictionary/list that will be encoded as JSON
            - A bytes/bytearray sequence

        :param binary: If ``True``, then the message is either a
            bytes/bytearray sequence or a base64-encoded string.
        """

        device, baud_rate = self._get_device_and_baud_rate(device, baud_rate)
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        if isinstance(data, str):
            data = base64.b64decode(data) if binary else data.encode('utf-8')

        data = bytes(data)
        with get_lock(self.serial_lock, timeout=self._timeout) as serial_available:
            assert serial_available, 'Could not acquire the device lock'
            ser = self._get_serial(device=device, baud_rate=baud_rate)
            self.logger.info('Writing %d bytes to %s', len(data), device)
            ser.write(data)

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:
        transformed_entities = []

        for k, v in entities.items():
            sensor_id = f'serial:{k}'
            try:
                value = float(v)
                entity_type = NumericSensor
            except (TypeError, ValueError):
                value = v
                entity_type = RawSensor

            transformed_entities.append(
                entity_type(
                    id=sensor_id,
                    name=k,
                    value=value,
                )
            )

        return [
            Device(
                id='serial',
                name=self.device,
                children=transformed_entities,
            )
        ]

    @override
    def main(self):
        if not self._enable_polling:
            # If the polling is disabled, we don't need to do anything here
            self.wait_stop()
            return

        super().main()

    @override
    def stop(self):
        super().stop()
        self._close_serial()


# vim:sw=4:ts=4:et:
