import re
from typing import Optional, Type


def type_str(t: Optional[Type]) -> Optional[str]:
    """
    :return: A human-readable representation of a type.
    """
    if not t:
        return None

    return re.sub(r"<class '(.*)'>", r'\1', str(t).replace('typing.', ''))
