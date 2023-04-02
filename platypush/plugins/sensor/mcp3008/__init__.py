import enum
from typing import Dict, List
from typing_extensions import override

from platypush.common.sensors import Numeric
from platypush.entities.devices import Device
from platypush.entities.sensors import NumericSensor
from platypush.plugins import action
from platypush.plugins.sensor import SensorPlugin


class MCP3008Mode(enum.Enum):
    """
    MPC3008 mode enum (``hardware`` or ``software``).
    """

    SOFTWARE = 'software'
    HARDWARE = 'hardware'


# pylint: disable=too-many-ancestors
class SensorMcp3008Plugin(SensorPlugin):
    """
    Plugin to read analog sensor values from an MCP3008 chipset.  The MCP3008
    chipset is a circuit that allows you to read measurements from multiple
    analog sources (e.g. sensors) and multiplex them to a digital device like a
    Raspberry Pi or a regular laptop.  See
    https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008
    for more info.

    Requires:

        * ``adafruit-mcp3008`` (``pip install adafruit-mcp3008``)

    Triggers:

        * :class:`platypush.message.event.sensor.SensorDataAboveThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataBelowThresholdEvent`
        * :class:`platypush.message.event.sensor.SensorDataChangeEvent`

    """

    N_CHANNELS = 8

    # noinspection PyPep8Naming
    def __init__(
        self,
        CLK=None,
        MISO=None,
        MOSI=None,
        CS=None,
        spi_port=None,
        spi_device=None,
        channels=None,
        Vdd=3.3,
        **kwargs,
    ):
        """
        The MCP3008 can be connected in two modes:

            * Hardware SPI mode: advised if you have enough GPIO pins available
                (and slightly faster)
            * Software SPI mode: useful if you don't have all the required GPIO
                PINs for hardware SPI available. Slightly slower, as the conversion
                is done via software, but still relatively performant.

            See
            https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008#wiring
            for info

        :param CLK: (software SPI mode) CLK GPIO PIN
        :type CLK: int
        :param MISO: (software SPI mode) MISO GPIO PIN
        :type MISO: int
        :param MOSI: (software SPI mode) MOSI GPIO PIN
        :type MOSI: int
        :param CS: (software SPI mode) CS GPIO PIN
        :type CS: int

        :param spi_port: (hardware SPI mode) SPI port
        :type spi_port: int
        :param spi_device: (hardware SPI mode) SPI device name
        :type spi_device: str

        :param channels: name-value mapping between MCP3008 output PINs and sensor names. This mapping will be used
            when you get values through :func:`.get_measurement()`. Example::

                channels = {
                    "0": {
                        "name": "temperature",
                        "conv_function": 'round(x*100.0, 2)'  # T = Vout / (10 [mV/C])
                    },
                    "1": {
                        "name": "light",  # ALS-PT9
                        "conv_function": 'round(x*1000.0, 6)'  # ALS-PT9 has a 10 kOhm resistor
                    }
                }

            Note that you can also pass a conversion function as
            ``conv_function`` that will convert the output voltage to whichever
            human-readable value you wish.  In the case above I connected a
            simple temperature sensor to the channel 0 and a simple ALS-PT9
            light sensor to the channel 1, and passed the appropriate conversion
            functions to convert from voltage to, respectively, temperature in
            Celsius degrees and light intensity in lumen. Note that we reference
            the current voltage as ``x`` in ``conv_function``.

        :type channels: dict

        :param Vdd: Input voltage provided to the circuit (default: 3.3V, Raspberry Pi default power source)
        :type Vdd: float
        """

        super().__init__(**kwargs)

        if CLK and MISO and MOSI and CS:
            self.CLK = CLK
            self.MISO = MISO
            self.MOSI = MOSI
            self.CS = CS
            self.mode = MCP3008Mode.SOFTWARE
        elif spi_port and spi_device:
            self.spi_port = spi_port
            self.spi_device = spi_device
            self.mode = MCP3008Mode.HARDWARE
        else:
            raise RuntimeError(
                "At least one mode must be specified.\n"
                + "Software SPI: Specify CLK, MISO, MOSI and CS pins\n"
                + "Hardware SPI: Specify spi_port and spi_device\n"
            )

        self.Vdd = Vdd
        self.channels = channels if channels else {}
        self.mcp = None

    def _get_mcp(self):
        import Adafruit_GPIO.SPI as SPI
        import Adafruit_MCP3008

        if self.mode == MCP3008Mode.SOFTWARE:
            self.mcp = Adafruit_MCP3008.MCP3008(
                clk=self.CLK, cs=self.CS, miso=self.MISO, mosi=self.MOSI
            )
        elif self.mode == MCP3008Mode.HARDWARE:
            self.mcp = Adafruit_MCP3008.MCP3008(
                spi=SPI.SpiDev(self.spi_port, self.spi_device)
            )
        else:
            raise RuntimeError(f'Unsupported MCP3008 mode: {self.mode}')

        return self.mcp

    def _convert_to_voltage(self, value):
        return (value * self.Vdd) / 1023.0 if value is not None else None

    @override
    @action
    def get_measurement(self):
        """
        Returns a measurement from the sensors connected to the MCP3008 device.
        If channels were passed to the configuration, the appropriate sensor names
        will be used and the voltage will be converted through the appropriate
        conversion function. Example::

            output = {
                "temperature": 21.0,  # Celsius
                "humidity": 45.1    # %
            }

        Otherwise, the output dictionary will contain the channel numbers as key
        and the row voltage (between 0 and 255) will be returned. Example::

            output = {
                "0": 145,
                "1": 130
            }

        """

        mcp = self._get_mcp()
        values = {}

        for i in range(self.N_CHANNELS):
            value = self._convert_to_voltage(mcp.read_adc(i))

            if self.channels:
                if i in self.channels:
                    channel = self.channels[i]
                    if 'conv_function' in channel:
                        x = value  # noqa
                        value = eval(channel['conv_function'])

                    values[channel['name']] = value
            else:
                values[i] = value

        return values

    @override
    def transform_entities(self, entities: Dict[str, Numeric]) -> List[Device]:
        return [
            Device(
                id='mcp3008',
                name='MCP3008',
                children=[
                    NumericSensor(
                        id=f'mcp3008:{key}',
                        name=key,
                        value=value,
                    )
                    for key, value in entities.items()
                ],
            )
        ]


# vim:sw=4:ts=4:et:
