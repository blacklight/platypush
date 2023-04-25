from sqlalchemy import Column, String

from platypush.common.db import declarative_base
from platypush.context import get_plugin
from platypush.plugins import Plugin, action
from platypush.plugins.db import DbPlugin

Base = declarative_base()


# pylint: disable=too-few-public-methods
class Variable(Base):
    """Models the variable table"""

    __tablename__ = 'variable'

    name = Column(String, primary_key=True, nullable=False)
    value = Column(String)


class VariablePlugin(Plugin):
    """
    This plugin allows you to manipulate context variables that can be
    accessed across your tasks. It requires the :mod:`platypush.plugins.db`
    and :mod:`platypush.plugins.redis` plugins to be enabled, as the variables
    will be stored either persisted on a local database or on the local Redis instance.
    """

    def __init__(self, **kwargs):
        """
        The plugin will create a table named ``variable`` on the database
        configured in the :mod:`platypush.plugins.db` plugin. You'll have
        to specify a default ``engine`` in your ``db`` plugin configuration.
        """

        super().__init__(**kwargs)
        db_plugin = get_plugin('db')
        redis_plugin = get_plugin('redis')
        assert db_plugin, 'Database plugin not configured'
        assert redis_plugin, 'Redis plugin not configured'

        self.redis_plugin = redis_plugin
        self.db_plugin: DbPlugin = db_plugin
        self.db_plugin.create_all(self.db_plugin.get_engine(), Base)

    @action
    def get(self, name, default_value=None):
        """
        Get the value of a variable by name from the local db.

        :param name: Variable name
        :type name: str

        :param default_value: What will be returned if the variable is not defined (default: None)

        :returns: A map in the format ``{"<name>":"<value>"}``
        """

        with self.db_plugin.get_session() as session:
            var = session.query(Variable).filter_by(name=name).first()

        return {name: (var.value if var is not None else default_value)}

    @action
    def set(self, **kwargs):
        """
        Set a variable or a set of variables on the local db.

        :param kwargs: Key-value list of variables to set (e.g. ``foo='bar', answer=42``)
        """

        with self.db_plugin.get_session() as session:
            existing_vars = {
                var.name: var
                for var in session.query(Variable)
                .filter(Variable.name.in_(kwargs.keys()))
                .all()
            }

            new_vars = {
                name: Variable(name=name, value=value)
                for name, value in kwargs.items()
                if name not in existing_vars
            }

            for name, var in existing_vars.items():
                var.value = kwargs[name]  # type: ignore

            session.add_all([*existing_vars.values(), *new_vars.values()])

        return kwargs

    @action
    def unset(self, name):
        """
        Unset a variable by name if it's set on the local db.

        :param name: Name of the variable to remove
        :type name: str
        """

        with self.db_plugin.get_session() as session:
            session.query(Variable).filter_by(name=name).delete()

        return True

    @action
    def mget(self, name):
        """
        Get the value of a variable by name from Redis.

        :param name: Variable name
        :type name: str

        :returns: A map in the format ``{"<name>":"<value>"}``
        """

        return self.redis_plugin.mget([name])

    @action
    def mset(self, **kwargs):
        """
        Set a variable or a set of variables on Redis.

        :param kwargs: Key-value list of variables to set (e.g. ``foo='bar', answer=42``)

        :returns: A map with the set variables
        """

        self.redis_plugin.mset(**kwargs)
        return kwargs

    @action
    def munset(self, name):
        """
        Unset a Redis variable by name if it's set

        :param name: Name of the variable to remove
        :type name: str
        """

        return self.redis_plugin.delete(name)

    @action
    def expire(self, name, expire):
        """
        Set a variable expiration on Redis

        :param name: Variable name
        :type name: str

        :param expire: Expiration time in seconds
        :type expire: int
        """

        return self.redis_plugin.expire(name, expire)


# vim:sw=4:ts=4:et:
