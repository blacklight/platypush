import json


class ProcedureEncoder(json.JSONEncoder):
    """
    Encoder for the Procedure model.
    """

    def default(self, o):
        if callable(o):
            return {
                'type': 'native_function',
                'source': f'{o.__module__}.{o.__name__}',
            }

        return super().default(o)
