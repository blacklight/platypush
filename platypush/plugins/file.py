from platypush.plugins import Plugin, action


class FilePlugin(Plugin):
    """
    A plugin for general-purpose file methods
    """

    @action
    def get(self, filename):
        """
        Gets the content of a file

        :param filename: Path of the file
        :type filename: str
        """

        with open(filename, 'r') as f:
            return f.read()

    @action
    def write(self, filename, content, append=False):
        """
        Writes content to a specified filename

        :param filename: Path of the file
        :type filename: str

        :param content: Content to write
        :type content: str

        :param append: If set, the content will be appended to the file (default: False, truncate file upon write)
        :type append: bool
        """

        mode = 'a' if append else 'w'
        with open(filename, mode) as f:
            f.write(content)

# vim:sw=4:ts=4:et:

