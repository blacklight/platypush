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
    def write(self, filename, content):
        """
        Writes content to a specified filename. Previous content will be truncated.

        :param filename: Path of the file
        :type filename: str

        :param content: Content to write
        :type content: str
        """

        with open(filename, 'w') as f:
            f.write(content)

    @action
    def append(self, filename, content):
        """
        Append content to a specified filename

        :param filename: Path of the file
        :type filename: str

        :param content: Content to write
        :type content: str
        """

        with open(filename, 'a') as f:
            f.write(content)

# vim:sw=4:ts=4:et:

