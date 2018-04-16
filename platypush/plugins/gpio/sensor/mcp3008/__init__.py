import enum
import logging
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

from platypush.plugins.gpio.sensor import GpioSensorPlugin
from platypush.message.response import Response


class MCP3008Mode(enum.Enum):
    SOFTWARE = 'software'
    HARDWARE = 'hardware'


class GpioSensorMcp3008Plugin(GpioSensorPlugin):
    """
    Plugin to read analog sensor values from an MCP3008 chipset,
    see https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008
    Requires adafruit-mcp3008 Python package
    """

    N_CHANNELS = 8

    def __init__(self, CLK=None, MISO=None, MOSI=None, CS=None, spi_port=None,
                 spi_device=None, channels=None, Vdd=3.3, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            raise RuntimeError("At least one mode must be specified.\n" +
                               "Software SPI: Specify CLK, MISO, MOSI and CS pins\n" +
                               "Hardware SPI: Specify spi_port and spi_device\n")

        self.Vdd = Vdd
        self.channels = channels if channels else {}
        self.mcp = None


    def _get_mcp(self):
        if self.mode == MCP3008Mode.SOFTWARE:
            self.mcp = Adafruit_MCP3008.MCP3008(clk=self.CLK, cs=self.CS,
                                           miso=self.MISO, mosi=self.MOSI)
        elif self.mode == MCP3008Mode.HARDWARE:
            self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.spi_port, self.spi_device))
        else:
            raise RuntimeError('Unsupported MCP3008 mode: {}'.format(self.mode))

        return self.mcp


    def _convert_to_voltage(self, value):
        return (value * self.Vdd) / 1023.0 if value is not None else None


    def get_measurement(self):
        mcp = self._get_mcp()
        values = {}

        for i in range(self.N_CHANNELS):
            value = self._convert_to_voltage(mcp.read_adc(i))

            if self.channels:
                if i in self.channels:
                    channel = self.channels[i]
                    if 'conv_function' in channel:
                        x = value
                        value = eval(channel['conv_function'])

                    values[channel['name']] = value
            else:
                values[i] = value

        return Response(output=values)


# vim:sw=4:ts=4:et:

