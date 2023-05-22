import re
from typing_extensions import override

from ._base import Parser


class MethodParser(Parser):
    """
    Parse method references in the docstrings with rendered links to their
    respective documentation.
    """

    _method_regex = re.compile(
        r'(\s*):meth:`(platypush\.plugins\.(.+?))`', re.MULTILINE
    )

    @override
    @classmethod
    def parse(cls, docstring: str) -> str:
        while True:
            m = cls._method_regex.search(docstring)
            if not m:
                break

            tokens = m.group(3).split('.')
            method = tokens[-1]
            package = '.'.join(tokens[:-2])
            docstring = cls._method_regex.sub(
                f'{m.group(1)}`{package}.{method} '
                f'<https://docs.platypush.tech/platypush/plugins/{package}.html#{m.group(2)}>`_',
                docstring,
                count=1,
            )

        return docstring
