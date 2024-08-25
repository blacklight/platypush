import json
import os
import pathlib
import shutil
import stat
from functools import lru_cache
from multiprocessing import RLock
from typing import Any, Iterable, List, Dict, Optional, Set, Union

from platypush.plugins import Plugin, action
from platypush.utils import get_mime_type, is_binary

Bookmarks = Union[Iterable[str], Iterable[Union[str, Dict[str, Any]]], Dict[str, Any]]


class FilePlugin(Plugin):
    """
    A plugin for general-purpose file methods
    """

    def __init__(self, *args, bookmarks: Optional[Bookmarks] = None, **kwargs):
        """
        :param bookmarks: A list/dictionary of bookmarks. Bookmarks will be
            shown in the file browser UI home page for easier access.

            Possible formats:

              .. code-block:: yaml

                bookmarks:
                    - /path/to/directory1
                    - /path/to/directory2

              .. code-block:: yaml

                bookmarks:
                    Movies: /path/to/movies
                    Music: /path/to/music

              .. code-block:: yaml

                bookmarks:
                    - name: Movies
                      path: /path/to/movies
                      icon:
                          class: fa fa-film

              .. code-block:: yaml

                bookmarks:
                    Movies:
                        name: Movies
                        path: /path/to/movies
                        icon:
                            url: /path/to/icon.png

        """
        super().__init__(*args, **kwargs)
        self._mime_types_lock = RLock()
        self._bookmarks = self._parse_bookmarks(bookmarks)

    def _parse_bookmarks(self, bookmarks: Bookmarks) -> Dict[str, Dict[str, Any]]:
        ret = {}
        if isinstance(bookmarks, (list, tuple, set)):
            for bookmark in bookmarks:
                if isinstance(bookmark, str):
                    ret[bookmark] = {'name': bookmark, 'path': bookmark}
                else:
                    ret[bookmark['name']] = bookmark
        elif isinstance(bookmarks, dict):
            ret.update(bookmarks)

        for name, bookmark in ret.items():
            ret[name] = (
                {'name': name, 'path': os.path.abspath(os.path.expanduser(bookmark))}
                if isinstance(bookmark, str)
                else bookmark
            )

        return ret

    @classmethod
    def _get_path(cls, filename):
        return os.path.abspath(os.path.expanduser(filename))

    @classmethod
    def _to_string(cls, content):
        try:
            return json.dumps(content)
        except (ValueError, TypeError):
            return str(content)

    @action
    def read(self, file: str):
        """
        Read and return the content of a (text) file.

        Note that this method should only be used for small text files, as it
        reads the entire file in memory.

        If you need to read large/binary files, consider using the
        ``GET /file?path=<path>`` HTTP API endpoint instead.

        :param file: Path of the file.
        """
        with open(self._get_path(file), 'r') as f:
            return f.read()

    @action
    def write(self, file: str, content: str):
        """
        Writes content to a specified (text) file. Previous content will be truncated.

        :param file: Path of the file.
        :param content: Content to write.
        """

        if not isinstance(content, str):
            content = self._to_string(content)

        with open(self._get_path(file), 'w') as f:
            f.write(content)

    @action
    def append(self, file: str, content):
        """
        Append content to a specified (text) file.

        :param file: Path of the file.
        :param content: Content to write.
        """

        if not isinstance(content, str):
            content = self._to_string(content)

        with open(self._get_path(file), 'a') as f:
            f.write(content)

    @action
    def getsize(self, file):
        """
        Get the size of the specified file in bytes.

        :param file: File path.
        """
        return os.path.getsize(self._get_path(file))

    @action
    def mkdir(self, directory: str, exist_ok=True, parents=True, mode=0o755):
        """
        Create a directory.

        :param directory: Directory name/path.
        :param exist_ok: If set and the directory already exist the method will
            not return an error (default: True).
        :param parents: If set and any of the parent directories in the path don't
            exist they will be created (analogous to mkdir -p) (default: True).
        :param mode: Access mode (default: 0755).
        """
        pathlib.Path(self._get_path(directory)).mkdir(
            parents=parents, exist_ok=exist_ok, mode=mode
        )

    @action
    def rmdir(self, directory: str, recursive: bool = False):
        """
        Remove a directory. The directory must be empty.

        :param directory: Directory name/path.
        :param recursive: If set, the directory and all its contents will be
            removed recursively (default: False).
        """
        directory = self._get_path(directory)
        if not recursive:
            pathlib.Path(directory).rmdir()
        else:
            shutil.rmtree(directory)

    @action
    def touch(self, file: str, mode=0o644):
        """
        Create/touch a file.

        :param file: File name/path.
        :param mode: File permissions (default: 0644).
        """
        pathlib.Path(self._get_path(file)).touch(mode=mode)

    @action
    def chmod(self, file: str, mode):
        """
        Change the mode/permissions of a file.

        :param file: File name/path.
        :param mode: New file permissions.
        """
        pathlib.Path(self._get_path(file)).chmod(mode=mode)

    @action
    def home(self) -> str:
        """
        Returns the current user's home directory.
        """
        return str(pathlib.Path.home())

    @action
    def rename(self, file: str, name: str):
        """
        Rename/move a file.

        :param file: File to rename.
        :param name: New file name.
        """
        pathlib.Path(self._get_path(file)).rename(self._get_path(name))

    @action
    def copy(self, source: str, target: str):
        """
        Copy a file.

        :param source: Source file.
        :param target: Destination file.
        """
        shutil.copy(self._get_path(source), self._get_path(target))

    @action
    def move(self, source: str, target: str):
        """
        Move a file.

        :param source: Source file.
        :param target: Destination file.
        """
        shutil.move(self._get_path(source), self._get_path(target))

    @action
    def link(self, file: str, target: str, symbolic=True):
        """
        Create a link to a file.

        :param file: File to symlink.
        :param target: Symlink path.
        :param symbolic: If True, then the target link will be a symbolic link. Otherwise,
            it will be a hard link (default: symbolic).
        """
        path = pathlib.Path(self._get_path(file))
        target = self._get_path(target)

        if symbolic:
            path.symlink_to(target)
        else:
            path.hardlink_to(target)

    @action
    def unlink(self, file: str):
        """
        Remove a file or symbolic link.

        :param file: File/link to remove.
        """
        pathlib.Path(self._get_path(file)).unlink()

    @action
    def list(
        self,
        path: Optional[str] = None,
        sort: str = 'name',
        reverse: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List a file or all the files in a directory.

        :param path: File or directory (default: root directory).
        :param sort: Sort the files by ``name``, ``size``, ``last_modified``
            or ``created`` time (default: ``name``).
        :param reverse: If set, the files will be sorted in descending order
            according to the specified ``sort`` field (default: False).
        :return: List of files in the specified path, or absolute path of the
            specified path if ``path`` is a file and it exists. Each item will
            contain the fields ``type`` (``file`` or ``directory``) and
            ``path``.
        """
        path = self._get_path(path or '/')
        assert path and os.path.exists(path), f'No such file or directory: {path}'

        if not os.path.isdir(path):
            return [
                {
                    'type': 'file',
                    'path': path,
                    'name': os.path.basename(path),
                    **self._get_file_info(path),
                }
            ]

        return sorted(
            [
                {
                    'type': (
                        'directory' if os.path.isdir(os.path.join(path, f)) else 'file'
                    ),
                    'path': os.path.join(path, f),
                    'name': os.path.basename(f),
                    **self._get_file_info(os.path.join(path, f)),
                }
                for f in os.listdir(path)
            ],
            key=lambda f: (f.get('type'), (f.get(sort) or 0)),
            reverse=reverse,
        )

    @staticmethod
    def _get_file_info(file: str) -> Dict[str, Any]:
        ret: dict = {'path': file}

        try:
            ret['size'] = os.path.getsize(file)
        except Exception:
            ret['size'] = None

        try:
            ret['last_modified'] = os.path.getmtime(file)
        except Exception:
            ret['last_modified'] = None

        try:
            ret['created'] = os.path.getctime(file)
        except Exception:
            ret['created'] = None

        try:
            stat_info = os.stat(file)
            ret.update(
                {
                    'permissions': stat.filemode(stat_info.st_mode),
                    'owner': stat_info.st_uid,
                    'group': stat_info.st_gid,
                }
            )
        except Exception:
            ret.update({'permissions': None, 'owner': None, 'group': None})

        return ret

    @action
    def info(self, files: Iterable[str]) -> Dict[str, Dict[str, str]]:
        """
        Retrieve information about a list of files.

        :param files: List of files.
        :return: Dict containing the information about each file. Example:

          .. code-block:: json

            {
                "/path/to/file": {
                    "path": "/path/to/file",
                    "name": "file",
                    "size": 1234,
                    "type": "file",
                    "mime_type": "application/octet-stream",
                    "last_modified": "2021-01-01T00:00:00",
                    "permissions": "rw-r--r--",
                    "owner": "user",
                    "group": "group",
                }
            }

        """
        with self._mime_types_lock:
            ret = {}
            for file in files:
                file = self._get_path(file)
                if not os.path.exists(file):
                    self.logger.warning('File not found: %s', file)
                    continue

                ret[file] = {
                    **self._get_file_info(file),
                    'mime_type': get_mime_type(file),
                }

        return ret

    @action
    def get_mime_types(
        self,
        files: Iterable[str],
        types: Optional[Iterable[str]] = None,
    ) -> Dict[str, str]:
        """
        Given a list of files or URLs, get their MIME types, or filter them by
        MIME type.

        :param files: List of files or URLs.
        :param types: Filter of MIME types to apply. Partial matches are
            allowed - e.g. 'video' will match all video types. No filter means
            that all the input resources will be returned with their respective
            MIME types.
        :return: Dict containing the filtered resources and their MIME types.
        """
        filter_types = set()
        for t in types or []:
            filter_types.add(t)
            tokens = t.split('/')
            for token in tokens:
                filter_types.add(token)

        with self._mime_types_lock:
            return self._get_mime_types(files, filter_types)

    @action
    def is_binary(self, file: str) -> bool:
        """
        :file: File path.
        :return: True if the file is binary, False otherwise.
        """
        with open(self._get_path(file), 'rb') as f:
            return is_binary(f.read(1024))

    @action
    def get_user_home(self) -> str:
        """
        :return: The current user's home directory.
        """
        return str(pathlib.Path.home())

    @action
    def get_bookmarks(self) -> Dict[str, Dict[str, Any]]:
        """
        :return: List of bookmarks. Example:

            .. code-block:: json

                {
                    "directory1": {
                        "name": "directory1",
                        "path": "/path/to/directory1"
                        "icon": {
                            "class": "fa fa-folder"
                        }
                    },

                    "directory2": {
                        "name": "directory2",
                        "path": "/path/to/directory2"
                        "icon": {
                            "url": "/path/to/icon.png"
                        }
                    }
                }

        """
        return self._bookmarks

    def _get_mime_types(
        self, files: Iterable[str], filter_types: Set[str]
    ) -> Dict[str, str]:
        ret = {}
        for file in files:
            try:
                mime_type = self._get_mime_type(file)
            except Exception as e:
                self.logger.warning('Error while getting MIME type for %s: %s', file, e)
                continue

            mime_tokens = {mime_type, *mime_type.split('/')}
            if not filter_types or any(token in filter_types for token in mime_tokens):
                ret[file] = mime_type

        return ret

    @lru_cache(maxsize=1024)  # noqa
    def _get_mime_type(self, file: str) -> str:
        if file.startswith('file://'):
            file = file[len('file://') :]

        return get_mime_type(file) or 'application/octet-stream'


# vim:sw=4:ts=4:et:
