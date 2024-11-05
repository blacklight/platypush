import inspect
import json


class ProcedureEncoder(json.JSONEncoder):
    """
    Encoder for the Procedure model.
    """

    def default(self, o):
        from platypush.entities.procedures import ProcedureType

        if callable(o):
            return {
                'type': 'python',
                'module': o.__module__,
                'source': getattr(o, "_source", inspect.getsourcefile(o)),
                'line': getattr(o, "_line", inspect.getsourcelines(o)[1]),
                'args': [
                    name
                    for name, arg in inspect.signature(o).parameters.items()
                    if arg.kind != arg.VAR_KEYWORD
                ],
            }

        if isinstance(o, ProcedureType):
            return o.value

        return super().default(o)
