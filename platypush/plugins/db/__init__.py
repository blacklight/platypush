"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from sqlalchemy import create_engine, Table, MetaData

from platypush.plugins import Plugin, action

class DbPlugin(Plugin):
    """
    Database plugin. It allows you to programmatically select, insert, update
    and delete records on a database backend through requests, procedures and
    event hooks.

    Requires:
        * **sqlalchemy** (``pip install sqlalchemy``)
    """

    engine = None

    def __init__(self, engine=None, *args, **kwargs):
        """
        :param engine: Default SQLAlchemy connection engine string (e.g.  ``sqlite:///:memory:`` or ``mysql://user:pass@localhost/test``) that will be used. You can override the default engine in the db actions.
        :type engine: str
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        """

        super().__init__()
        self.engine = self._get_engine(engine, *args, **kwargs)


    def _get_engine(self, engine=None, *args, **kwargs):
        if engine:
            return create_engine(engine, *args, **kwargs)
        else:
            return self.engine

    def _build_condition(self, table, column, value):
        if isinstance(value, str):
            value = "'{}'".format(value)
        elif not isinstance(value, int) and not isinstance(value, 'float'):
            value = "'{}'".format(str(value))

        return eval('table.c.{}=={}'.format(column, value))

    @action
    def execute(self, statement, engine=None, *args, **kwargs):
        """
        Executes a raw SQL statement.

        .. warning::
            Avoid calling this method directly if possible.  Use ``insert``,
            ``update`` and ``delete`` methods instead if possible.  Don't use this
            method if you need to select records, use the ``select`` method
            instead, as this method is mostly meant to execute raw SQL without
            returning anything.

        :param statement: SQL to be executed
        :type statement: str
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        """

        engine = self._get_engine(engine, *args, **kwargs)

        with engine.connect() as connection:
            result = connection.execute(statement)


    @action
    def select(self, query=None, table=None, filter=None, engine=None, *args, **kwargs):
        """
        Returns rows (as a list of hashes) given a query.

        :param query: SQL to be executed
        :type query: str
        :param filter: Query WHERE filter expressed as a dictionary. This approach is preferred over specifying raw SQL in ``query`` as the latter approach may be prone to SQL injection, unless you need to build some complex SQL logic.
        :type filter: dict
        :param table: If you specified a filter instead of a raw query, you'll have to specify the target table
        :type table: str
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :returns: List of hashes representing the result rows.

        Examples:

            Request::

                {
                    "type": "request",
                    "target": "your_host",
                    "action": "db.select",
                    "args": {
                        "engine": "sqlite:///:memory:",
                        "query": "SELECT id, name FROM table"
                    }
                }

            or::

                {
                    "type": "request",
                    "target": "your_host",
                    "action": "db.select",
                    "args": {
                        "engine": "sqlite:///:memory:",
                        "table": "table",
                        "filter": {"id": 1}
                    }
                }

            Response::

                [
                    {
                        "id": 1,
                        "name": foo
                    }
                ]
        """

        db = self._get_engine(engine, *args, **kwargs)

        if table:
            metadata = MetaData()
            table = Table(table, metadata, autoload=True, autoload_with=db)
            query = table.select()

            if filter:
                for (k,v) in filter.items():
                    query = query.where(self._build_condition(table, k, v))

        if query is None:
            raise RuntimeError('You need to specify either "query", or "table" and "filter"')

        with db.connect() as connection:
            result = connection.execute(query)

            columns = result.keys()
            rows = [
                { columns[i]: row[i] for i in range(0, len(columns)) }
                for row in result.fetchall()
            ]

        return rows


    @action
    def insert(self, table, records, engine=None, key_columns=[],
               on_duplicate_update=False, *args, **kwargs):
        """
        Inserts records (as a list of hashes) into a table.

        :param table: Table name
        :type table: str
        :param records: Records to be inserted (as a list of hashes)
        :type records: list
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param key_columns: Set it to specify the names of the key columns for ``table``. Set it if you want your statement to be executed with the ``on_duplicate_update`` flag.
        :type key_columns: list
        :param on_duplicate_update: If set, update the records in case of duplicate rows (default: False). If set, you'll need to specify ``key_columns`` as well.
        :type on_duplicate_update: bool
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)

        Example:

            Request::

                {
                    "type": "request",
                    "target": "your_host",
                    "action": "db.insert",
                    "args": {
                        "table": "table",
                        "engine": "sqlite:///:memory:",
                        "records": [
                            {
                                "id": 1,
                                "name": foo
                            },

                            {
                                "id": 2,
                                "name": bar
                            }
                        ]
                    }
                }
        """

        db = self._get_engine(engine, *args, **kwargs)

        for record in records:
            metadata = MetaData()
            table = Table(table, metadata, autoload=True, autoload_with=db)
            insert = table.insert().values(**record)

            try:
                db.execute(insert)
            except Exception as e:
                if on_duplicate_update and key_columns:
                    self.update(table=table, records=records,
                                key_columns=key_columns, engine=engine,
                                *args, **kwargs)
                else:
                    raise e


    @action
    def update(self, table, records, key_columns, engine=None, *args, **kwargs):
        """
        Updates records on a table.

        :param table: Table name
        :type table: str
        :param records: Records to be updated (as a list of hashes)
        :type records: list
        :param key_columns: Names of the key columns, used in the WHERE condition
        :type key_columns: list
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)

        Example:

            Request::

                {
                    "type": "request",
                    "target": "your_host",
                    "action": "db.update",
                    "args": {
                        "table": "table",
                        "engine": "sqlite:///:memory:",
                        "key_columns": ["id"],
                        "records": [
                            {
                                "id": 1,
                                "name": foo
                            },

                            {
                                "id": 2,
                                "name": bar
                            }
                        ]
                    }
                }
        """

        engine = self._get_engine(engine, *args, **kwargs)

        for record in records:
            metadata = MetaData()
            table = Table(table, metadata, autoload=True, autoload_with=engine)
            key = { k:v for (k,v) in record.items() if k in key_columns }
            values = { k:v for (k,v) in record.items() if k not in key_columns }

            update = table.update()

            for (k,v) in key.items():
                update = update.where(self._build_condition(table, k, v))

            update = update.values(**values)
            engine.execute(update)


    @action
    def delete(self, table, records, engine=None, *args, **kwargs):
        """
        Deletes records from a table.

        :param table: Table name
        :type table: str
        :param records: Records to be deleted, as a list of dictionaries
        :type records: list
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)

        Example:

            Request::

                {
                    "type": "request",
                    "target": "your_host",
                    "action": "db.delete",
                    "args": {
                        "table": "table",
                        "engine": "sqlite:///:memory:",
                        "records": [
                            { "id": 1 },
                            { "id": 2 }
                        ]
                    }
                }
        """

        engine = self._get_engine(engine, *args, **kwargs)

        for record in records:
            metadata = MetaData()
            table = Table(table, metadata, autoload=True, autoload_with=engine)
            delete = table.delete()

            for (k,v) in record.items():
                delete = delete.where(self._build_condition(table, k, v))

            engine.execute(delete)


# vim:sw=4:ts=4:et:

