import re
from typing_extensions import override

from ._base import Parser


class EventParser(Parser):
    """
    Parse event references in the docstrings with rendered links to their
    respective documentation.
    """

    _event_regex = re.compile(
        r'(\s*):class:`(platypush\.message\.event\.(.+?))`', re.MULTILINE
    )

    @override
    @classmethod
    def parse(cls, docstring: str, *_, **__) -> str:
        while True:
            m = cls._event_regex.search(docstring)
            if not m:
                break

            class_name = m.group(3).split('.')[-1]
            package = '.'.join(m.group(3).split('.')[:-1])
            docstring = cls._event_regex.sub(
                f'{m.group(1)}`{class_name} '
                f'<https://docs.platypush.tech/platypush/events/{package}.html#{m.group(2)}>`_',
                docstring,
                count=1,
            )

        return docstring
