from dataclasses import dataclass, field
from enum import Enum
from random import randint
from threading import RLock
from time import time
from typing import Any, Optional

from platypush.context import get_backend
from platypush.message.response import Response


def _generate_id() -> str:
    return ''.join(f'{i:02x}' for i in (randint(0, 255) for _ in range(16)))


class LoggedActionStatus(Enum):
    """
    Data class representing the status of a logged action.
    """

    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


@dataclass
class LoggedAction:
    """
    Data class representing a logged action.
    """

    action: str
    args: dict = field(default_factory=dict)
    id: str = field(default_factory=_generate_id)
    origin: Optional[str] = None
    target: Optional[str] = None
    response: Optional[Any] = None
    status: LoggedActionStatus = LoggedActionStatus.RUNNING
    started_at: float = field(default_factory=time)
    completed_at: Optional[float] = None

    def dump(self):
        if isinstance(self.response, Response):
            response = (
                self.response.errors[0]
                if self.response.errors
                else self.response.output
            )
        else:
            response = self.response

        args = {
            k: v
            for k, v in self.args.items()
            if k
            not in (
                'password',
                'new_password',
                'token',
                'access_token',
                'new_context',
                '__stack__',
            )
        }

        return {
            'id': self.id,
            'action': self.action,
            'args': args,
            'status': self.status.value,
            **({'origin': self.origin} if self.origin else {}),
            **({'target': self.target} if self.target else {}),
            'response': response,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'running_time': (
                self.completed_at - self.started_at
                if self.completed_at is not None
                else time() - self.started_at
            ),
        }


class LoggedActions:
    """
    Class to manage logged actions.
    """

    def __init__(self):
        self._logged_actions = {}
        self._logged_actions_lock = RLock()

    def add(self, action: LoggedAction):
        """
        Add a new logged action.
        """

        with self._logged_actions_lock:
            self._logged_actions[action.id] = action

        self._notify_web_clients(action)

    def remove(self, action_id: str, response: Optional[Any] = None):
        """
        Remove a logged action.
        """

        with self._logged_actions_lock:
            action = self._logged_actions.pop(action_id, None)

        if not action:
            return

        status = LoggedActionStatus.COMPLETED
        if response and isinstance(response, Response):
            if response.errors:
                status = LoggedActionStatus.FAILED
                response = "\n\n".join(response.errors)
            else:
                response = response.output

        action.response = response
        action.status = status
        action.completed_at = time()
        self._notify_web_clients(action)

    def get(self, action_id: str) -> Optional[LoggedAction]:
        """
        Get a logged action by ID.
        """

        with self._logged_actions_lock:
            return self._logged_actions.get(action_id)

    def dump(self):
        """
        Dump the list of logged actions.
        """

        with self._logged_actions_lock:
            return [action.dump() for action in self._logged_actions.values()]

    @staticmethod
    def _notify_web_clients(action: LoggedAction):
        """
        Notify the web clients about an action status update.
        """
        from platypush.backend.http.app.ws.monitor import WSMonitorProxy

        if get_backend('http') is None:
            return

        WSMonitorProxy.publish(action)


def register_action(action: dict) -> str:
    """
    Register a new action.

    :param action: The action to register. Format:

        .. code-block:: python

            {
                'action': 'plugin.action_name',
                'args': {
                    'arg1': 'value1',
                    ...
                }
            }

    """
    a = LoggedAction(**action)
    pending_actions.add(a)
    return a.id


def unregister_action(action_id: Optional[str], response: Optional[Any] = None):
    """
    Unregister an action by ID.

    :param action_id: ID of the action to unregister.
    :param response: Response to send back to the client.
    """
    if action_id is None:
        return

    pending_actions.remove(action_id, response=response)


pending_actions = LoggedActions()
