from typing import Optional

from platypush.plugins.lcd import LcdPlugin


class LcdI2cPlugin(LcdPlugin):
    """
    Plugin to write to an LCD display connected via I2C.
    Adafruit I2C/SPI LCD Backback is supported.

    Warning: You might need a level shifter (that supports i2c)
    between the SCL/SDA connections on the MCP chip / backpack and the Raspberry Pi.
    Or you might damage the Pi and possibly any other 3.3V i2c devices
    connected on the i2c bus. Or cause reliability issues. The SCL/SDA are rated 0.7*VDD
    on the MCP23008, so it needs 3.5V on the SCL/SDA when 5V is applied to drive the LCD.
    The MCP23008 and MCP23017 needs to be connected exactly the same way as the backpack.
    For complete schematics see the adafruit page at:
    https://learn.adafruit.com/i2c-spi-lcd-backpack/
    4-bit operation. I2C only supported.

    Pin mapping::

        7  | 6  | 5  | 4  | 3  | 2 | 1  | 0
        BL | D7 | D6 | D5 | D4 | E | RS | -

    Requires:

        * **RPLCD** (``pip install RPLCD``)
        * **RPi.GPIO** (``pip install RPi.GPIO``)

    """

    def __init__(self, i2c_expander: str, address: int,
                 expander_params: Optional[dict] = None,
                 port: int = 1, cols: int = 16, rows: int = 2,
                 backlight_enabled: bool = True,
                 dotsize: int = 8, charmap: str = 'A02',
                 auto_linebreaks: bool = True, **kwargs):
        """
        :param i2c_expander: Set your I²C chip type. Supported: "PCF8574", "MCP23008", "MCP23017".
        :param address: The I2C address of your LCD.
        :param expander_params: Parameters for expanders, in a dictionary. Only needed for MCP23017
            gpio_bank - This must be either ``A`` or ``B``. If you have a HAT, A is usually marked 1 and B is 2.
            Example: ``expander_params={'gpio_bank': 'A'}``
        :param port: The I2C port number. Default: ``1``.
        :param cols: Number of columns per row (usually 16 or 20). Default: ``16``.
        :param rows: Number of display rows (usually 1, 2 or 4). Default: ``2``.
        :param backlight_enabled: Whether the backlight is enabled initially.  Default: ``True``. Has no effect if pin_backlight is ``None``
        :param dotsize: Some 1 line displays allow a font height of 10px.  Allowed: ``8`` or ``10``. Default: ``8``.
        :param charmap: The character map used. Depends on your LCD. This must be either ``A00`` or ``A02`` or ``ST0B``. Default: ``A02``.
        :param auto_linebreaks: Whether or not to automatically insert line breaks. Default: ``True``.
        """
        super().__init__(**kwargs)

        self.i2c_expander = i2c_expander
        self.address = address
        self.expander_params = expander_params or {}
        self.port = port
        self.cols = cols
        self.rows = rows
        self.backlight_enabled = backlight_enabled
        self.dotsize = dotsize
        self.auto_linebreaks = auto_linebreaks
        self.charmap = charmap

    def _get_lcd(self):
        from RPLCD.i2c import CharLCD
        return CharLCD(cols=self.cols, rows=self.rows,
                       i2c_expander=self.i2c_expander,
                       address=self.address, port=self.port,
                       backlight_enabled=self.backlight_enabled,
                       dotsize=self.dotsize, charmap=self.charmap,
                       auto_linebreaks=self.auto_linebreaks)


class LcdI2CPlugin(LcdI2cPlugin):
    pass


# vim:sw=4:ts=4:et:
