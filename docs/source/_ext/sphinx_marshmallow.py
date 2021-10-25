import importlib
import json
import os
import re
import sys
from random import randint
from typing import Union, List

from docutils import nodes
from docutils.parsers.rst import Directive
from marshmallow import fields


class SchemaDirective(Directive):
    """
    Support for response/message schemas in the docs. Format: ``.. schema:: rel_path.SchemaClass(arg1=value1, ...)``,
    where ``rel_path`` is the path of the schema relative to ``platypush/schemas``.
    """
    has_content = True
    _schema_regex = re.compile(r'^\s*(.+?)\s*(\((.+?)\))?\s*$')
    _schemas_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.relpath(__file__)), '..', '..', '..', 'platypush', 'schemas'))

    sys.path.insert(0, _schemas_path)

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
                cls._get_field_value(field.key_field) if field.key_field else 'key':
                    cls._get_field_value(field.value_field) if field.value_field else 'value'
            }
        if isinstance(field, fields.Nested):
            ret = {
                name: cls._get_field_value(f)
                for name, f in field.nested().fields.items()
            }

            return [ret] if field.many else ret

        return str(field.__class__.__name__).lower()

    def _parse_schema(self) -> Union[dict, List[dict]]:
        m = self._schema_regex.match('\n'.join(self.content))
        schema_module_name = '.'.join(['platypush.schemas', *(m.group(1).split('.')[:-1])])
        schema_module = importlib.import_module(schema_module_name)
        schema_class = getattr(schema_module, m.group(1).split('.')[-1])
        schema_args = eval(f'dict({m.group(3)})') if m.group(3) else {}
        schema = schema_class(**schema_args)
        output = {
            name: self._get_field_value(field)
            for name, field in schema.fields.items()
            if not field.load_only
        }

        return [output] if schema.many else output

    def run(self):
        content = json.dumps(self._parse_schema(), sort_keys=True, indent=2)
        block = nodes.literal_block(content, content)
        block['language'] = 'json'
        return [block]


def setup(app):
    app.add_directive('schema', SchemaDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
