from enum import IntEnum


class ParseState(IntEnum):
    """
    Parse state.
    """

    DOC = 0
    PARAM = 1
    TYPE = 2
    RETURN = 3
