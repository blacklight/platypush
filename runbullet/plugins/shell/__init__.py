import subprocess

from .. import Plugin

class ShellPlugin(Plugin):
    def exec(self, cmd):
        output = None
        error = None

        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            error = e.output

        return [output, error]

# vim:sw=4:ts=4:et:

