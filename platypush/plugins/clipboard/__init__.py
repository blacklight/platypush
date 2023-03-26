from time import time
from typing import Optional

from platypush.context import get_bus
from platypush.message.event.clipboard import ClipboardEvent
from platypush.plugins import RunnablePlugin, action


class ClipboardPlugin(RunnablePlugin):
    """
    Plugin to programmatically copy strings to your system clipboard,
    monitor and get the current clipboard content.

    Requires:

        - **pyclip** (``pip install pyclip``)

    Triggers:

        - :class:`platypush.message.event.clipboard.ClipboardEvent` on clipboard update.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_text: Optional[str] = None

    @action
    def copy(self, text):
        """
        Copies a text to the OS clipboard

        :param text: Text to copy
        :type text: str
        """
        import pyclip

        pyclip.copy(text)

    @action
    def paste(self):
        """
        Get the current content of the clipboard
        """
        import pyclip

        return pyclip.paste(text=True)

    def main(self):
        import pyclip

        last_error_time = 0

        while not self.should_stop():
            try:
                text = pyclip.paste(text=True)
                if text and text != self._last_text:
                    get_bus().post(ClipboardEvent(text=text))
                    self._last_text = text
            except Exception as e:
                if time() - last_error_time > 60:
                    last_error_time = time()
                    self.logger.error(
                        'Could not access the clipboard: %s: %s', type(e), e
                    )
            finally:
                self._should_stop.wait(0.1)

        self.logger.info('Stopped clipboard monitor backend')


# vim:sw=4:ts=4:et:
