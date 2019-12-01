from platypush.plugins import Plugin, action


class ClipboardPlugin(Plugin):
    """
    Plugin to programmatically copy strings to your system clipboard
    and get the current clipboard content.

    Requires:
        * **pyperclip** (``pip install pyperclip``)
    """

    @action
    def copy(self, text):
        """
        Copies a text to the OS clipboard

        :param text: Text to copy
        :type text: str
        """
        import pyperclip
        pyperclip.copy(text)


    @action
    def paste(self):
        """
        Get the current content of the clipboard
        """
        import pyperclip
        return pyperclip.paste()


# vim:sw=4:ts=4:et:

