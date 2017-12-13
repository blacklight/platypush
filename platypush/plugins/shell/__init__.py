import subprocess

from platypush.response import Response

from .. import Plugin

class ShellPlugin(Plugin):
    def exec(self, cmd):
        output = None
        error = None

        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            error = e.output.decode('utf-8')

        return Response(output=output, errors=[error])

# vim:sw=4:ts=4:et:

