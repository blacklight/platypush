from typing import Collection, Dict, Iterable, Optional, Union
from typing_extensions import override

from platypush.entities import EntityManager
from platypush.entities.variables import Variable
from platypush.plugins import Plugin, action


class VariablePlugin(Plugin, EntityManager):
    """
    This plugin allows you to manipulate context variables that can be
    accessed across your tasks. It requires the :mod:`platypush.plugins.db`
    and :mod:`platypush.plugins.redis` plugins to be enabled, as the variables
    will be stored either persisted on a local database or on the local Redis instance.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        db = self._db
        self._db_vars: Dict[str, Optional[str]] = {}
        """ Local cache for db variables. """

        with db.get_session() as session:
            self._db_vars.update(
                {  # type: ignore
                    str(var.name): var.value for var in session.query(Variable).all()
                }
            )

    @action
    def get(self, name: Optional[str] = None, default_value=None):
        """
        Get the value of a variable by name from the local db.

        :param name: Variable name. If not specified, all the stored variables will be returned.
        :param default_value: What will be returned if the variable is not defined (default: None)
        :returns: A map in the format ``{"<name>":"<value>"}``
        """

        return (
            {name: self._db_vars.get(name, default_value)}
            if name is not None
            else self.status().output
        )

    @action
    def set(self, **kwargs):
        """
        Set a variable or a set of variables on the local db.

        :param kwargs: Key-value list of variables to set (e.g. ``foo='bar', answer=42``)
        """

        self.publish_entities(kwargs)
        self._db_vars.update(kwargs)
        return kwargs

    @action
    def delete(self, name: str):
        """
        Delete a variable from the database.

        Unlike :meth:`.unset`, this method actually deletes the record from the
        database instead of setting it to null.

        :param name: Name of the variable to remove.
        """

        with self._db.get_session() as session:
            entity = session.query(Variable).filter(Variable.name == name).first()
            if entity is not None:
                self._entities.delete(entity.id)

        self._db_vars.pop(name, None)
        return True

    @action
    def unset(self, name: str):
        """
        Unset a variable by name if it's set on the local db.

        Unlike :meth:`.delete`, this method only sets the record to null
        instead of removing it from the database.

        :param name: Name of the variable to remove.
        """

        return self.set(**{name: None})

    @action
    def mget(self, name: str):
        """
        Get the value of a variable by name from Redis.

        :param name: Variable name
        :returns: A map in the format ``{"<name>":"<value>"}``
        """

        return self._redis.mget([name])

    @action
    def mset(self, **kwargs):
        """
        Set a variable or a set of variables on Redis.

        :param kwargs: Key-value list of variables to set (e.g. ``foo='bar', answer=42``)
        :returns: A map with the set variables
        """

        self._redis.mset(**kwargs)
        return kwargs

    @action
    def munset(self, name: str):
        """
        Unset a Redis variable by name if it's set

        :param name: Name of the variable to remove
        """

        return self._redis.delete(name)

    @action
    def expire(self, name: str, expire: int):
        """
        Set a variable expiration on Redis

        :param name: Variable name
        :param expire: Expiration time in seconds
        """

        return self._redis.expire(name, expire)

    @override
    def transform_entities(
        self, entities: Union[dict, Iterable]
    ) -> Collection[Variable]:
        variables = (
            [
                {
                    'name': name,
                    'value': value,
                }
                for name, value in entities.items()
            ]
            if isinstance(entities, dict)
            else entities
        )

        return super().transform_entities(
            [
                Variable(id=var['name'], name=var['name'], value=var['value'])
                for var in variables
            ]
        )

    @override
    @action
    def status(self, *_, **__):
        variables = {
            name: value for name, value in self._db_vars.items() if value is not None
        }

        self.publish_entities(variables)
        return variables


# vim:sw=4:ts=4:et:
