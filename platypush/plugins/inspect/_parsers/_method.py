import re
from typing_extensions import override

from ._base import Parser


class MethodParser(Parser):
    """
    Parse method references in the docstrings with rendered links to their
    respective documentation.
    """

    _abs_method_regex = re.compile(
        r'(\s*):meth:`(platypush\.plugins\.(.+?))`', re.MULTILINE
    )

    _rel_method_regex = re.compile(r'(\s*):meth:`\.(.+?)`', re.MULTILINE)

    @override
    @classmethod
    def parse(cls, docstring: str, obj_type: type) -> str:
        while True:
            m = cls._rel_method_regex.search(docstring)
            if m:
                tokens = m.group(2).split('.')
                method = tokens[-1]
                package = obj_type.__module__
                rel_package = '.'.join(package.split('.')[2:])
                full_name = '.'.join(
                    [
                        package,
                        '.'.join(obj_type.__qualname__.split('.')[:-1]),
                        method,
                    ]
                )

                docstring = cls._rel_method_regex.sub(
                    f'{m.group(1)}`{package}.{method} '
                    f'<https://docs.platypush.tech/platypush/plugins/{rel_package}.html#{full_name}>`_',
                    docstring,
                    count=1,
                )

                continue

            m = cls._abs_method_regex.search(docstring)
            if m:
                tokens = m.group(3).split('.')
                method = tokens[-1]
                package = '.'.join(tokens[:-2])
                docstring = cls._abs_method_regex.sub(
                    f'{m.group(1)}`{package}.{method} '
                    f'<https://docs.platypush.tech/platypush/plugins/{package}.html#{m.group(2)}>`_',
                    docstring,
                    count=1,
                )

                continue

            break

        return docstring
