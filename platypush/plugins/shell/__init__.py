import subprocess

from platypush.message.response import Response

from .. import Plugin

class ShellPlugin(Plugin):
    """
    Plugin to run custom shell commands.
    """

    def exec(self, cmd):
        """
        Execute a command.

        :param cmd: Command to execute
        :type cmd: str

        :returns: A response object where the ``output`` field will contain the command output as a string, and the ``errors`` field will contain whatever was sent to stderr.
        """

        output = None
        errors = []

        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            errors = [e.output.decode('utf-8')]

        return Response(output=output, errors=errors)

# vim:sw=4:ts=4:et:

