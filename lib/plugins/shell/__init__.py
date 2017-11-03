import subprocess

from .. import Plugin

class ShellPlugin(Plugin):
    def run(self, args):
        if 'cmd' not in args:
            raise RuntimeError('No cmd parameter specified')

        cmd = args['cmd']
        output = None
        error = None

        try:
            output = subprocess.check_output(cmd,
                                             stderr=subprocess.STDOUT,
                                             shell=True)
        except subprocess.CalledProcessError as e:
            error = e.output

        return [output, error]

# vim:sw=4:ts=4:et:

