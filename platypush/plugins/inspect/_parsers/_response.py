import re
from typing_extensions import override

from ._base import Parser


class ResponseParser(Parser):
    """
    Parse response references in the docstrings with rendered links to their
    respective documentation.
    """

    _response_regex = re.compile(
        r'(\s*):class:`(platypush\.message\.response\.(.+?))`', re.MULTILINE
    )

    @override
    @classmethod
    def parse(cls, docstring: str, *_, **__) -> str:
        while True:
            m = cls._response_regex.search(docstring)
            if not m:
                break

            class_name = m.group(3).split('.')[-1]
            package = '.'.join(m.group(3).split('.')[:-1])
            docstring = cls._response_regex.sub(
                f'{m.group(1)}`{class_name} '
                f'<https://docs.platypush.tech/platypush/responses/{package}.html#{m.group(2)}>`_',
                docstring,
                count=1,
            )

        return docstring
