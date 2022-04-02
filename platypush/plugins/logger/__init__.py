from platypush.plugins import Plugin, action


class LoggerPlugin(Plugin):
    """
    Plugin to log traces on the standard Platypush logger
    """

    @action
    def trace(self, msg, *args, **kwargs):
        """
        logger.trace wrapper
        """
        self.logger.trace(msg, *args, **kwargs)

    @action
    def debug(self, msg, *args, **kwargs):
        """
        logger.debug wrapper
        """
        self.logger.debug(msg, *args, **kwargs)

    @action
    def info(self, msg, *args, **kwargs):
        """
        logger.info wrapper
        """
        self.logger.info(msg, *args, **kwargs)

    @action
    def warning(self, msg, *args, **kwargs):
        """
        logger.warning wrapper
        """
        self.logger.warning(msg, *args, **kwargs)

    @action
    def error(self, msg, *args, **kwargs):
        """
        logger.error wrapper
        """
        self.logger.error(msg, *args, **kwargs)

    @action
    def exception(self, exception, *args, **kwargs):
        """
        logger.exception wrapper
        """
        self.logger.exception(exception, *args, **kwargs)


# vim:sw=4:ts=4:et:

