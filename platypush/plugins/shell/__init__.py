import subprocess

from platypush.message.response import Response

from .. import Plugin

class ShellPlugin(Plugin):
    def exec(self, cmd):
        output = None
        errors = []

        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            errors = [e.output.decode('utf-8')]

        return Response(output=output, errors=errors)

# vim:sw=4:ts=4:et:

