import subprocess

from platypush.plugins import Plugin, action


class ShellPlugin(Plugin):
    """
    Plugin to run custom shell commands.
    """

    @action
    def exec(self, cmd, ignore_errors=False):
        """
        Execute a command.

        :param cmd: Command to execute
        :type cmd: str

        :param ignore_errors: If set, then any errors in the command execution will be ignored. Otherwise a RuntimeError will be thrown (default value: False)
        :returns: A response object where the ``output`` field will contain the command output as a string, and the ``errors`` field will contain whatever was sent to stderr.
        """

        try:
            return subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            if ignore_errors:
                self.logger.warning('Command {} failed with error: {}'.format(
                    cmd, e.output.decode('utf-8')))
            else:
                raise RuntimeError(e.output.decode('utf-8'))


# vim:sw=4:ts=4:et:

