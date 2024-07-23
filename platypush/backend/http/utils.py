import collections.abc
import datetime
import json
import logging
import os
import re

from platypush.config import Config
from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import current_user


class HttpUtils:
    """
    Common utilities used by the HTTP backend and jinja templates.
    """

    log = logging.getLogger('platypush:web')

    @staticmethod
    def widget_columns_to_html_class(columns):
        if not isinstance(columns, int):
            try:
                columns = int(columns)
            except ValueError as e:
                raise RuntimeError(
                    f'columns should be a number, got {type(columns)} ({columns})'
                ) from e

        if 1 <= columns <= 12:
            return f'col-{columns}'

        raise RuntimeError(
            'Constraint violation: should be 1 <= columns <= 12, '
            f'got columns={columns}'
        )

    @staticmethod
    def search_directory(directory, *extensions, recursive=False):
        files = []

        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if (
                        not extensions
                        or os.path.splitext(file)[1].lower() in extensions
                    ):
                        files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if not extensions or os.path.splitext(file)[1].lower() in extensions:
                    files.append(os.path.join(directory, file))

        return files

    @classmethod
    def search_web_directory(cls, directory, *extensions):
        directory = os.path.abspath(os.path.expanduser(directory))
        resource_dirs = (Config.get('backend.http') or {}).get('resource_dirs', {})
        resource_path = None
        uri = ''

        for name, resource_path in resource_dirs.items():
            resource_path = os.path.abspath(os.path.expanduser(resource_path))
            if directory.startswith(resource_path):
                uri = '/resources/' + name
                break

        if not uri:
            raise RuntimeError(
                (
                    'Directory {} not found among the available '
                    + 'static resources on the webserver'
                ).format(directory)
            )

        results = [
            re.sub(fr'^{resource_path}(.*)$', uri + '\\1', path)
            for path in cls.search_directory(directory, *extensions)
        ]

        return results

    @classmethod
    def to_json(cls, data):
        def json_parse(x):
            if isinstance(x, datetime.timedelta):
                return x.days * 24 * 60 * 60 + x.seconds + x.microseconds / 1e6

            # Ignore non-serializable attributes
            cls.log.warning('Non-serializable attribute type "%s": %s', type(x), x)
            return None

        if isinstance(data, collections.abc.KeysView):
            # Convert dict_keys to list before serializing
            data = list(data)
        return json.dumps(data, default=json_parse)

    @classmethod
    def from_json(cls, data):
        return json.loads(data)

    @classmethod
    def get_config(cls, attr):
        return Config.get(attr)

    @classmethod
    def plugin_name_to_tag(cls, module_name):
        return module_name.replace('.', '-')

    @classmethod
    def find_templates_in_dir(cls, directory):
        # noinspection PyTypeChecker
        return [
            os.path.join(directory, file)
            for _, __, files in os.walk(
                os.path.abspath(os.path.join(template_folder, directory))
            )
            for file in files
            if file.endswith('.html') or file.endswith('.htm')
        ]

    @classmethod
    def readfile(cls, file):
        with open(file) as f:
            return f.read()

    @classmethod
    def isfile(cls, *path):
        path = path[0] if len(path) == 1 else os.path.join(*path)
        return os.path.isfile(path)

    @staticmethod
    def current_user():
        return current_user()


# vim:sw=4:ts=4:et:
