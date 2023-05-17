import inspect
import json


class ProcedureEncoder(json.JSONEncoder):
    """
    Encoder for the Procedure model.
    """

    def default(self, o):
        if callable(o):
            return {
                'type': 'native_function',
                'module': o.__module__,
                'source': inspect.getsourcefile(o),
                'args': [
                    name
                    for name, arg in inspect.signature(o).parameters.items()
                    if arg.kind != arg.VAR_KEYWORD
                ],
            }

        return super().default(o)
