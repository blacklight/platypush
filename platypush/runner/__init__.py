from ._runner import ApplicationRunner


def main(*args: str):
    """
    Main application entry point.

    This is usually the entry point that you want to use to start your
    application, rather than :meth:`platypush.app.main`, as this entry point
    wraps the main application in a controllable process.
    """

    app_runner = ApplicationRunner()
    app_runner.run(*args)


__all__ = ["ApplicationRunner", "main"]
