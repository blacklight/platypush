import base64
import io
import os
import threading
from typing import Dict, Optional, List, Any, Union

import websocket

from platypush import Response
from platypush.message.response.esp import EspWifiScanResult, EspWifiConfigResult
from platypush.plugins import Plugin, action
from platypush.plugins.esp.models.connection import Connection
from platypush.plugins.esp.models.device import Device


class EspPlugin(Plugin):
    # noinspection PyUnresolvedReferences
    """
        This plugin allows you to fully control to ESP8266/ESP32 devices connected over WiFi.
        It uses the WebREPL interface embedded in MicroPython to communicate with the device.

        All you need to do is to flash the MicroPython firmware to your device, enable the WebREPL interface,
        and you can use this plugin to fully control the device remotely without deploying any code to the controller.

            - Download the `MicroPython firmware <https://micropython.org/download>`_ for your device.
            - Connect your ESP8266/ESP32 via serial/USB port and
              `flash the firmware <https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#intro>`_.
              For example. using ``esptool`` and assuming that you have an ESP8266 device connected on ``/dev/ttyUSB0``:

              .. code-block:: shell

                  # Erase the flash memory
                  esptool.py --port /dev/ttyUSB0 erase_flash
                  # Flash the firmware
                  esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect 0 esp8266-[version].bin

            - Access the MicroPython interpreter over serial/USB port. For example, on Linux:

            .. code-block:: shell

                picocom /dev/ttyUSB0 -b11520

            - Configure the WiFi interface:

            .. code-block:: python

                >>> import network
                >>> wlan = network.WLAN(network.STA_IF)
                >>> wlan.active(True)
                >>> wlan.connect('YourSSID', 'YourPassword')
                >>> # Print the device IP address
                >>> wlan.ifconfig()[0]
                >>> '192.168.1.23'

            - Enable the`WebREPL <https://docs.micropython.org/en/latest/esp8266/quickref.html#webrepl-web-browser-interactive-prompt>`_
              interface on the device:

              .. code-block:: python

                  >>> import webrepl_setup

            - Follow the instructions, set a password and reset your device. A websocket service should be available
              by default on the port 8266 of your ESP8266/ESP32 and it can accept commands sent by platypush.
        """

    def __init__(self, devices: List[Union[Device, dict]] = None, **kwargs):
        """
        :param devices: List of configured device. Pre-configuring devices by name allows you to call the actions
            directly by device name, instead of specifying ``host``, ``port`` and ``password`` on each call. It
            also allows you to interact with PINs by name, if you specified names for them, instead of using the
            PIN number on your calls. Example configuration:

            .. code-block:: yaml

                devices:
                    - host: 192.168.1.23
                      port: 8266        # WebREPL websocket port
                      password: pwd1    # Device password
                      name: smoke_detector
                      pins:
                        - number: 14
                          name: smoke_sensor
                          pwm: False

                    - host: 192.168.1.24
                      port: 8266
                      password: pwd2
                      name: smart_switch
                      pins:
                        - number: 13
                          name: relay
                          pwm: True

        """

        super().__init__(**kwargs)
        self.devices = [
            dev if isinstance(dev, Device) else Device(**dev)
            for dev in (devices or [])
        ]

        self._devices_by_host = {dev['host']: dev for dev in self.devices}
        self._devices_by_name = {dev['name']: dev for dev in self.devices if dev['name']}
        self._connections: Dict[tuple, Connection] = {}

    def __del__(self):
        if not self._connections:
            return
        for conn in self._connections.values():
            conn.close()

    def on_open(self, conn: Connection):
        def callback(*_):
            conn.on_connect()
            self.logger.info('Connection to {} opened'.format(conn.ws.url))

        return callback

    def on_message(self, conn: Connection):
        def handler(*args):
            msg = args[1] if len(args) > 1 else args[0]
            if not isinstance(msg, str):
                # Bytes sequences will be handled by on_data
                return

            if msg.endswith('Password: ') and conn.state == conn.State.CONNECTED:
                conn.on_password_requested()
                return

            if conn.state in (conn.State.CONNECTED, conn.state.PASSWORD_REQUIRED) and msg.endswith('>>> '):
                conn.on_ready()
                return

            if conn.state == conn.State.WAITING_ECHO:
                conn.on_recv_echo(msg)
                return

            if conn.state == conn.State.WAITING_RESPONSE:
                if msg.endswith('>>> '):
                    msg = msg[:-4]
                    conn.on_recv_response(msg)
                else:
                    conn.append_response(msg)

                return

            self.logger.debug('Message received on {}: {}'.format(conn.ws.url, msg))

        def callback(ws, msg):
            try:
                handler(ws, msg)
            except Exception as e:
                self.logger.exception(e)
                raise e

        return callback

    def on_data(self, conn: Connection):
        # noinspection PyUnusedLocal
        def handler(ws, data):
            if conn.state == conn.State.WAITING_FILE_TRANSFER_RESPONSE:
                conn.on_recv_file_transfer_response(data)
                return

            if conn.state == conn.State.UPLOADING_FILE:
                conn.on_file_transfer_completed(data)
                return

            if conn.state == conn.State.DOWNLOADING_FILE:
                conn.on_chunk_received(data)
                return

        # noinspection PyUnusedLocal
        def callback(ws, data, data_type, *_):
            try:
                if data_type == websocket.ABNF.OPCODE_BINARY:
                    handler(ws, data)
            except Exception as e:
                self.logger.exception(e)
                raise e

        return callback

    def on_close(self, conn: Connection):
        def callback(*_):
            try:
                conn.ws.close()
            except Exception as e:
                self.logger.warning('Could not close connection: {}'.format(str(e)))

            conn.on_close()
            self.logger.info('Connection to {}:{} closed'.format(conn.host, conn.port))

        return callback

    def on_error(self, conn: Connection):
        def callback(*args):
            err = args[1] if len(args) > 1 else args[0]
            conn.on_close()
            self.logger.warning('Websocket connection error: {}'.format(err))

        return callback

    # noinspection PyUnusedLocal
    def _get_device(self, device: Optional[str] = None, host: Optional[str] = None, port: int = 8266,
                    password: Optional[str] = None, **kwargs) -> Device:
        if device:
            assert device in self._devices_by_name, 'No such device configured: ' + device
            return self._devices_by_name[device]

        assert host and port, 'No host and port specified'
        if host in self._devices_by_host:
            return self._devices_by_host[host]

        return Device(host=host, port=port, password=password)

    # noinspection PyUnusedLocal
    def _get_connection(self, device: Optional[str] = None, host: Optional[str] = None, port: int = 8266, **kwargs) \
            -> Connection:
        if device:
            assert device in self._devices_by_name, 'No such device configured: ' + device
            device = self._devices_by_name[device]
            host = device['host']
            port = device['port']

        assert host and port, 'No host and port specified'
        return self._connections.get((host, port))

    @action
    def connect(self, device: Optional[str] = None, host: Optional[str] = None, port: int = 8266,
                password: Optional[str] = None, timeout: Optional[float] = 10.0):
        """
        Open a connection to an ESP device.

        :param device: Configured device name. Either ``device`` or ``host`` and ``port`` must be provided.
        :param host: ESP host.
        :param port: ESP port (default: 8266).
        :param password: ESP WebREPL password.
        :param timeout: Connection timeout (default: 10 seconds).
        """
        device = self._get_device(device=device, host=host, port=port, password=password)
        host = device['host']
        port = device['port']
        conn = self._get_connection(host=host, port=port)
        if conn and conn.ws and conn.ws.sock.connected:
            self.logger.info('Already connected to {}:{}'.format(host, port))
            return

        conn = Connection(host=host, port=port, password=password, connect_timeout=timeout)
        self._connections[(host, port)] = conn

        ws = websocket.WebSocketApp('ws://{host}:{port}'.format(host=host, port=port),
                                    on_open=self.on_open(conn),
                                    on_message=self.on_message(conn),
                                    on_data=self.on_data(conn),
                                    on_error=self.on_error(conn),
                                    on_close=self.on_close(conn))

        conn.ws = ws
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        conn.wait_ready()

    @action
    def close(self, device: Optional[str] = None, host: Optional[str] = None, port: int = 8266):
        """
        Close an active connection to a device.
        :param device: Configured device name. Either ``device`` or ``host`` and ``port`` must be provided.
        :param host: ESP host.
        :param port: ESP port.
        """
        device = self._get_device(device=device, host=host, port=port)
        host, port = [device['host'], device['port']]
        conn = self._connections.get((host, port))
        assert conn, 'No active connection found to {}:{}'.format(host, port)
        conn.close()
        del self._connections[(host, port)]

    # noinspection PyUnusedLocal
    @action
    def execute(self,
                code: str,
                device: Optional[str] = None,
                host: Optional[str] = None,
                port: int = 8266,
                password: Optional[str] = None,
                conn_timeout: Optional[float] = 10.0,
                recv_timeout: Optional[float] = 30.0,
                wait_response: bool = True,
                **kwargs) -> Response:
        """
        Run raw Python code on the ESP device.

        :param code: Snippet of code to run.
        :param device: Configured device name. Either ``device`` or ``host`` and ``port`` must be provided.
        :param host: ESP host.
        :param port: ESP port (default: 8266).
        :param password: ESP WebREPL password.
        :param conn_timeout: Connection timeout (default: 10 seconds).
        :param recv_timeout: Response receive timeout (default: 30 seconds).
        :param wait_response: Wait for the response from the device (default: True)
        :return: The response returned by the Micropython interpreter, as a string.
        """
        device = self._get_device(device=device, host=host, port=port, password=password)
        self.connect(host=device['host'], port=device['port'], password=device['password'], timeout=conn_timeout)
        conn = self._connections.get((device['host'], device['port']))

        try:
            return conn.send(code, timeout=recv_timeout, wait_response=wait_response)
        except Exception as e:
            conn.close()
            raise e

    @action
    def pin_on(self, pin: Union[int, str], pull_up: bool = False, **kwargs):
        """
        Set the specified PIN to HIGH.

        :param pin: GPIO PIN number or configured name.
        :param pull_up: Set to True if the PIN has a (weak) pull-up resistor attached.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.Pin({pin}, machine.Pin.OUT{pull_up})
pin.on()
'''.format(pin=pin, pull_up=', machine.Pin.PULL_UP' if pull_up else '')

        self.execute(code, **kwargs)

    @action
    def pin_off(self, pin: Union[int, str], pull_up: bool = False, **kwargs):
        """
        Set the specified PIN to LOW.

        :param pin: GPIO PIN number.
        :param pull_up: Set to True if the PIN has a (weak) pull-up resistor attached.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.Pin({pin}, machine.Pin.OUT{pull_up})
pin.off()
'''.format(pin=pin, pull_up=', machine.Pin.PULL_UP' if pull_up else '')

        self.execute(code, **kwargs)

    @action
    def pin_toggle(self, pin: Union[int, str], pull_up: bool = False, **kwargs):
        """
        Toggle a PIN state - to HIGH if LOW, to LOW if HIGH.

        :param pin: GPIO PIN number or configured name.
        :param pull_up: Set to True if the PIN has a (weak) pull-up resistor attached.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.Pin({pin}, machine.Pin.OUT{pull_up})
if pin.value():
    pin.off()
else:
    pin.on()
'''.format(pin=pin, pull_up=', machine.Pin.PULL_UP' if pull_up else '')

        self.execute(code, **kwargs)

    @action
    def pin_read(self, pin: Union[int, str], out: bool = False, pull_up: bool = False, **kwargs) -> bool:
        """
        Get the ON/OFF value of a PIN.

        :param pin: GPIO PIN number or configured name.
        :param out: Treat the PIN as an output PIN - e.g. if you usually write to it and now want to read the
            value. If not set, then the PIN will be treated as an input PIN.
        :param pull_up: Set to True if the PIN has a (weak) pull-up resistor attached.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.Pin({pin}, machine.Pin.{inout}{pull_up})
pin.value()
'''.format(pin=pin, inout='OUT' if out else 'IN', pull_up=', machine.Pin.PULL_UP' if pull_up else '')

        return bool(self.execute(code, **kwargs).output)

    @action
    def adc_read(self, pin: int = 0, **kwargs) -> int:
        """
        Read an analog value from a PIN. Note that the ESP8266 only has one analog PIN, accessible on
        the channel ``0``. If you are interested in the actual voltage that is measured then apply
        ``V = Vcc * (value/1024)``, where ``Vcc`` is the supply voltage provided to the device (usually 3V if
        connected to the Vcc PIN of an ESP8266).

        :param pin: GPIO PIN number (default: 0).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: A value between ``0`` and ``1024``.
        """
        code = '''
import machine
adc = machine.ADC({pin})
adc.read()
'''.format(pin=pin)

        response = self.execute(code, **kwargs)
        return int(response.output)

    @action
    def pwm_freq(self, pin: Union[int, str], freq: Optional[int] = None, **kwargs) -> Optional[int]:
        """
        Get/set the frequency of a PWM PIN.

        :param pin: GPIO PIN number or configured name.
        :param freq: If set, set the frequency for the PIN in Hz.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.PWM(machine.Pin({pin}))
pin.freq({freq})
'''.format(pin=pin, freq=freq if freq else '')

        ret = self.execute(code, **kwargs).output
        if not freq:
            return int(ret)

    @action
    def pwm_duty(self, pin: Union[int, str], duty: Optional[int] = None, **kwargs) -> Optional[int]:
        """
        Get/set the duty cycle of a PWM PIN.

        :param pin: GPIO PIN number or configured name.
        :param duty: Optional duty value to set.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.PWM(machine.Pin({pin}))
pin.duty({duty})
'''.format(pin=pin, duty=duty if duty else '')

        ret = self.execute(code, **kwargs).output
        if not duty:
            return int(ret)

    @action
    def pwm_on(self, pin: Union[int, str], freq: Optional[int] = None, duty: Optional[int] = None, **kwargs):
        """
        Set the specified PIN to HIGH.

        :param pin: GPIO PIN number or configured name.
        :param freq: PWM PIN frequency.
        :param duty: PWM PIN duty cycle.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.PWM(machine.Pin({pin}))

if {freq}:
    pin.freq({freq})
if {duty}:
    pin.duty({duty})

pin.on()
'''.format(pin=pin, freq=freq, duty=duty)

        self.execute(code, **kwargs)

    @action
    def pwm_off(self, pin: Union[int, str], **kwargs):
        """
        Turn off a PWM PIN.

        :param pin: GPIO PIN number or configured name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
pin = machine.PWM(machine.Pin({pin}))
pin.deinit()
'''.format(pin=pin)

        self.execute(code, **kwargs)

    @action
    def spi_open(self, id=1, baudrate: int = 1000000, polarity: int = 0, phase: int = 0,
                 bits: int = 8, sck: Optional[int] = None, mosi: Optional[int] = None,
                 miso: Optional[int] = None, **kwargs):
        """
        Open a connection to an SPI port.
        Note that ``sck``, ``mosi`` and ``miso`` parameters are only allowed if you're setting up a software
        managed SPI connection. If you're using the hardware SPI implementation then those PINs are
        pre-defined depending on the model of your board.

        :param id: Values of id depend on a particular port and its hardware. Values 0, 1, etc. are commonly used to
            select hardware SPI block #0, #1, etc. Value -1 can be used for bit-banging (software) implementation of
            SPI (if supported by a port).
        :param baudrate: Port baudrate/SCK clock rate (default: 1 MHz).
        :param polarity: It can be 0 or 1, and is the level the idle clock line sits at.
        :param phase: It can be 0 or 1 to sample data on the first or second clock edge respectively.
        :param bits: Number of bits per character. It can be 7, 8 or 9.
        :param sck: SCK PIN number.
        :param mosi: MOSI PIN number.
        :param miso: MISO PIN number.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
args = {
    'baudrate': {baudrate},
    'polarity': {polarity},
    'phase': {phase},
    'bits': {bits},
}
'''.format(baudrate=baudrate, polarity=polarity, phase=phase, bits=bits)

        self.execute(code, **kwargs)
        code = '''
import machine

if {sck}:
    args['sck'] = machine.Pin({sck})
if {mosi}:
    args['mosi'] = machine.Pin({mosi})
if {miso}:
    args['miso'] = machine.Pin({miso})
'''.format(sck=sck, mosi=mosi, miso=miso)

        self.execute(code, **kwargs)
        code = 'spi = machine.SPI({id}, **args)'.format(id=id)
        self.execute(code, **kwargs)

    @action
    def spi_close(self, **kwargs):
        """
        Turn off an SPI bus.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.spi_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.spi_open(**kwargs)
        self.execute('spi.deinit()', **kwargs)

    @action
    def spi_read(self, size: int, **kwargs) -> str:
        """
        Read from an SPI bus.

        :param size: Number of bytes to read.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.spi_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        self.spi_open(**kwargs)
        code = 'spi.read({size})'.format(size=size)
        response = self.execute(code, **kwargs).output

        try:
            return response.decode()
        except UnicodeDecodeError:
            return base64.encodebytes(response).decode()

    @action
    def spi_write(self, data: str, binary: bool = False, **kwargs):
        """
        Write data to an SPI bus.

        :param data: Data to be written.
        :param binary: By default data will be treated as a string. Set binary to True if it should
            instead be treated as a base64-encoded binary string to be decoded before being sent.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.spi_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        if binary:
            data = base64.decodebytes(data.encode())
        else:
            data = data.encode()

        data = 'b"' + ''.join(['\\x{:02x}'.format(b) for b in data]) + '"'
        self.spi_open(**kwargs)

        code = 'spi.write({data})'.format(data=data)
        self.execute(code, **kwargs)

    @action
    def i2c_open(self, scl: Optional[int] = None, sda: Optional[int] = None, id: int = -1, baudrate: int = 400000,
                 **kwargs):
        """
        Open a connection to an I2C (or "two-wire") port.

        :param scl: PIN number for the SCL (serial clock) line.
        :param sda: PIN number for the SDA (serial data) line.
        :param id: The default value of -1 selects a software implementation of I2C which can work (in most cases)
            with arbitrary pins for SCL and SDA. If id is -1 then scl and sda must be specified. Other allowed
            values for id depend on the particular port/board, and specifying scl and sda may or may not be required
            or allowed in this case.
        :param baudrate: Port frequency/clock rate (default: 400 kHz).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine

args = {}
if {scl}:
    args['scl'] = machine.Pin(''' + str(scl) + ''')
if {sda}:
    args['sda'] = machine.Pin(''' + str(sda) + ''')
'''

        self.execute(code, **kwargs)

        code = '''
i2c = machine.I2C(id={id}, freq={baudrate}, **args)
'''.format(id=id, baudrate=baudrate)

        self.execute(code, **kwargs)

    @action
    def i2c_close(self, **kwargs):
        """
        Turn off an I2C bus.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.i2c_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.i2c_open(**kwargs)
        self.execute('i2c.deinit()', **kwargs)

    @action
    def i2c_scan(self, **kwargs) -> List[int]:
        """
        Scan for device addresses on the I2C bus.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.i2c_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: List of 7-bit addresses.
        """
        self.i2c_open(**kwargs)
        return self.execute('i2c.scan', **kwargs).output

    @action
    def i2c_read(self, address: int, size: int, **kwargs) -> str:
        """
        Read data from the I2C bus.

        :param address: I2C address.
        :param size: Number of bytes to read.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.i2c_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        self.i2c_open(**kwargs)
        code = 'i2c.readfrom({address}, {size})'.format(address=address, size=size)
        response = self.execute(code, **kwargs).output

        try:
            return response.decode()
        except UnicodeDecodeError:
            return base64.encodebytes(response).decode()

    @action
    def i2c_write(self, address: int, data: str, binary: bool = False, **kwargs):
        """
        Write data to the I2C bus.

        :param address: I2C address.
        :param data: Data to be sent.
        :param binary: By default data will be treated as a string. Set binary to True if it should
            instead be treated as a base64-encoded binary string to be decoded before being sent.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.i2c_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        if binary:
            data = base64.decodebytes(data.encode())
        else:
            data = data.encode()

        data = 'b"' + ''.join(['\\x{:02x}'.format(b) for b in data]) + '"'
        self.i2c_open(**kwargs)
        code = 'i2c.writeto({address}, {data})'.format(address=address, data=data)
        self.execute(code, **kwargs)

    @action
    def i2c_start(self, **kwargs):
        """
        Generate a START condition on an I2C bus.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.i2c_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        self.i2c_open(**kwargs)
        self.execute('i2c.start()', **kwargs)

    @action
    def i2c_stop(self, **kwargs):
        """
        Generate a STOP condition on an I2C bus.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.i2c_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        self.i2c_open(**kwargs)
        self.execute('i2c.stop()', **kwargs)

    @action
    def uart_open(self, id=1, baudrate: Optional[int] = 9600, bits: Optional[int] = 8, parity: Optional[int] = None,
                  stop: int = 1, tx_pin: Optional[int] = None, rx_pin: Optional[int] = None,
                  timeout: Optional[float] = None, timeout_char: Optional[float] = None, **kwargs):
        """
        Open a connection to a UART port.

        :param id: Bus ID (default: 1).
        :param baudrate: Port baudrate (default: 9600).
        :param bits: Number of bits per character. It can be 7, 8 or 9.
        :param parity: Parity configuration. It can be None (no parity), 0 (even) or 1 (odd).
        :param stop: Number of stop bits. It can be 1 or 2.
        :param tx_pin: Specify the TX PIN to use.
        :param rx_pin: Specify the RX PIN to use.
        :param timeout: Specify the time to wait for the first character in seconds.
        :param timeout_char: Specify the time to wait between characters in seconds.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
args = {
    'bits': {bits},
    'parity': {parity},
    'stop': {stop},
}

if {tx_pin}:
    args['tx'] = {tx_pin}
if {rx_pin}:
    args['rx'] = {rx_pin}
if {timeout}:
    args['timeout'] = {timeout}
if {timeout_char}:
    args['timeout_char'] = {timeout_char}
'''.format(bits=bits, parity=parity, stop=stop, tx_pin=tx_pin, rx_pin=rx_pin,
           timeout=timeout, timeout_char=timeout_char)

        self.execute(code, **kwargs)

        code = '''
import machine
uart = machine.UART({id}, {baudrate}, **args)
'''.format(id=id, baudrate=baudrate)

        self.execute(code, **kwargs)

    @action
    def uart_close(self, **kwargs):
        """
        Turn off the UART bus.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.uart_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.uart_open(**kwargs)
        self.execute('uart.deinit()', **kwargs)

    @action
    def uart_read(self, size: Optional[int] = None, **kwargs) -> str:
        """
        Read from a UART interface.

        :param size: Number of bytes to read (default: read all available characters).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.uart_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        self.uart_open(**kwargs)

        code = '''
args = []
if {size}:
    args.append({size})

uart.read(*args)
'''.format(size=size)

        response = self.execute(code, **kwargs).output
        try:
            return response.decode()
        except UnicodeDecodeError:
            return base64.encodebytes(response).decode()

    @action
    def uart_readline(self, **kwargs) -> str:
        """
        Read a line (any character until newline is found) from a UART interface.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.uart_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: String representation of the read bytes, or base64-encoded representation if the
            data can't be decoded to a string.
        """
        self.uart_open(**kwargs)
        response = self.execute('uart.readline()', **kwargs).output

        try:
            return response.decode()
        except UnicodeDecodeError:
            return base64.encodebytes(response).decode()

    @action
    def uart_write(self, data: str, binary: bool = False, **kwargs):
        """
        Write data to the UART bus.

        :param data: Data to be written.
        :param binary: By default data will be treated as a string. Set binary to True if it should
            instead be treated as a base64-encoded binary string to be decoded before being sent.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.uart_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        if binary:
            data = base64.decodebytes(data.encode())
        else:
            data = data.encode()

        data = 'b"' + ''.join(['\\x{:02x}'.format(b) for b in data]) + '"'
        self.uart_open(**kwargs)

        code = 'uart.write({data})'.format(data=data)
        self.execute(code, **kwargs)

    @action
    def uart_send_break(self, **kwargs):
        """
        Send a break condition to a UART bus.
        This drives the bus low for a duration longer than required for a normal transmission of a character.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.uart_open` and
            :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.uart_open(**kwargs)
        code = 'uart.sendbreak()'
        self.execute(code, **kwargs)

    @action
    def get_freq(self, **kwargs) -> int:
        """
        Get the frequency of the device in Hz.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.freq()
'''
        return self.execute(code, **kwargs).output

    @action
    def set_freq(self, freq: int, **kwargs):
        """
        Set the frequency of the device.
        :param freq: New frequency in Hz.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.freq({freq})
'''.format(freq=freq)
        self.execute(code, **kwargs)

    @action
    def reset(self, **kwargs):
        """
        Perform a device reset, similar to the user pushing the RESET button.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.reset()
'''
        return self.execute(code, wait_response=False, **kwargs).output

    @action
    def soft_reset(self, **kwargs):
        """
        Performs a soft reset of the interpreter, deleting all Python objects and resetting the Python heap.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.soft_reset()
'''
        return self.execute(code, wait_response=False, **kwargs).output

    @action
    def disable_irq(self, **kwargs):
        """
        Disable interrupt requests.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.disable_irq()
'''
        return self.execute(code, **kwargs).output

    @action
    def enable_irq(self, **kwargs):
        """
        Enable interrupt requests.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.enable_irq()
'''
        return self.execute(code, **kwargs).output

    @action
    def sleep(self, seconds: float, **kwargs):
        """
        Perform a software sleep (i.e. ``time.sleep()``).

        :param seconds: Sleep seconds.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import time
time.sleep({sec})
'''.format(sec=seconds)

        return self.execute(code, wait_response=False, **kwargs).output

    @action
    def soft_sleep(self, seconds: Optional[float] = None, **kwargs):
        """
        Stops execution in an attempt to enter a low power state.
        A light-sleep has full RAM and state retention. Upon wake execution is resumed from the point where the sleep
        was requested, with all subsystems operational.

        :param seconds: Sleep seconds (default: sleep until there are some PIN/RTC events to process)
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.lightsleep({msec})
'''.format(msec=int(seconds * 1000) if seconds else '')

        return self.execute(code, wait_response=False, **kwargs).output

    @action
    def deep_sleep(self, seconds: Optional[float] = None, **kwargs):
        """
        Stops execution in an attempt to enter a low power state.
        A deepsleep may not retain RAM or any other state of the system (for example peripherals or network interfaces).
        Upon wake execution is resumed from the main script, similar to a hard or power-on reset.

        :param seconds: Sleep seconds (default: sleep until there are some PIN/RTC events to process)
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
machine.deepsleep({msec})
'''.format(msec=int(seconds * 1000) if seconds else '')

        return self.execute(code, wait_response=False, **kwargs).output

    @action
    def unique_id(self, **kwargs) -> str:
        """
        Get the unique ID of the device.
        t will vary from a board/SoC instance to another, if underlying hardware allows. Length varies by hardware
        (so use substring of a full value if you expect a short ID). In some MicroPython ports, ID corresponds to
        the network MAC address..

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import machine
print(':'.join(['{:02x}'.format(b) for b in machine.unique_id()]))
'''

        return self.execute(code, **kwargs).output

    @action
    def set_password(self, new_password: str, **kwargs):
        """
        Change the WebREPL password for the device.

        :param new_password: New password.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import webrepl
webrepl._webrepl.password({password})
'''.format(password=new_password)

        return self.execute(code, **kwargs).output

    @action
    def wifi_connect(self, essid: str, passphrase: str, **kwargs):
        """
        Connect the device WiFi interface to the specified access point.

        :param essid: WiFi ESSID.
        :param passphrase: WiFi passphrase.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('{essid}', '{passphrase}')

while not wlan.isconnected():
    time.sleep(1)
'''.format(essid=essid, passphrase=passphrase)

        self.execute(code, **kwargs)

    def net_enabled_change(self, net: str, enabled: bool, **kwargs):
        code = '''
import network
wlan = network.WLAN({})
wlan.active({})
'''.format(net, str(enabled))
        self.execute(code, **kwargs)

    def net_ifconfig(self, net: str, ip: Optional[str] = None, netmask: Optional[str] = None,
                     gateway: Optional[str] = None, dns: Optional[str] = None, **kwargs):
        code = '''
import json
import network

wlan = network.WLAN({})
print(json.dumps(list(wlan.ifconfig())))
'''.format(net)

        config = self.execute(code, **kwargs).output
        if ip:
            config[0] = ip
        if netmask:
            config[1] = netmask
        if gateway:
            config[2] = gateway
        if dns:
            config[3] = dns

        code = 'wlan.ifconfig({})'.format(tuple(config))
        self.execute(code, **kwargs)

    @action
    def wifi_config(self, ip: Optional[str] = None, netmask: Optional[str] = None,
                    gateway: Optional[str] = None, dns: Optional[str] = None, **kwargs) \
            -> Optional[EspWifiConfigResult]:
        """
        Get or set network properties for the WiFi interface.
        If called with no arguments it will return the configuration of the interface.

        :param ip: IP address.
        :param netmask: Netmask.
        :param gateway: Default gateway address.
        :param dns: Default DNS address.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        if ip or netmask or gateway or dns:
            self.net_ifconfig(net_type='network.STA_IF', ip=ip, netmask=netmask, gateway=gateway, dns=dns, **kwargs)
            return

        return self.net_config('network.STA_IF', **kwargs)

    @action
    def ap_config(self, ip: Optional[str] = None, netmask: Optional[str] = None,
                  gateway: Optional[str] = None, dns: Optional[str] = None, essid: Optional[str] = None,
                  passphrase: Optional[str] = None, channel: Optional[int] = None,
                  hidden: Optional[bool] = None, **kwargs) -> Optional[EspWifiConfigResult]:
        """
        Get or set network properties for the WiFi access point interface.
        If called with no arguments it will return the configuration of the interface.

        :param ip: IP address.
        :param netmask: Netmask.
        :param gateway: Default gateway address.
        :param dns: Default DNS address.
        :param essid: ESSID of the access point.
        :param passphrase: Password/passphrase.
        :param channel: WiFi channel.
        :param hidden: Whether the network is hidden.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        has_args = False
        self.execute(code='import network; ap = network.WLAN(network.AP_IF)'.format(essid=essid), **kwargs)

        if ip or netmask or gateway or dns:
            self.net_ifconfig(net_type='network.AP_IF', ip=ip, netmask=netmask, gateway=gateway, dns=dns, **kwargs)
            has_args = True
        if essid:
            self.execute(code='ap.config(essid="{essid}")'.format(essid=essid), **kwargs)
            has_args = True
        if passphrase:
            self.execute(code='ap.config(password="{passphrase}")'.format(passphrase=passphrase), **kwargs)
            has_args = True
        if channel:
            self.execute(code='ap.config(channel={channel})'.format(channel=channel), **kwargs)
            has_args = True
        if hidden is not None:
            self.execute(code='ap.config(hidden={hidden})'.format(hidden=str(hidden)), **kwargs)
            has_args = True

        if has_args:
            return

        return self.net_config('network.AP_IF', **kwargs)

    @action
    def wifi_enable(self, **kwargs):
        """
        Enable the device WiFi interface.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.net_enabled_change('network.STA_IF', True, **kwargs)

    @action
    def wifi_disable(self, **kwargs):
        """
        Disable the device WiFi interface.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.net_enabled_change('network.STA_IF', False, **kwargs)

    @action
    def wifi_disconnect(self, **kwargs):
        """
        Disconnect from the currently connected WiFi network

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import network
wlan = network.WLAN(network.STA_IF)
wlan.disconnect()
'''
        self.execute(code, **kwargs)

    @action
    def ap_enable(self, **kwargs):
        """
        Enable the device WiFi access point interface.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.net_enabled_change('network.AP_IF', True, **kwargs)

    @action
    def ap_disable(self, **kwargs):
        """
        Disable the device WiFi access point interface.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        self.net_enabled_change('network.AP_IF', False, **kwargs)

    def net_config(self, net_type: str, **kwargs) -> Optional[EspWifiConfigResult]:
        # Split the code into multiple execution to overcome the size limitation of the input ESP WebREPL buffer.
        code = '''
import network
import json

net = network.WLAN(''' + net_type + ''')
ifconfig = net.ifconfig()
mac = ':'.join([hex(c)[2:] for c in net.config('mac')])'''
        self.execute(code, **kwargs)

        code = '''
active = net.active()
essid = net.config('essid')
channel = net.config('channel')
try:
    hidden = net.config('hidden')
except:
    hidden = None

connected = net.isconnected()'''
        self.execute(code, **kwargs)

        code = '''
config = {
    'ip': ifconfig[0],
    'netmask': ifconfig[1],
    'gateway': ifconfig[2],
    'dns': ifconfig[3],
    'mac': mac,
    'connected': connected,
    'active': active,
    'essid': essid,
    'channel': channel,
    'hidden': hidden,
}

print(json.dumps(config))
'''

        net = self.execute(code, **kwargs).output
        if not net:
            return
        return EspWifiConfigResult(**net)

    @action
    def wifi_scan(self, **kwargs) -> List[EspWifiScanResult]:
        """
        Scan the available networks.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import network
import json

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(json.dumps([{
    'essid':net[0].decode(),
    'bssid':''.join(['\\\\x' + hex(c)[2:] for c in net[1]]),
    'channel': net[2],
    'rssi': net[3],
    'auth_mode': net[4],
    'hidden': bool(net[5])
} for net in wlan.scan()]))
'''
        results = self.execute(code, **kwargs).output
        if not results:
            return []

        return [EspWifiScanResult(**network) for network in results]

    def open_db(self, dbfile: str, **kwargs):
        code = '''
import btree

try:
    dbfile = open('{dbfile}', 'r+b')
except OSError:
    dbfile = open('{dbfile}', 'w+b')

db = btree.open(dbfile)
'''.format(dbfile=dbfile)

        self.close_db(dbfile, **kwargs)
        self.execute(code, **kwargs)

    def close_db(self, dbfile: str, **kwargs):
        code = '''
try:
    db.close()
    dbfile.close()
    db = None
    dbfile = None
except:
    pass
'''.format(dbfile=dbfile)

        self.execute(code, **kwargs)

    @staticmethod
    def string_quote(s: str):
        return s.replace("'", "\\'")

    @action
    def db_set(self, dbfile: str, key: str, value: Any, **kwargs):
        """
        Set a value on an internal B-Tree file database.

        :param dbfile: Database file name.
        :param key: Key to set.
        :param value: Value to set.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
db[b'{key}'] = b'{value}'
db.flush()
'''.format(key=self.string_quote(key), value=self.string_quote(str(value)))

        try:
            self.open_db(dbfile, **kwargs)
            self.execute(code, **kwargs)
        finally:
            self.close_db(dbfile, **kwargs)

    @action
    def db_get(self, dbfile: str, key: str, **kwargs) -> Any:
        """
        Set a value on an internal B-Tree file database.

        :param dbfile: Database file name.
        :param key: Key to set.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: Whichever value is stored as output, or null if the key doesn't exist.
        """
        code = '''
try:
    print(db[b'{key}'].decode())
except KeyError:
    pass
'''.format(key=self.string_quote(key))

        try:
            self.open_db(dbfile, **kwargs)
            response = self.execute(code, **kwargs)
            return response
        finally:
            self.close_db(dbfile, **kwargs)

    @action
    def db_keys(self, dbfile: str, **kwargs) -> List[str]:
        """
        Get the list of keys stored on an internal B-Tree file database.

        :param dbfile: Database file name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import json
print(json.dumps([k.decode() for k in db.keys()]))
'''

        try:
            self.open_db(dbfile, **kwargs)
            return self.execute(code, **kwargs).output
        finally:
            self.close_db(dbfile, **kwargs)

    @action
    def db_values(self, dbfile: str, **kwargs) -> List[str]:
        """
        Get the list of item values stored on an internal B-Tree file database.

        :param dbfile: Database file name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import json
print(json.dumps([k.decode() for k in db.values()]))
'''

        try:
            self.open_db(dbfile, **kwargs)
            return self.execute(code, **kwargs).output
        finally:
            self.close_db(dbfile, **kwargs)

    @action
    def db_items(self, dbfile: str, **kwargs) -> Dict[str, str]:
        """
        Get a key->value mapping of the items stored in a B-Tree file database.

        :param dbfile: Database file name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        :return: Whichever value is stored as output, or null if the key doesn't exist.
        """
        code = '''
import json
print(json.dumps({k.decode(): v.decode() for k, v in db.items()}))
'''

        try:
            self.open_db(dbfile, **kwargs)
            return self.execute(code, **kwargs).output
        finally:
            self.close_db(dbfile, **kwargs)

    @action
    def set_ntp_time(self, **kwargs):
        """
        Set the device time using an NTP server.

        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import ntptime
ntptime.settime()
'''

        self.execute(code, **kwargs)

    @action
    def listdir(self, directory: str = '/', **kwargs) -> List[str]:
        """
        List the content of a directory.

        :param directory: Directory name (default: root).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        directory = self.string_quote(directory)
        code = '''
import os
import json

print(json.dumps(os.listdir('{dir}')))
'''.format(dir=directory)

        return self.execute(code, **kwargs).output

    @action
    def chdir(self, directory: str, **kwargs):
        """
        Move to the specified directory.

        :param directory: Directory name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        directory = self.string_quote(directory)
        code = '''
import os
os.chdir('{dir}')
'''.format(dir=directory)

        self.execute(code, **kwargs)

    @action
    def mkdir(self, directory: str, **kwargs):
        """
        Create a directory.

        :param directory: Directory name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        directory = self.string_quote(directory)
        code = '''
import os
os.mkdir('{dir}')
'''.format(dir=directory)

        self.execute(code, **kwargs)

    @action
    def rmdir(self, directory: str, **kwargs):
        """
        Remove a directory.

        :param directory: Directory name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        directory = self.string_quote(directory)
        code = '''
import os
os.rmdir('{dir}')
'''.format(dir=directory)

        self.execute(code, **kwargs)

    @action
    def rename(self, name: str, new_name: str, **kwargs):
        """
        Rename a file or directory.

        :param name: Current resource name.
        :param new_name: New resource name.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        name = self.string_quote(name)
        new_name = self.string_quote(new_name)
        code = '''
import os
os.rename('{old}', '{new}')
'''.format(old=name, new=new_name)

        self.execute(code, **kwargs)

    @action
    def remove(self, file: str, **kwargs):
        """
        Remove a file.

        :param file: File name/path.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        file = self.string_quote(file)
        code = '''
import os
os.remove('{file}')
'''.format(file=file)

        self.execute(code, **kwargs)

    @action
    def urandom(self, size: int = 1, **kwargs) -> List[int]:
        """
        Get randomly generated bytes.

        :param size: Number of random bytes to be generated (default: 1).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        code = '''
import os
import json

print([b for b in os.urandom({size})])
'''.format(size=size)

        return self.execute(code, **kwargs).output

    @action
    def file_get(self, file: str, binary: bool = False, timeout: Optional[float] = 60.0, **kwargs) -> str:
        """
        Get the content of a file on the board.

        :param file: File name/path to get from the device.
        :param binary: If True, then the base64-encoded content of the file will be returned.
        :param timeout: File transfer timeout (default: one minute).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.connect`.
        """
        device = self._get_device(**kwargs)
        host = device['host']
        port = device['port']
        self.connect(host=host, port=port, password=device['password'])
        conn = self._get_connection(host=host, port=port)

        with io.BytesIO() as buffer:
            conn.file_download(file, buffer, timeout=timeout)
            data = buffer.getvalue()

        if binary:
            data = base64.encodebytes(data).decode()
        else:
            data = data.decode()

        return data

    @action
    def file_upload(self, source: str, destination: Optional[str] = None, timeout: Optional[float] = 60.0, **kwargs):
        """
        Upload a file to the board.

        :param source: Path of the local file to copy.
        :param destination: Target file name (default: a filename will be created under the board's
            root folder with the same name as the source file).
        :param timeout: File transfer timeout (default: one minute).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.connect`.
        """
        device = self._get_device(**kwargs)
        host = device['host']
        port = device['port']
        self.connect(host=host, port=port, password=device['password'])
        conn = self._get_connection(host=host, port=port)
        conn.file_upload(source=source, destination=destination, timeout=timeout)

    @action
    def file_download(self, source: str, destination: str, timeout: Optional[float] = 60.0, **kwargs):
        """
        Download a file from the board to the local machine.

        :param source: Name or path of the file to download from the device.
        :param destination: Target directory or path on the local machine.
        :param timeout: File transfer timeout (default: one minute).
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        destination = os.path.abspath(os.path.expanduser(destination))
        if os.path.isdir(destination):
            filename = os.path.basename(source)
            destination = os.path.join(destination, filename)

        device = self._get_device(**kwargs)
        host = device['host']
        port = device['port']
        self.connect(host=host, port=port, password=device['password'])
        conn = self._get_connection(host=host, port=port)

        with open(destination, 'wb') as f:
            conn.file_download(source, f, timeout=timeout)

    def _dht_get_value(self, pin: Union[int, str], dht_type: int, value: str, **kwargs) -> float:
        device = self._get_device(**kwargs)
        pin = device.get_pin(pin)
        code = '''
import machine
import dht

dht_sensor = dht.DHT{type}(machine.Pin({pin}))
dht_sensor.measure()
dht_sensor.{value}()
'''.format(pin=pin, type=dht_type, value=value)

        return self.execute(code, **kwargs).output

    @action
    def dht11_get_temperature(self, pin: Union[int, str], **kwargs) -> float:
        """
        Get the temperature value in Celsius from a connected DHT11 sensor.

        :param pin: GPIO PIN number or configured name where the sensor is connected.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        return self._dht_get_value(pin=pin, dht_type=11, value='temperature', **kwargs)

    @action
    def dht11_get_humidity(self, pin: Union[int, str], **kwargs) -> float:
        """
        Get the humidity value in percentage (0-100) from a connected DHT11 sensor.

        :param pin: GPIO PIN number or configured name where the sensor is connected.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        return self._dht_get_value(pin=pin, dht_type=11, value='humidity', **kwargs)

    @action
    def dht22_get_temperature(self, pin: Union[int, str], **kwargs) -> float:
        """
        Get the temperature value in Celsius from a connected DHT22 sensor.

        :param pin: GPIO PIN number or configured name where the sensor is connected.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        return self._dht_get_value(pin=pin, dht_type=22, value='temperature', **kwargs)

    @action
    def dht22_get_humidity(self, pin: Union[int, str], **kwargs) -> float:
        """
        Get the humidity value in percentage (0-100) from a connected DHT22 sensor.

        :param pin: GPIO PIN number or configured name where the sensor is connected.
        :param kwargs: Parameters to pass to :meth:`platypush.plugins.esp.EspPlugin.execute`.
        """
        return self._dht_get_value(pin=pin, dht_type=22, value='humidity', **kwargs)


# vim:sw=4:ts=4:et:
