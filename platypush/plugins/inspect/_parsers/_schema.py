import importlib
import inspect
import json
import os
from random import randint
import re
import textwrap
from typing_extensions import override

from marshmallow import fields

import platypush.schemas

from ._base import Parser


class SchemaParser(Parser):
    """
    Support for response/message schemas in the docs. Format: ``.. schema:: rel_path.SchemaClass(arg1=value1, ...)``,
    where ``rel_path`` is the path of the schema relative to ``platypush/schemas``.
    """

    _schemas_path = os.path.dirname(inspect.getfile(platypush.schemas))
    _schema_regex = re.compile(
        r'^(\s*)\.\.\s+schema::\s*([a-zA-Z0-9._]+)\s*(\((.+?)\))?', re.MULTILINE
    )

    @classmethod
    def _get_field_value(cls, field):
        metadata = getattr(field, 'metadata', {})
        if metadata.get('example'):
            return metadata['example']
        if metadata.get('description'):
            return metadata['description']

        if isinstance(field, fields.Number):
            return randint(1, 99)
        if isinstance(field, fields.Boolean):
            return bool(randint(0, 1))
        if isinstance(field, fields.URL):
            return 'https://example.org'
        if isinstance(field, fields.List):
            return [cls._get_field_value(field.inner)]
        if isinstance(field, fields.Dict):
            return {
                cls._get_field_value(field.key_field)
                if field.key_field
                else 'key': cls._get_field_value(field.value_field)
                if field.value_field
                else 'value'
            }
        if isinstance(field, fields.Nested):
            ret = {
                name: cls._get_field_value(f)
                for name, f in field.nested().fields.items()
            }

            return [ret] if field.many else ret

        return str(field.__class__.__name__).lower()

    @override
    @classmethod
    def parse(cls, docstring: str, *_, **__) -> str:
        while True:
            m = cls._schema_regex.search(docstring)
            if not m:
                break

            schema_module_name = '.'.join(
                ['platypush.schemas', *(m.group(2).split('.')[:-1])]
            )
            schema_module = importlib.import_module(schema_module_name)
            schema_class = getattr(schema_module, m.group(2).split('.')[-1])
            schema_args = eval(f'dict({m.group(4)})') if m.group(4) else {}
            schema = schema_class(**schema_args)
            parsed_schema = {
                name: cls._get_field_value(field)
                for name, field in schema.fields.items()
                if not field.load_only
            }

            if schema.many:
                parsed_schema = [parsed_schema]

            padding = m.group(1)
            docstring = cls._schema_regex.sub(
                textwrap.indent('\n\n.. code-block:: json\n\n', padding)
                + textwrap.indent(
                    json.dumps(parsed_schema, sort_keys=True, indent=2),
                    padding + '  ',
                ).replace('\n\n', '\n')
                + '\n\n',
                docstring,
            )

        return docstring
