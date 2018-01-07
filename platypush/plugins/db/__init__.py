import logging

from sqlalchemy import create_engine, Table, MetaData

from platypush.message.response import Response

from .. import Plugin

class DbPlugin(Plugin):
    """ Database plugin. It allows you to programmatically select, insert,
        update and delete records on a database backend through requests,
        procedures and event hooks """

    engine = None

    def __init__(self, engine=None, *args, **kwargs):
        """
        Params:
            engine -- Default SQLAlchemy connection engine string
            (e.g. sqlite:///:memory: or mysql://user:pass@localhost/test)
            that will be used. You can override this value in your statement actions

            args, kwargs -- Extra arguments for sqlalchemy.create_engine
        """

        self.engine = self._get_engine(engine, *args, **kwargs)


    def _get_engine(self, engine=None, *args, **kwargs):
        if engine:
            return create_engine(engine, *args, **kwargs)
        else:
            return self.engine

    def execute(self, statement, engine=None, *args, **kwargs):
        """ Executes a raw SQL statement """

        engine = self._get_engine(engine, *args, **kwargs)

        with engine.connect() as connection:
            result = connection.execute(statement)
            connection.commit()

        return Response()


    def select(self, query, engine=None, *args, **kwargs):
        """ Returns rows (as a list of dicts) given a query """

        engine = self._get_engine(engine, *args, **kwargs)

        with engine.connect() as connection:
            result = connection.execute(query)
            columns = result.keys()
            rows = [
                { columns[i]: row[i] for i in range(0, len(columns)) }
                for row in result.fetchall()
            ]

        return Response(output=rows)


    def insert(self, table, records, engine=None, *args, **kwargs):
        """ Inserts records (as a list of dicts) into a table """

        engine = self._get_engine(engine, *args, **kwargs)

        for record in records:
            metadata = MetaData()
            table = Table(table, metadata, autoload=True, autoload_with=engine)
            insert = table.insert().values(**record)
            engine.execute(insert)

        return Response()


# vim:sw=4:ts=4:et:

