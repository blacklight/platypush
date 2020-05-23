import time
from typing import Optional

import pyperclip

from platypush.backend import Backend
from platypush.message.event.clipboard import ClipboardEvent


class ClipboardBackend(Backend):
    """
    This backend monitors for changes in the clipboard and generates even when the user copies a new text.

    Requires:

        - **pyperclip** (``pip install pyperclip``)

    Triggers:

        - :class:`platypush.message.event.clipboard.ClipboardEvent` on clipboard update.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_text: Optional[str] = None

    def run(self):
        while not self.should_stop():
            text = pyperclip.paste()
            if text and text != self._last_text:
                self.bus.post(ClipboardEvent(text=text))

            self._last_text = text
            time.sleep(0.1)


# vim:sw=4:ts=4:et:
