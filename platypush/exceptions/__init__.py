from typing import Optional, Union


class PlatypushException(Exception):
    """
    Base class for all Platypush exceptions.
    """
    def __init__(self, error: Optional[Union[str, Exception]] = None, *args):
        super().__init__(*args)
        self._inner_exception = None
        self._msg = None

        if isinstance(error, str):
            self._msg = error
        elif isinstance(error, Exception):
            self._inner_exception = error
            self._msg = str(error)

    def __str__(self):
        return self._msg
