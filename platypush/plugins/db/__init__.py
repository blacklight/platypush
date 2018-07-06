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

    .. todo::
        Implement ``update`` and ``delete`` methods
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
            connection.commit()


    @action
    def select(self, query, engine=None, *args, **kwargs):
        """
        Returns rows (as a list of hashes) given a query.

        :param query: SQL to be executed
        :type query: str
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param args: Extra arguments that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to ``sqlalchemy.create_engine`` (see http://docs.sqlalchemy.org/en/latest/core/engines.html)
        :returns: List of hashes representing the result rows.

        Example:

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

            Response::

                [
                    {
                        "id": 1,
                        "name": foo
                    },

                    {
                        "id": 2,
                        "name": bar
                    }
                ]
        """

        engine = self._get_engine(engine, *args, **kwargs)

        with engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [
                { columns[i]: row[i] for i in range(0, len(columns)) }
                for row in result.fetchall()
            ]

        return rows


    @action
    def insert(self, table, records, engine=None, *args, **kwargs):
        """
        Inserts records (as a list of hashes) into a table.

        :param table: Table name
        :type table: str
        :param records: Records to be inserted (as a list of hashes)
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

        engine = self._get_engine(engine, *args, **kwargs)

        for record in records:
            metadata = MetaData()
            table = Table(table, metadata, autoload=True, autoload_with=engine)
            insert = table.insert().values(**record)
            engine.execute(insert)


# vim:sw=4:ts=4:et:

