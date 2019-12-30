from typing import List

from platypush.plugins import Plugin, action


class InputsPlugin(Plugin):
    """
    This plugin emulates user input on a keyboard/mouse. It requires the a graphical server (X server or Mac/Win
    interface) to be running - it won't work in console mode.

    Requires:

        * **pyuserinput** (``pip install pyuserinput``)

    """

    @staticmethod
    def _get_keyboard():
        # noinspection PyPackageRequirements
        from pykeyboard import PyKeyboard
        return PyKeyboard()

    @staticmethod
    def _get_mouse():
        # noinspection PyPackageRequirements
        from pymouse import PyMouse
        return PyMouse()

    @classmethod
    def _parse_key(cls, key: str):
        k = cls._get_keyboard()
        keymap = {
            'ctrl': k.control_key,
            'alt': k.alt_key,
            'meta': k.windows_l_key,
            'shift': k.shift_key,
            'enter': k.enter_key,
            'tab': k.tab_key,
            'home': k.home_key,
            'end': k.end_key,
            'capslock': k.caps_lock_key,
            'back': k.backspace_key,
            'del': k.delete_key,
            'up': k.up_key,
            'down': k.down_key,
            'left': k.left_key,
            'right': k.right_key,
            'pageup': k.page_up_key,
            'pagedown': k.page_down_key,
            'esc': k.escape_key,
            'find': k.find_key,
            'f1': k.function_keys[1],
            'f2': k.function_keys[2],
            'f3': k.function_keys[3],
            'f4': k.function_keys[4],
            'f5': k.function_keys[5],
            'f6': k.function_keys[6],
            'f7': k.function_keys[7],
            'f8': k.function_keys[8],
            'f9': k.function_keys[9],
            'f10': k.function_keys[10],
            'f11': k.function_keys[11],
            'f12': k.function_keys[12],
            'help': k.help_key,
            'media_next': k.media_next_track_key,
            'media_prev': k.media_prev_track_key,
            'media_play': k.media_play_pause_key,
            'menu': k.menu_key,
            'numlock': k.num_lock_key,
            'print': k.print_key,
            'print_screen': k.print_screen_key,
            'sleep': k.sleep_key,
            'space': k.space_key,
            'voldown': k.volume_down_key,
            'volup': k.volume_up_key,
            'volmute': k.volume_mute_key,
            'zoom': k.zoom_key,
        }

        lkey = key.lower()
        if lkey in keymap:
            return keymap[lkey]

        return key

    @action
    def press_key(self, key: str):
        """
        Emulate the pressure of a key.
        :param key: Key to be pressed
        """
        kbd = self._get_keyboard()
        key = self._parse_key(key)
        kbd.press_key(key)

    @action
    def release_key(self, key: str):
        """
        Release a pressed key.
        :param key: Key to be released
        """
        kbd = self._get_keyboard()
        key = self._parse_key(key)
        kbd.release_key(key)

    @action
    def press_keys(self, keys: List[str]):
        """
        Emulate the pressure of multiple keys.
        :param keys: List of keys to be pressed.
        """
        kbd = self._get_keyboard()
        keys = [self._parse_key(k) for k in keys]
        kbd.press_keys(keys)

    @action
    def tap_key(self, key: str, repeat: int = 1, interval: float = 0):
        """
        Emulate a key tap.
        :param key: Key to be pressed
        :param repeat: Number of iterations (default: 1)
        :param interval: Repeat interval in seconds (default: 0)
        """
        kbd = self._get_keyboard()
        key = self._parse_key(key)
        kbd.tap_key(key, n=repeat, interval=interval)

    @action
    def type_string(self, string: str, interval: float = 0):
        """
        Type a string.
        :param string: String to be typed
        :param interval: Interval between key strokes in seconds (default: 0)
        """
        kbd = self._get_keyboard()
        kbd.type_string(string, interval=interval)

    @action
    def get_screen_size(self) -> List[int]:
        """
        Get the size of the screen in pixels.
        """
        m = self._get_mouse()
        return [m.screen_size()]

    @action
    def mouse_click(self, x: int, y: int, btn: int, repeat: int = 1):
        """
        Mouse click.
        :param x: x screen position
        :param y: y screen position
        :param btn: Button number (1 for left, 2 for right, 3 for middle)
        :param repeat: Number of clicks (default: 1)
        """
        m = self._get_mouse()
        m.click(x, y, btn, n=repeat)


# vim:sw=4:ts=4:et:
