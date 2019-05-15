import json
import os
import re

from platypush.config import Config

class HttpUtils(object):
    @staticmethod
    def widget_columns_to_html_class(columns):
        if not isinstance(columns, int):
            raise RuntimeError('columns should be a number, got "{}"'.format(columns))

        if columns == 1:
            return 'one column'
        elif columns == 2:
            return 'two columns'
        elif columns == 3:
            return 'three columns'
        elif columns == 4:
            return 'four columns'
        elif columns == 5:
            return 'five columns'
        elif columns == 6:
            return 'six columns'
        elif columns == 7:
            return 'seven columns'
        elif columns == 8:
            return 'eight columns'
        elif columns == 9:
            return 'nine columns'
        elif columns == 10:
            return 'ten columns'
        elif columns == 11:
            return 'eleven columns'
        elif columns == 12:
            return 'twelve columns'
        else:
            raise RuntimeError('Constraint violation: should be 1 <= columns <= 12, ' +
                               'got columns={}'.format(columns))

    @staticmethod
    def search_directory(directory, *extensions, recursive=False):
        files = []

        if recursive:
            for root, subdirs, files in os.walk(directory):
                for file in files:
                    if not extensions or os.path.splitext(file)[1].lower() in extensions:
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
                subdir = re.sub('^{}(.*)$'.format(resource_path),
                                '\\1', directory)
                uri = '/resources/' + name
                break

        if not uri:
            raise RuntimeError(('Directory {} not found among the available ' +
                               'static resources on the webserver').format(
                                   directory))

        results = [
            re.sub('^{}(.*)$'.format(resource_path), uri + '\\1', path)
            for path in cls.search_directory(directory, *extensions)
        ]

        return results

    @classmethod
    def to_json(cls, data):
        if isinstance(data, type({}.keys())):
            # Convert dict_keys to list before serializing
            data = list(data)
        return json.dumps(data)

    @classmethod
    def from_json(cls, data):
        return json.loads(data)

    @classmethod
    def get_config(cls, attr):
        return Config.get(attr)


# vim:sw=4:ts=4:et:
