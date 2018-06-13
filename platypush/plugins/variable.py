from platypush.message.response import Response
from platypush.plugins import Plugin


class VariablePlugin(Plugin):
    """
    This plugin allows you to manipulate context variables that can be
    accessed across your tasks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variables = {}

    def get(self, name, default_value=None):
        return Response(output={name: self._variables.get(name, default_value)})

    def set(self, name, value):
        self._variables[name] = value
        return Response(output={'status':'ok'})

    def unset(self, name):
        if name in self._variables:
            del self._variables[name]
            return Response(output={'status':'ok'})
        else:
            return Response(output={'status':'not_found'})


# vim:sw=4:ts=4:et:

