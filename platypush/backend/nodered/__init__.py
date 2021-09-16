import inspect
import os
import subprocess
import sys

from platypush.backend import Backend


class NoderedBackend(Backend):
    """
    This backend publishes platypush actions to a Node-RED instance.
    If you enable this backend on a host that runs Node-RED then a new block (platypush -> run) can be
    used in your flows. This block will accept JSON requests as input in the format
    ``{"type":"request", "action":"plugin.name.action_name", "args": {...}}`` and return the output
    of the action as block output, or raise an exception if the action failed.

    Requires:

        * **pynodered** (``pip install pynodered``)

    """

    def __init__(self, port: int = 5051, *args, **kwargs):
        """
        :param port: Listening port for the local publishing web server (default: 5051)
        """
        super().__init__(*args, **kwargs)
        self.port = port
        self._runner_path = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), 'runner.py')
        self._server = None

    def on_stop(self):
        super().on_stop()
        if self._server:
            self._server.terminate()
            self._server = None

    def run(self):
        super().run()
        self.register_service(port=self.port, name='node')

        self._server = subprocess.Popen([sys.executable, '-m', 'pynodered.server',
                                         '--port', str(self.port), self._runner_path])

        self.logger.info('Started Node-RED backend on port {}'.format(self.port))
        self._server.wait()


# vim:sw=4:ts=4:et:
