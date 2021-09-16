import enum
import os
from typing import Optional, Union, Tuple, List

from PIL import Image, ImageFont

from platypush.plugins import Plugin, action


class DeviceInterface(enum.Enum):
    I2C = 'i2c'
    SPI = 'spi'


class DeviceSlot(enum.IntEnum):
    BACK = 0
    FRONT = 1


class DeviceRotation(enum.IntEnum):
    ROTATE_0 = 0
    ROTATE_90 = 1
    ROTATE_180 = 2
    ROTATE_270 = 3


class LumaOledPlugin(Plugin):
    """
    Plugin to interact with small OLED-based RaspberryPi displays through the luma.oled driver.

    Requires:

        * **luma.oled** (``pip install git+https://github.com/rm-hull/luma.oled``)

    """

    def __init__(self,
                 interface: str,
                 device: str,
                 port: int = 0,
                 slot: int = DeviceSlot.BACK.value,
                 width: int = 128,
                 height: int = 64,
                 rotate: int = DeviceRotation.ROTATE_0.value,
                 gpio_DC: int = 24,
                 gpio_RST: int = 25,
                 bus_speed_hz: int = 8000000,
                 address: int = 0x3c,
                 cs_high: bool = False,
                 transfer_size: int = 4096,
                 spi_mode: Optional[int] = None,
                 font: Optional[str] = None,
                 font_size: int = 10,
                 **kwargs):
        """
        :param interface: Serial interface the display is connected to (``spi`` or ``i2c``).
        :param device: Display chipset type (supported: ssd1306 ssd1309, ssd1322, ssd1325, ssd1327, ssd1331, ssd1351, ssd1362, sh1106).
		:param port: Device port (usually 0 or 1).
        :param slot: Device slot (0 for back, 1 for front).
        :param width: Display width.
        :param height: Display height.
        :param rotate: Display rotation (0 for no rotation, 1 for 90 degrees, 2 for 180 degrees, 3 for 270 degrees).
        :param gpio_DC: [SPI only] GPIO PIN used for data (default: 24).
        :param gpio_RST: [SPI only] GPIO PIN used for RST (default: 25).
        :param bus_speed_hz: [SPI only] Bus speed in Hz (default: 8 MHz).
        :param address: [I2C only] Device address (default: 0x3c).
        :param cs_high: [SPI only] Set to True if the SPI chip select is high.
        :param transfer_size: [SPI only] Maximum amount of bytes to transfer in one go (default: 4096).
        :param spi_mode: [SPI only] SPI mode as two bit pattern of clock polarity and phase [CPOL|CPHA], 0-3 (default:None).
        :param font: Path to a default TTF font used to display the text.
        :param font_size: Font size - it only applies if ``font`` is set.
        """
        import luma.core.interface.serial as serial
        import luma.oled.device
        from luma.core.render import canvas

        super().__init__(**kwargs)

        iface_name = interface
        interface = getattr(serial, DeviceInterface(interface).value)

        if iface_name == DeviceInterface.SPI.value:
            self.serial = interface(port=port, device=slot, cs_high=cs_high, gpio_DC=gpio_DC,
                                    gpio_RST=gpio_RST, bus_speed_hz=bus_speed_hz,
                                    transfer_size=transfer_size, spi_mode=spi_mode)
        else:
            self.serial = interface(port=port, address=address)

        device = getattr(luma.oled.device, device)
        self.device = device(self.serial, width=width, height=height, rotate=rotate)
        self.canvas = canvas(self.device)
        self.font = None
        self.font_size = font_size
        self.font = self._get_font(font, font_size)

    def _get_font(self, font: Optional[str] = None, font_size: Optional[int] = None):
        if font:
            return ImageFont.truetype(os.path.abspath(os.path.expanduser(font)), font_size or self.font_size)

        return self.font

    @action
    def clear(self):
        """
        clear the display canvas.
        """
        from luma.core.render import canvas
        self.device.clear()
        del self.canvas
        self.canvas = canvas(self.device)

    @action
    def text(self, text: str, pos: Union[Tuple[int], List[int]] = (0, 0),
             fill: str = 'white', font: Optional[str] = None, font_size: Optional[int] = None, clear: bool = False):
        """
        Draw text on the canvas.

        :param text: Text to be drawn.
        :param pos: Position of the text.
        :param fill: Text color (default: ``white``).
        :param font: ``font`` type override.
        :param font_size: ``font_size`` override.
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        font = self._get_font(font, font_size)

        with self.canvas as draw:
            draw.text(pos, text, fill=fill, font=font)

    @action
    def rectangle(self, xy: Optional[Union[Tuple[int], List[int]]] = None,
                  fill: Optional[str] = None, outline: Optional[str] = None,
                  width: int = 1, clear: bool = False):
        """
        Draw a rectangle on the canvas.

        :param xy: Two points defining the bounding box, either as [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]. Default: bounding box of the device.
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param width: Figure width in pixels (default: 1).
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.rectangle(xy, outline=outline, fill=fill, width=width)

    @action
    def arc(self, start: int, end: int, xy: Optional[Union[Tuple[int], List[int]]] = None,
            fill: Optional[str] = None, outline: Optional[str] = None,
            width: int = 1, clear: bool = False):
        """
        Draw an arc on the canvas.

        :param start: Starting angle, in degrees (measured from 3 o' clock and increasing clockwise).
        :param end: Ending angle, in degrees (measured from 3 o' clock and increasing clockwise).
        :param xy: Two points defining the bounding box, either as [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]. Default: bounding box of the device.
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param width: Figure width in pixels (default: 1).
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.arc(xy, start=start, end=end, outline=outline, fill=fill, width=width)

    @action
    def chord(self, start: int, end: int, xy: Optional[Union[Tuple[int], List[int]]] = None,
              fill: Optional[str] = None, outline: Optional[str] = None,
              width: int = 1, clear: bool = False):
        """
        Same as ``arc``, but it connects the end points with a straight line.

        :param start: Starting angle, in degrees (measured from 3 o' clock and increasing clockwise).
        :param end: Ending angle, in degrees (measured from 3 o' clock and increasing clockwise).
        :param xy: Two points defining the bounding box, either as [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]. Default: bounding box of the device.
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param width: Figure width in pixels (default: 1).
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.chord(xy, start=start, end=end, outline=outline, fill=fill, width=width)

    @action
    def pieslice(self, start: int, end: int, xy: Optional[Union[Tuple[int], List[int]]] = None,
                 fill: Optional[str] = None, outline: Optional[str] = None,
                 width: int = 1, clear: bool = False):
        """
        Same as ``arc``, but it also draws straight lines between the end points and the center of the bounding box.

        :param start: Starting angle, in degrees (measured from 3 o' clock and increasing clockwise).
        :param end: Ending angle, in degrees (measured from 3 o' clock and increasing clockwise).
        :param xy: Two points defining the bounding box, either as [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]. Default: bounding box of the device.
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param width: Figure width in pixels (default: 1).
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.pieslice(xy, start=start, end=end, outline=outline, fill=fill, width=width)

    @action
    def ellipse(self, xy: Optional[Union[Tuple[int], List[int]]] = None,
                fill: Optional[str] = None, outline: Optional[str] = None,
                width: int = 1, clear: bool = False):
        """
        Draw an ellipse on the canvas.

        :param xy: Two points defining the bounding box, either as [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]. Default: bounding box of the device.
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param width: Figure width in pixels (default: 1).
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.ellipse(xy, outline=outline, fill=fill, width=width)

    @action
    def line(self, xy: Optional[Union[Tuple[int], List[int]]] = None,
             fill: Optional[str] = None, outline: Optional[str] = None,
             width: int = 1, curve: bool = False, clear: bool = False):
        """
        Draw a line on the canvas.

        :param xy: Sequence of either 2-tuples like [(x, y), (x, y), ...] or numeric values like [x, y, x, y, ...].
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param width: Figure width in pixels (default: 1).
        :param curve: Set to True for rounded edges (default: False).
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.line(xy, outline=outline, fill=fill, width=width, joint='curve' if curve else None)

    @action
    def point(self, xy: Optional[Union[Tuple[int], List[int]]] = None,
              fill: Optional[str] = None, clear: bool = False):
        """
        Draw one or more points on the canvas.

        :param xy: Sequence of either 2-tuples like [(x, y), (x, y), ...] or numeric values like [x, y, x, y, ...].
        :param fill: Fill color - can be ``black`` or ``white``.
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.point(xy, fill=fill)

    @action
    def polygon(self, xy: Optional[Union[Tuple[int], List[int]]] = None,
                fill: Optional[str] = None, outline: Optional[str] = None,
                clear: bool = False):
        """
        Draw a polygon on the canvas.

        :param xy: Sequence of either 2-tuples like [(x, y), (x, y), ...] or numeric values like [x, y, x, y, ...].
        :param fill: Fill color - can be ``black`` or ``white``.
        :param outline: Outline color - can be ``black`` or ``white``.
        :param clear: Set to True if you want to clear the canvas before writing the text (default: False).
        """
        if clear:
            self.clear()

        if not xy:
            xy = self.device.bounding_box

        with self.canvas as draw:
            draw.polygon(xy, outline=outline, fill=fill)

    @action
    def image(self, image: str):
        """
        Draws an image to the canvas (this will clear the existing canvas).

        :param image: Image path.
        """
        image = Image.open(os.path.abspath(os.path.expanduser(image)))
        self.clear()
        self.device.display(image)


# vim:sw=4:ts=4:et:
