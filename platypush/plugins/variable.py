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
        """
        Get the value of a variable by name.

        :param name: Variable name
        :type name: str

        :param default_value: What will be returned if the variable is not defined (default: None)

        :returns: A map in the format ``{"<name>":"<value>"}``
        """

        return Response(output={name: self._variables.get(name, default_value)})

    def set(self, **kwargs):
        """
        Set a variable or a set of variables.

        :param kwargs: Key-value list of variables to set (e.g. ``foo='bar', answer=42``)
        """

        for (name, value) in kwargs.items():
            self._variables[name] = value
        return Response(output=kwargs)

    def unset(self, name):
        """
        Unset a variable by name if it's set

        :param name: Name of the variable to remove
        :type name: str
        """
        if name in self._variables:
            del self._variables[name]
            return Response(output={'status':'ok'})
        else:
            return Response(output={'status':'not_found'})


# vim:sw=4:ts=4:et:

