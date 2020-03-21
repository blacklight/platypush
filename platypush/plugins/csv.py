import csv
import os
from typing import Optional, List, Any, Union, Dict
from typing.io import TextIO

from platypush.plugins import Plugin, action


class CsvPlugin(Plugin):
    """
    A plugin for managing CSV files.
    """

    @classmethod
    def _get_path(cls, filename: str) -> str:
        return os.path.abspath(os.path.expanduser(filename))

    @staticmethod
    def reversed_blocks(f: TextIO, blocksize=4096):
        """ Generate blocks of file's contents in reverse order. """
        f.seek(0, os.SEEK_END)
        here = f.tell()
        while 0 < here:
            delta = min(blocksize, here)
            here -= delta
            f.seek(here, os.SEEK_SET)
            yield f.read(delta)

    @classmethod
    def lines(cls, f: TextIO, reverse: bool = False):
        if not reverse:
            for line in f:
                yield line
        else:
            part = ''
            quoting = False
            for block in cls.reversed_blocks(f):
                for c in reversed(block):
                    if c == '"':
                        quoting = not quoting
                    elif c == '\n' and part and not quoting:
                        yield part[::-1]
                        part = ''
                    part += c
            if part:
                yield part[::-1]

    @staticmethod
    def _parse_header(filename: str, **csv_args) -> List[str]:
        column_names = []
        with open(filename, 'r', newline='') as f:
            try:
                has_header = csv.Sniffer().has_header(f.read(1024))
            except csv.Error:
                has_header = False

        if has_header:
            with open(filename, 'r', newline='') as f:
                for row in csv.reader(f, **csv_args):
                    column_names = row
                    break

        return column_names

    @action
    def read(self,
             filename: str,
             delimiter: str = ',',
             quotechar: Optional[str] = '"',
             start: int = 0,
             limit: Optional[int] = None,
             reverse: bool = False,
             has_header: bool = None,
             column_names: Optional[List[str]] = None,
             dialect: str = 'excel'):
        """
        Gets the content of a CSV file.

        :param filename: Path of the file.
        :param delimiter: Field delimiter (default: ``,``).
        :param quotechar: Quote character (default: ``"``).
        :param start: (Zero-based) index of the first line to be read (starting from the last if ``reverse`` is True)
            (default: 0).
        :param limit: Maximum number of lines to be read (default: all).
        :param reverse: If True then the lines will be read starting from the last (default: False).
        :param has_header: Set to True if the first row of the file is a header, False if the first row
            isn't expected to be a header (default: None, the method will scan the first chunk of the file
            and estimate whether the first line is a header).
        :param column_names: Specify if the file has no header or you want to override the column names.
        :param dialect: CSV dialect (default: ``excel``).
        """

        filename = self._get_path(filename)
        column_names = column_names or []
        csv_args = {
            'delimiter': delimiter,
            'quotechar': quotechar,
            'dialect': dialect,
        }

        if has_header is None and not column_names:
            column_names = self._parse_header(filename, **csv_args)
            has_header = len(column_names) > 0

        rows = []
        with open(filename, 'r', newline='') as f:
            for i, row in enumerate(csv.reader(self.lines(f, reverse=reverse), **csv_args)):
                if not row or i < start:
                    continue
                if limit and len(rows) >= limit + (1 if has_header else 0):
                    break

                rows.append(dict(zip(column_names, row)) if column_names else row)

        if has_header:
            rows.pop(-1 if reverse else 0)
        return rows

    @action
    def write(self,
              filename: str,
              rows: List[Union[List[Any], Dict[str, Any]]],
              truncate: bool = False,
              delimiter: str = ',',
              quotechar: Optional[str] = '"',
              dialect: str = 'excel'):
        """
        Writes lines to a CSV file.

        :param filename: Path of the CSV file.
        :param rows: Rows to write. It can be a list of lists or a key->value dictionary where the keys match
            the names of the columns. If the rows are dictionaries then a header with the column names will be
            written to the file if not available already, otherwise no header will be written.
        :param truncate: If True then any previous file content will be removed, otherwise the new rows will be
            appended to the file (default: False).
        :param delimiter: Field delimiter (default: ``,``).
        :param quotechar: Quote character (default: ``"``).
        :param dialect: CSV dialect (default: ``excel``).
        """
        filename = self._get_path(filename)
        file_exists = os.path.isfile(filename)
        column_names = []
        csv_args = {
            'delimiter': delimiter,
            'quotechar': quotechar,
            'dialect': dialect,
        }

        if file_exists:
            column_names = self._parse_header(filename, **csv_args)
        elif rows and isinstance(rows[0], dict):
            column_names = rows[0].keys()

        column_name_to_idx = {name: i for i, name in enumerate(column_names)}
        if truncate:
            file_exists = False

        with open(filename, 'w' if truncate else 'a', newline='') as f:
            writer = csv.writer(f, **csv_args)
            if not file_exists and column_names:
                writer.writerow(column_names)

            for row in rows:
                if isinstance(row, dict):
                    flat_row = [None] * len(column_names)
                    for column, value in row.items():
                        assert column in column_name_to_idx, \
                            'No such column available in the CSV file: {}'.format(column)
                        idx = column_name_to_idx[column]
                        flat_row[idx] = value

                    row = flat_row

                writer.writerow(row)


# vim:sw=4:ts=4:et:
