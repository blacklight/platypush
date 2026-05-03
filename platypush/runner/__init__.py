import multiprocessing
import sys

from ._runner import ApplicationRunner


def _ensure_fork_start_method():
    """
    Python >= 3.14 defaults to ``forkserver`` on Linux, which requires
    picklable process targets and is incompatible with several debuggers
    (e.g. PyCharm's pydevd).  Platypush is POSIX-only and expects ``fork``
    semantics, so we restore it here before any process is created.
    """
    try:
        multiprocessing.set_start_method('fork')
    except RuntimeError:
        pass


def main():
    """
    Main application entry point.

    This is usually the entry point that you want to use to start your
    application, rather than :meth:`platypush.app.main`, as this entry point
    wraps the main application in a controllable process.
    """

    _ensure_fork_start_method()
    app_runner = ApplicationRunner()
    app_runner.run(*sys.argv[1:])


__all__ = ["ApplicationRunner", "main"]
