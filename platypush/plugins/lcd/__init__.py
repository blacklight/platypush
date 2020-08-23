from abc import ABC, abstractmethod
from typing import List, Optional

from platypush.plugins import Plugin, action


class LcdPlugin(Plugin, ABC):
    """
    Abstract class for plugins to communicate with LCD displays.

    Requires:

        * **RPLCD** (``pip install RPLCD``)
        * **RPi.GPIO** (``pip install RPi.GPIO``)

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lcd = None

    @staticmethod
    def _get_pin_mode(pin_mode: str) -> int:
        import RPi.GPIO
        pin_modes = ['BOARD', 'BCM']
        pin_mode = pin_mode.upper()
        assert pin_mode in pin_modes, 'Invalid pin_mode: {}. Supported modes: {}'.format(pin_mode, pin_modes)
        return getattr(RPi.GPIO, pin_mode).value

    @abstractmethod
    def _get_lcd(self):
        pass

    def _init_lcd(self):
        if self.lcd:
            return

        self.lcd = self._get_lcd()

    @action
    def close(self, clear: bool = False):
        """
        Close the handler to the LCD display and release the GPIO resources.

        :param clear: Clear the display as well on close (default: False).
        """
        if self.lcd:
            self.lcd.close(clear=clear)
            self.lcd = None

    @action
    def clear(self):
        """
        Clear the LCD display.
        """
        self._init_lcd()
        self.lcd.clear()

    @action
    def home(self):
        """
        Set cursor to initial position and reset any shifting.
        """
        self._init_lcd()
        self.lcd.home()

    @action
    def shift_display(self, amount: int):
        """
        Set cursor to initial position and reset any shifting.
        """
        self._init_lcd()
        self.lcd.shift_display(amount)

    @action
    def write_string(self, value: str, position: Optional[List[int]] = None):
        """
        Write a string to the display.

        :param value: String to be displayed.
        :param position: String position on the display as a 2-int list.
        """
        self._init_lcd()
        if position:
            self.lcd.cursor_pos = tuple(position)

        self.lcd.write_string(value)

    @action
    def set_cursor_pos(self, position: List[int]):
        """
        Change the position of the cursor on the display.

        :param position: New cursor position, as a list of two elements.
        """
        self._init_lcd()
        self.lcd.cursor_pos = tuple(position)

    @action
    def set_text_align(self, mode: str):
        """
        Change the text align mode.

        :param mode: Supported values: ``left``, ``right``.
        """
        modes = ['left', 'right']
        mode = mode.lower()
        assert mode in modes, 'Unsupported text mode: {}. Supported modes: {}'.format(
            mode, modes)

        self._init_lcd()
        self.lcd.text_align_mode = mode

    @action
    def enable_display(self):
        """
        Turn on the display.
        """
        self._init_lcd()
        self.lcd.display_enabled = True

    @action
    def disable_display(self):
        """
        Turn off the display.
        """
        self._init_lcd()
        self.lcd.display_enabled = False

    @action
    def toggle_display(self):
        """
        Toggle the display state.
        """
        self._init_lcd()
        self.lcd.display_enabled = not self.lcd.display_enabled

    @action
    def enable_backlight(self):
        """
        Enable the display backlight.
        """
        self._init_lcd()
        self.lcd.backlight_enabled = True

    @action
    def disable_backlight(self):
        """
        Disable the display backlight.
        """
        self._init_lcd()
        self.lcd.backlight_enabled = False

    @action
    def toggle_backlight(self):
        """
        Toggle the display backlight on/off.
        """
        self._init_lcd()
        self.lcd.backlight_enabled = not self.lcd.backlight_enabled

    @action
    def create_char(self, location: int, bitmap: List[int]):
        """
        Create a new character.
        The HD44780 supports up to 8 custom characters (location 0-7).

        :param location: The place in memory where the character is stored.
            Values need to be integers between 0 and 7.
        :param bitmap: The bitmap containing the character. This should be a
            list of 8 numbers, each representing a 5 pixel row.

        Example for the smiley character:

            .. code-block:: python

                [
                    0,   # 0b00000
                    10,  # 0b01010
                    10,  # 0b01010
                    0,   # 0b00000
                    17,  # 0b10001
                    17,  # 0b10001
                    14,  # 0b01110
                    0    # 0b00000
                ]

        """
        self._init_lcd()
        self.lcd.create_char(location=location, bitmap=tuple(bitmap))

    @action
    def command(self, value: int):
        """
        Send a raw command to the LCD.

        :param value: Command to be sent.
        """
        self._init_lcd()
        self.lcd.command(value)

    @action
    def write(self, value: int):
        """
        Write a raw byte to the LCD.

        :param value: Byte to be sent.
        """
        self._init_lcd()
        self.lcd.write(value)

    @action
    def cr(self):
        """
        Write a carriage return (``\\r``) character to the LCD.
        """
        self._init_lcd()
        self.lcd.cr()

    @action
    def lf(self):
        """
        Write a line feed (``\\n``) character to the LCD.
        """
        self._init_lcd()
        self.lcd.lf()

    @action
    def crlf(self):
        """
        Write a carriage return + line feed (``\\r\\n``) sequence to the LCD.
        """
        self._init_lcd()
        self.lcd.crlf()


# vim:sw=4:ts=4:et:
