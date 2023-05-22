import re
from typing_extensions import override

from ._base import Parser


class PluginParser(Parser):
    """
    Parse plugin references in the docstrings with rendered links to their
    respective documentation.
    """

    _plugin_regex = re.compile(
        r'(\s*):class:`(platypush\.plugins\.(.+?))`', re.MULTILINE
    )

    @override
    @classmethod
    def parse(cls, docstring: str, *_, **__) -> str:
        while True:
            m = cls._plugin_regex.search(docstring)
            if not m:
                break

            class_name = m.group(3).split('.')[-1]
            package = '.'.join(m.group(3).split('.')[:-1])
            docstring = cls._plugin_regex.sub(
                f'{m.group(1)}`{class_name} '
                f'<https://docs.platypush.tech/platypush/plugins/{package}.html#{m.group(2)}>`_',
                docstring,
                count=1,
            )

        return docstring
