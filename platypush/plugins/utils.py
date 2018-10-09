import time

from platypush.plugins import Plugin, action


class UtilsPlugin(Plugin):
    """
    A plugin for general-purpose util methods
    """

    @action
    def sleep(self, seconds):
        """
        Make the current executor sleep for the specified number of seconds.

        :param seconds: Sleep seconds
        :type seconds: float
        """

        time.sleep(seconds)


# vim:sw=4:ts=4:et:

