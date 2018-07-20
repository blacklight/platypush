from platypush.config import Config
from platypush.context import get_plugin
from platypush.plugins import Plugin, action


class VariablePlugin(Plugin):
    """
    This plugin allows you to manipulate context variables that can be
    accessed across your tasks. It requires the :mod:`platypush.plugins.db`
    plugin to be enabled, as the variables will be stored on a local database
    for persistency and multi-process sharing purposes.

    Requires:

        * **sqlalchemy** (``pip install sqlalchemy``)
    """

    _variable_table_name = 'variable'

    def __init__(self, *args, **kwargs):
        """
        The plugin will create a table named ``variable`` on the database
        configured in the :mod:`platypush.plugins.db` plugin. You'll have
        to specify a default ``engine`` in your ``db`` plugin configuration.
        """

        super().__init__(*args, **kwargs)
        self.db_plugin = get_plugin('db')

        db = Config.get('db')
        self.db_config = {
            'engine': db.get('engine'),
            'args': db.get('args', []),
            'kwargs': db.get('kwargs', {})
        }

        self._create_tables()
        # self._variables = {}

    def _create_tables(self):
        self.db_plugin.execute("""CREATE TABLE IF NOT EXISTS {}(
            name varchar(255) not null primary key,
            value text
        )""".format(self._variable_table_name))

    @action
    def get(self, name, default_value=None):
        """
        Get the value of a variable by name.

        :param name: Variable name
        :type name: str

        :param default_value: What will be returned if the variable is not defined (default: None)

        :returns: A map in the format ``{"<name>":"<value>"}``
        """

        rows = self.db_plugin.select(table=self._variable_table_name,
                                     filter={'name': name},
                                     engine=self.db_config['engine'],
                                     *self.db_config['args'],
                                     **self.db_config['kwargs']).output

        return {name: rows[0]['value'] if rows else None}

    @action
    def set(self, **kwargs):
        """
        Set a variable or a set of variables.

        :param kwargs: Key-value list of variables to set (e.g. ``foo='bar', answer=42``)
        """

        records = [ { 'name': k, 'value': v }
                   for (k,v) in kwargs.items() ]

        self.db_plugin.insert(table=self._variable_table_name,
                              records=records, key_columns=['name'],
                              engine=self.db_config['engine'],
                              on_duplicate_update=True,
                              *self.db_config['args'],
                              **self.db_config['kwargs'])

        return kwargs


    @action
    def unset(self, name):
        """
        Unset a variable by name if it's set

        :param name: Name of the variable to remove
        :type name: str
        """

        records = [ { 'name': name } ]

        self.db_plugin.delete(table=self._variable_table_name,
                              records=records, engine=self.db_config['engine'],
                              *self.db_config['args'],
                              **self.db_config['kwargs'])

        return True


# vim:sw=4:ts=4:et:

