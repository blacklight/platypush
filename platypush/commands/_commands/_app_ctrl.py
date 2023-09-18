from platypush.commands import Command


class StopCommand(Command):
    """
    Stop the application.
    """

    def __call__(self, app, *_, **__):
        self.logger.info('Received StopApplication command.')
        app.stop()


class RestartCommand(Command):
    """
    Restart the application.
    """

    def __call__(self, app, *_, **__):
        self.logger.info('Received RestartApplication command.')
        app.restart()
