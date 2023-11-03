from abc import ABC, abstractmethod
import json
from logging import getLogger, Logger


class Command(ABC):
    """
    Base class for application commands.
    """

    END_OF_COMMAND = b'\x00'
    """End-of-command marker."""

    def __init__(self, **args) -> None:
        self.args = args

    @property
    def logger(self) -> Logger:
        """
        The command class logger.
        """
        return getLogger(self.__class__.__name__)

    @abstractmethod
    def __call__(self, app, *_, **__):
        """
        Execute the command.
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """
        :return: A JSON representation of the command.
        """
        return json.dumps(
            {
                'type': 'command',
                'command': self.__class__.__name__,
                'args': self.args,
            }
        )

    def to_bytes(self):
        """
        :return: A JSON representation of the command.
        """
        return str(self).encode('utf-8') + self.END_OF_COMMAND

    @classmethod
    def parse(cls, data: bytes) -> "Command":
        """
        :param data: A JSON representation of the command.
        :raise ValueError: If the data is invalid.
        :return: The command instance or None if the data is invalid.
        """
        import platypush.commands

        try:
            json_data = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError from e

        kind = json_data.pop('type', None)
        if kind != 'command':
            raise ValueError(f'Invalid command type: {kind}')

        command_name = json_data.get('command')
        if not command_name:
            raise ValueError(f'Invalid command name: {command_name}')

        cmd_class = getattr(platypush.commands, command_name, None)
        if not (cmd_class and issubclass(cmd_class, Command)):
            raise ValueError(f'Invalid command class: {command_name}')

        try:
            return cmd_class(**json_data.get('args', {}))
        except Exception as e:
            raise ValueError(e) from e
