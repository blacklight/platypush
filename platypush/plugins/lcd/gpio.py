from typing import List, Optional

from platypush.plugins.lcd import LcdPlugin


class LcdGpioPlugin(LcdPlugin):
    """
    Plugin to write to an LCD display connected via GPIO.

    Requires:

        * **RPLCD** (``pip install RPLCD``)
        * **RPi.GPIO** (``pip install RPi.GPIO``)

    """

    def __init__(self, pin_rs: int, pin_e: int, pins_data: List[int],
                 pin_rw: Optional[int] = None, pin_mode: str = 'BOARD',
                 pin_backlight: Optional[int] = None,
                 cols: int = 16, rows: int = 2,
                 backlight_enabled: bool = True,
                 backlight_mode: str = 'active_low',
                 dotsize: int = 8, charmap: str = 'A02',
                 auto_linebreaks: bool = True,
                 compat_mode: bool = False, **kwargs):
        """
        :param pin_rs: Pin for register select (RS).
        :param pin_e: Pin to start data read or write (E).
        :param pins_data: List of data bus pins in 8 bit mode (DB0-DB7) or in 4
            bit mode (DB4-DB7) in ascending order.
        :param pin_mode: Which scheme to use for numbering of the GPIO pins,
            either ``BOARD`` or ``BCM``. Default: ``BOARD``.
        :param pin_rw: Pin for selecting read or write mode (R/W). Default:
            ``None``, read only mode.
        :param pin_backlight: Pin for controlling backlight on/off. Set this to
            ``None`` for no backlight control. Default: ``None``.
        :param cols: Number of columns per row (usually 16 or 20). Default: ``16``.
        :param rows: Number of display rows (usually 1, 2 or 4). Default: ``2``.
        :param backlight_enabled: Whether the backlight is enabled initially.
            Default: ``True``. Has no effect if pin_backlight is ``None``
        :param backlight_mode: Set this to either ``active_high`` or ``active_low``
            to configure the operating control for the backlight. Has no effect if
            pin_backlight is ``None``
        :param dotsize: Some 1 line displays allow a font height of 10px.
            Allowed: ``8`` or ``10``. Default: ``8``.
        :param charmap: The character map used. Depends on your LCD. This must
            be either ``A00`` or ``A02`` or ``ST0B``. Default: ``A02``.
        :param auto_linebreaks: Whether or not to automatically insert line
            breaks. Default: ``True``.
        :param compat_mode: Whether to run additional checks to support older LCDs
            that may not run at the reference clock (or keep up with it).
            Default: ``False``.
        """
        super().__init__(**kwargs)

        self.pin_mode = self._get_pin_mode(pin_mode)
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pin_rw = pin_rw
        self.pin_backlight = pin_backlight
        self.pins_data = pins_data
        self.cols = cols
        self.rows = rows
        self.backlight_enabled = backlight_enabled
        self.backlight_mode = backlight_mode
        self.dotsize = dotsize
        self.auto_linebreaks = auto_linebreaks
        self.compat_mode = compat_mode
        self.charmap = charmap

    def _get_lcd(self):
        from RPLCD.gpio import CharLCD
        return CharLCD(cols=self.cols, rows=self.rows, pin_rs=self.pin_rs,
                       pin_e=self.pin_e, pins_data=self.pins_data,
                       numbering_mode=self.pin_mode, pin_rw=self.pin_rw,
                       pin_backlight=self.pin_backlight,
                       backlight_enabled=self.backlight_enabled,
                       backlight_mode=self.backlight_mode,
                       dotsize=self.dotsize, charmap=self.charmap,
                       auto_linebreaks=self.auto_linebreaks,
                       compat_mode=self.compat_mode)


# vim:sw=4:ts=4:et:
