import time
from contextlib import contextmanager
from multiprocessing import RLock
from typing import Optional, Generator, Union

from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.exc import CompileError
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy.sql import and_, or_, text

from platypush.plugins import Plugin, action

session_locks = {}


class DbPlugin(Plugin):
    """
    Database plugin. It allows you to programmatically select, insert, update
    and delete records on a database backend through requests, procedures and
    event hooks.
    """

    engine = None
    _db_error_wait_interval = 5.0
    _db_error_retries = 3

    def __init__(self, engine=None, **kwargs):
        """
        :param engine: Default SQLAlchemy connection engine string (e.g.
            ``sqlite:///:memory:`` or ``mysql://user:pass@localhost/test``)
            that will be used. You can override the default engine in the db
            actions.
        :type engine: str
        :param args: Extra arguments that will be passed to
            ``sqlalchemy.create_engine`` (see
            https://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to
            ``sqlalchemy.create_engine``
            (see https:///docs.sqlalchemy.org/en/latest/core/engines.html)
        """

        super().__init__()
        self.engine_url = engine
        self.engine = self.get_engine(engine, **kwargs)

    def get_engine(
        self, engine: Optional[Union[str, Engine]] = None, *args, **kwargs
    ) -> Engine:
        if engine == self.engine_url and self.engine:
            return self.engine

        if engine or not self.engine:
            if isinstance(engine, Engine):
                return engine
            if not engine:
                engine = self.engine_url
            if isinstance(engine, str) and engine.startswith('sqlite://'):
                kwargs['connect_args'] = {'check_same_thread': False}

            return create_engine(engine, *args, **kwargs)  # type: ignore

        if not self.engine:
            self.engine = create_engine(self.engine_url, *args, **kwargs)  # type: ignore

        return self.engine

    @staticmethod
    def _build_condition(table, column, value):  # pylint: disable=unused-argument
        if isinstance(value, str) or not isinstance(value, (int, float)):
            value = f"'{value}'"

        return eval(f'table.c.{column}=={value}')  # pylint: disable=eval-used

    @action
    def execute(self, statement, *args, engine=None, **kwargs):
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
        :param args: Extra arguments that will be passed to
            ``sqlalchemy.create_engine`` (see
            https://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to
            ``sqlalchemy.create_engine``
            (see https:///docs.sqlalchemy.org/en/latest/core/engines.html)
        """

        with self.get_engine(engine, *args, **kwargs).connect() as connection:
            connection.execute(text(statement))

    def _get_table(self, table: str, *args, engine=None, **kwargs):
        if not engine:
            engine = self.get_engine(engine, *args, **kwargs)

        db_ok = False
        n_tries = 0
        last_error = None
        table_ = None

        while not db_ok and n_tries < self._db_error_retries:
            try:
                n_tries += 1
                metadata = MetaData()
                table_ = Table(table, metadata, autoload_with=engine)
                db_ok = True
            except Exception as e:
                last_error = e
                wait_time = self._db_error_wait_interval * n_tries
                self.logger.exception(e)
                self.logger.info('Waiting %s seconds before retrying', wait_time)
                time.sleep(wait_time)
                engine = self.get_engine(engine, *args, **kwargs)

        if not db_ok and last_error:
            raise last_error

        assert table_ is not None, f'No such table: {table}'
        return table_, engine

    @action
    def select(
        self,
        query=None,
        table=None,
        filter=None,
        engine=None,
        data: Optional[dict] = None,
        *args,
        **kwargs,
    ):
        """
        Returns rows (as a list of hashes) given a query.

        :param query: SQL to be executed
        :type query: str
        :param filter: Query WHERE filter expressed as a dictionary. This
            approach is preferred over specifying raw SQL
            in ``query`` as the latter approach may be prone to SQL injection,
            unless you need to build some complex SQL logic.
        :type filter: dict
        :param table: If you specified a filter instead of a raw query, you'll
            have to specify the target table
        :type table: str
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param data: If ``query`` is an SQL string, then you can use
            SQLAlchemy's *placeholders* mechanism. You can specify placeholders
            in the query for values that you want to be safely serialized, and
            their values can be specified on the ``data`` attribute in a
            ``name`` ➡️ ``value`` mapping format.
        :param args: Extra arguments that will be passed to
            ``sqlalchemy.create_engine`` (see
            https://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to
            ``sqlalchemy.create_engine`` (see
            https:///docs.sqlalchemy.org/en/latest/core/engines.html)
        :returns: List of hashes representing the result rows.

        Examples:

            Request::

                {
                    "type": "request",
                    "target": "your_host",
                    "action": "db.select",
                    "args": {
                        "engine": "sqlite:///:memory:",
                        "query": "SELECT id, name FROM table WHERE name = :name",
                        "data": {
                            "name": "foobar"
                        }
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

        engine = self.get_engine(engine, *args, **kwargs)

        if isinstance(query, str):
            query = text(query)

        if table:
            table, engine = self._get_table(table, engine=engine, *args, **kwargs)
            query = table.select()

            if filter:
                for k, v in filter.items():
                    query = query.where(self._build_condition(table, k, v))

        if query is None:
            raise RuntimeError(
                'You need to specify either "query", or "table" and "filter"'
            )

        with engine.connect() as connection:
            result = connection.execute(query, **(data or {}))
            columns = result.keys()
            rows = [
                {col: row[i] for i, col in enumerate(list(columns))}
                for row in result.fetchall()
            ]

        return rows

    @action
    def insert(
        self,
        table,
        records,
        engine=None,
        key_columns=None,
        on_duplicate_update=False,
        *args,
        **kwargs,
    ):
        """
        Inserts records (as a list of hashes) into a table.

        :param table: Table name
        :type table: str
        :param records: Records to be inserted (as a list of hashes)
        :type records: list
        :param engine: Engine to be used (default: default class engine)
        :type engine: str
        :param key_columns: Set it to specify the names of the key columns for
            ``table``. Set it if you want your statement to be executed with
            the ``on_duplicate_update`` flag.
        :type key_columns: list
        :param on_duplicate_update: If set, update the records in case of
            duplicate rows (default: False). If set, you'll need to specify
            ``key_columns`` as well. If ``key_columns`` is set, existing
            records are found but ``on_duplicate_update`` is false, then
            existing records will be ignored.
        :type on_duplicate_update: bool
        :param args: Extra arguments that will be passed to
            ``sqlalchemy.create_engine`` (see
            https://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to
            ``sqlalchemy.create_engine``
            (see https:///docs.sqlalchemy.org/en/latest/core/engines.html)

        :return: The inserted records, if the underlying engine supports the
            ``RETURNING`` statement, otherwise nothing.

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

        if on_duplicate_update:
            assert (
                key_columns
            ), 'on_duplicate_update requires key_columns to be specified'

        if key_columns is None:
            key_columns = []

        engine = self.get_engine(engine, *args, **kwargs)
        table, engine = self._get_table(table, engine=engine, *args, **kwargs)
        insert_records = records
        update_records = []
        returned_records = []

        with engine.connect() as connection:
            # Upsert case
            if key_columns:
                insert_records, update_records = self._get_new_and_existing_records(
                    connection, table, records, key_columns
                )

            if insert_records:
                insert = table.insert().values(insert_records)
                ret = self._execute_try_returning(connection, insert)
                if ret:
                    returned_records += ret

            if update_records and on_duplicate_update:
                ret = self._update(connection, table, update_records, key_columns)
                if ret:
                    returned_records = ret + returned_records

        if returned_records:
            return returned_records

    @staticmethod
    def _execute_try_returning(connection, stmt):
        ret = None
        stmt_with_ret = stmt.returning('*')

        try:
            ret = connection.execute(stmt_with_ret)
        except CompileError as e:
            if str(e).startswith('RETURNING is not supported'):
                connection.execute(stmt)
            else:
                raise e

        if ret:
            return [
                {col.name: getattr(row, col.name, None) for col in stmt.table.c}
                for row in ret
            ]

    def _get_new_and_existing_records(self, connection, table, records, key_columns):
        records_by_key = {
            tuple(record.get(k) for k in key_columns): record for record in records
        }

        query = table.select().where(
            or_(
                and_(  # type: ignore
                    self._build_condition(table, k, record.get(k))
                    for k in key_columns  # type: ignore
                )
                for record in records
            )
        )

        existing_records = {
            tuple(getattr(record, k, None) for k in key_columns): record
            for record in connection.execute(query).all()
        }

        update_records = [
            record for k, record in records_by_key.items() if k in existing_records
        ]

        insert_records = [
            record for k, record in records_by_key.items() if k not in existing_records
        ]

        return insert_records, update_records

    def _update(self, connection, table, records, key_columns):
        updated_records = []
        for record in records:
            key = {k: v for (k, v) in record.items() if k in key_columns}
            values = {k: v for (k, v) in record.items() if k not in key_columns}
            update = table.update()

            for k, v in key.items():
                update = update.where(self._build_condition(table, k, v))

            update = update.values(**values)
            ret = self._execute_try_returning(connection, update)
            if ret:
                updated_records += ret

        if updated_records:
            return updated_records

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
        :param args: Extra arguments that will be passed to
            ``sqlalchemy.create_engine`` (see
            https://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to
            ``sqlalchemy.create_engine``
            (see https:///docs.sqlalchemy.org/en/latest/core/engines.html)

        :return: The inserted records, if the underlying engine supports the
            ``RETURNING`` statement, otherwise nothing.

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
        engine = self.get_engine(engine, *args, **kwargs)
        with engine.connect() as connection:
            table, engine = self._get_table(table, engine=engine, *args, **kwargs)
            return self._update(connection, table, records, key_columns)

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
        :param args: Extra arguments that will be passed to
            ``sqlalchemy.create_engine`` (see
            https://docs.sqlalchemy.org/en/latest/core/engines.html)
        :param kwargs: Extra kwargs that will be passed to
            ``sqlalchemy.create_engine``
            (see https:///docs.sqlalchemy.org/en/latest/core/engines.html)

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

        engine = self.get_engine(engine, *args, **kwargs)

        with engine.connect() as connection:
            for record in records:
                table_, engine = self._get_table(table, engine=engine, *args, **kwargs)
                delete = table_.delete()

                for k, v in record.items():
                    delete = delete.where(self._build_condition(table_, k, v))

                connection.execute(delete)

    def create_all(self, engine, base):
        with self.get_session(engine, locked=True) as session:
            base.metadata.create_all(session.connection())

    @contextmanager
    def get_session(
        self, *args, engine=None, locked=False, autoflush=True, **kwargs
    ) -> Generator[Session, None, None]:
        engine = self.get_engine(engine, *args, **kwargs)
        if locked:
            lock = session_locks[engine.url] = session_locks.get(engine.url, RLock())
        else:
            # Mock lock
            lock = RLock()

        with lock, engine.connect() as conn:
            session_maker = scoped_session(
                sessionmaker(
                    expire_on_commit=False,
                    autoflush=autoflush,
                )
            )

            session_maker.configure(bind=conn)
            session = session_maker()
            yield session

            session.flush()
            session.commit()


# vim:sw=4:ts=4:et:
