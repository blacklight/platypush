import os

from platypush.plugins import Plugin, action


class FilePlugin(Plugin):
    """
    A plugin for general-purpose file methods
    """

    @classmethod
    def _get_path(cls, filename):
        return os.path.abspath(os.path.expanduser(filename))

    @action
    def get(self, filename):
        """
        Gets the content of a file

        :param filename: Path of the file
        :type filename: str
        """

        with open(self._get_path(filename), 'r') as f:
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

        with open(self._get_path(filename), 'w') as f:
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

        with open(self._get_path(filename), 'a') as f:
            f.write(content)

    @action
    def getsize(self, filename):
        """
        Get the size of the specified filename in bytes
        """
        return os.path.getsize(filename)

# vim:sw=4:ts=4:et:

