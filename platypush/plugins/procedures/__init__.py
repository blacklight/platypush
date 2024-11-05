from functools import wraps
import json
import re
from contextlib import contextmanager
from dataclasses import dataclass
from multiprocessing import RLock
from random import randint
from threading import Event
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Union,
)

import yaml
from sqlalchemy.orm import Session

from platypush.context import get_plugin
from platypush.entities import get_entities_engine
from platypush.entities.managers.procedures import ProcedureEntityManager
from platypush.entities.procedures import Procedure, ProcedureType
from platypush.message.event.entities import EntityDeleteEvent
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.db import DbPlugin
from platypush.utils import run

from ._serialize import ProcedureEncoder


# pylint: disable=protected-access
def ensure_initialized(f: Callable[..., Any]):
    """
    Ensures that the entities engine has been initialized before
    reading/writing the db.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        self: ProceduresPlugin = args[0]

        if not self._initialized.is_set():
            with self._init_lock:
                get_entities_engine(timeout=20)

                if not self._initialized.is_set():
                    self._initialized.set()

        return f(*args, **kwargs)

    return wrapper


@dataclass
class _ProcedureWrapper:
    name: str
    obj: Union[dict, Callable]


class ProceduresPlugin(RunnablePlugin, ProcedureEntityManager):
    """
    Utility plugin to run and store procedures as native entities.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialized = Event()
        self._init_lock = RLock()
        self._status_lock = RLock()

    @action
    def exec(self, procedure: Union[str, dict], *args, **kwargs):
        """
        Execute a procedure.

        :param procedure: Procedure name or definition. If a string is passed,
            then the procedure will be looked up by name in the configured
            procedures. If a dictionary is passed, then it should be a valid
            procedure definition with at least the ``actions`` key.
        :param args: Optional arguments to be passed to the procedure.
        :param kwargs: Optional arguments to be passed to the procedure.
        """
        if isinstance(procedure, str):
            return run(f'procedure.{procedure}', *args, **kwargs)

        assert isinstance(procedure, dict), 'Invalid procedure definition'
        procedure_name = procedure.get(
            'name', f'procedure_{f"{randint(0, 1 << 32):08x}"}'
        )

        actions = procedure.get('actions')
        assert actions and isinstance(
            actions, (list, tuple, set)
        ), 'Procedure definition should have at least the "actions" key as a list of actions'

        try:
            # Create a temporary procedure definition and execute it
            self._all_procedures[procedure_name] = {
                'name': procedure_name,
                'type': ProcedureType.CONFIG.value,
                'actions': list(actions),
                'args': procedure.get('args', []),
                '_async': False,
            }

            kwargs = {
                **procedure.get('args', {}),
                **kwargs,
            }

            return self.exec(procedure_name, *args, **kwargs)
        finally:
            self._all_procedures.pop(procedure_name, None)

    def _convert_procedure(
        self, name: str, proc: Union[dict, Callable, Procedure]
    ) -> Procedure:
        if isinstance(proc, Procedure):
            return proc

        metadata = self._serialize_procedure(proc, name=name)
        return Procedure(
            id=name,
            name=name,
            plugin=self,
            procedure_type=metadata['type'],
            module=metadata.get('module'),
            source=metadata.get('source'),
            line=metadata.get('line'),
            args=metadata.get('args', []),
            actions=metadata.get('actions', []),
            meta=metadata.get('meta', {}),
        )

    @action
    def status(self, *_, publish: bool = True, **__):
        """
        :param publish: If set to True (default) then the
            :class:`platypush.message.event.entities.EntityUpdateEvent` events
            will be published to the bus with the current configured procedures.
            Usually this should be set to True, unless you're calling this method
            from a context where you first want to retrieve the procedures and
            then immediately modify them. In such cases, the published events may
            result in race conditions on the entities engine.
        :return: The serialized configured procedures. Format:

            .. code-block:: json

                {
                    "procedure_name": {
                        "type": "python",
                        "module": "module_name",
                        "source": "/path/to/source.py",
                        "line": 42,
                        "args": ["arg1", "arg2"]
                    }
                }

        """
        with self._status_lock:
            self._sync_db_procedures()
            if publish:
                self.publish_entities(self._get_wrapped_procedures())

            return self._get_serialized_procedures()

    @action
    def save(
        self,
        name: str,
        actions: Iterable[dict],
        args: Optional[Iterable[str]] = None,
        old_name: Optional[str] = None,
        meta: Optional[dict] = None,
        **_,
    ):
        """
        Save a procedure.

        :param name: Name of the procedure.
        :param actions: Definition of the actions to be executed. Format:

              .. code-block:: json

                [
                    {
                        "action": "logger.info",
                        "args": {
                            "msg": "Hello, world!"
                        }
                    }
                ]

        :param args: Optional list of arguments to be passed to the procedure,
            as a list of strings with the argument names.
        :param old_name: Optional old name of the procedure if it's being
            renamed.
        :param meta: Optional metadata to be stored with the procedure. Example:

            .. code-block:: json

                {
                    "icon": {
                        "class": "fas fa-cogs",
                        "color": "#00ff00"
                    }
                }

        """
        assert name, 'Procedure name cannot be empty'
        assert actions, 'Procedure actions cannot be empty'

        args = args or []
        proc_def = self._all_procedures.get(name, {})
        proc_args = {
            'name': name,
            'type': ProcedureType.DB.value,
            'actions': actions,
            'args': args,
            'meta': (
                meta or (proc_def.get('meta', {}) if isinstance(proc_def, dict) else {})
            ),
        }

        def _on_entity_saved(*_, **__):
            self._all_procedures[name] = proc_args

        with self._status_lock:
            with self._db_session() as session:
                if old_name and old_name != name:
                    try:
                        self._delete(old_name, session=session)
                    except AssertionError as e:
                        self.logger.warning(
                            'Error while deleting old procedure: name=%s: %s',
                            old_name,
                            e,
                        )

            self.publish_entities(
                [_ProcedureWrapper(name=name, obj=proc_args)],
                callback=_on_entity_saved,
            )

        return self.status(publish=False)

    @action
    def delete(self, name: str):
        """
        Delete a procedure by name.

        Note that this is only possible for procedures that are stored on the
        database. Procedures that are loaded from Python scripts or
        configuration files should be removed from the source file.

        :param name: Name of the procedure to be deleted.
        """
        with self._db_session() as session:
            self._delete(name, session=session)

        self.status()

    @action
    def to_yaml(self, procedure: Union[str, dict]) -> str:
        """
        Serialize a procedure to YAML.

        This method is useful to export a procedure to a file.
        Note that it only works with either YAML-based procedures or
        database-stored procedures: Python procedures can't be converted to
        YAML.

        :param procedure: Procedure name or definition. If a string is passed,
            then the procedure will be looked up by name in the configured
            procedures. If a dictionary is passed, then it should be a valid
            procedure definition with at least the ``actions`` and ``name``
            keys.
        :return: The serialized procedure in YAML format.
        """
        if isinstance(procedure, str):
            proc = self._all_procedures.get(procedure)
            assert proc, f'Procedure {proc} not found'
        elif isinstance(procedure, dict):
            name = self._normalize_name(procedure.get('name'))
            assert name, 'Procedure name cannot be empty'

            actions = procedure.get('actions', [])
            assert actions and isinstance(
                actions, (list, tuple, set)
            ), 'Procedure definition should have at least the "actions" key as a list of actions'

            args = [self._normalize_name(arg) for arg in procedure.get('args', [])]
            proc = {
                f'procedure.{name}'
                + (f'({", ".join(args)})' if args else ''): [
                    self._serialize_action(action) for action in actions
                ]
            }
        else:
            raise AssertionError(
                f'Invalid procedure definition with type {type(procedure)}'
            )

        return yaml.safe_dump(proc, default_flow_style=False, indent=2)

    @staticmethod
    def _normalize_name(name: Optional[str]) -> str:
        return re.sub(r'[^\w.]+', '_', (name or '').strip(' .'))

    @classmethod
    def _serialize_action(cls, data: Union[Iterable, Dict]) -> Union[Dict, List, str]:
        if isinstance(data, dict):
            name = data.get('action', data.get('name'))
            if name:
                return {
                    'action': name,
                    **({'args': data['args']} if data.get('args') else {}),
                }

            return {
                k: (
                    cls._serialize_action(v)
                    if isinstance(v, (dict, list, tuple))
                    else v
                )
                for k, v in data.items()
            }
        elif isinstance(data, str):
            return data
        else:
            return [cls._serialize_action(item) for item in data if item is not None]

    @ensure_initialized
    @contextmanager
    def _db_session(self) -> Generator[Session, None, None]:
        db: Optional[DbPlugin] = get_plugin(DbPlugin)
        assert db, 'No database plugin configured'
        with db.get_session(locked=True) as session:
            assert isinstance(session, Session)
            yield session

            if session.is_active:
                session.commit()
            else:
                session.rollback()

    def _delete(self, name: str, session: Session):
        assert name, 'Procedure name cannot be empty'
        proc_row: Procedure = (
            session.query(Procedure).filter(Procedure.name == name).first()
        )

        assert proc_row, f'Procedure {name} not found in the database'
        assert proc_row.procedure_type == ProcedureType.DB.value, (  # type: ignore[attr-defined]
            f'Procedure {name} is not stored in the database, '
            f'it should be removed from the source file'
        )

        session.delete(proc_row)
        self._all_procedures.pop(name, None)
        self._bus.post(EntityDeleteEvent(plugin=self, entity=proc_row))

    def transform_entities(
        self, entities: Collection[_ProcedureWrapper], **_
    ) -> Collection[Procedure]:
        return [
            self._convert_procedure(
                name=proc.name,
                proc=proc if isinstance(proc, Procedure) else proc.obj,
            )
            for proc in entities
        ]

    def _get_wrapped_procedures(self) -> Collection[_ProcedureWrapper]:
        return [
            _ProcedureWrapper(name=name, obj=proc)
            for name, proc in self._all_procedures.items()
        ]

    def _sync_db_procedures(self):
        with self._status_lock:
            cur_proc_names = set(self._all_procedures.keys())
            with self._db_session() as session:
                saved_procs = {
                    str(proc.name): proc for proc in session.query(Procedure).all()
                }

                procs_to_remove = [
                    proc
                    for name, proc in saved_procs.items()
                    if name not in cur_proc_names
                    and proc.procedure_type != ProcedureType.DB.value  # type: ignore[attr-defined]
                ]

                for proc in procs_to_remove:
                    self.logger.info(
                        'Removing stale procedure record for %s', proc.name
                    )
                    session.delete(proc)

                procs_to_add = [
                    proc
                    for proc in saved_procs.values()
                    if proc.procedure_type == ProcedureType.DB.value  # type: ignore[attr-defined]
                ]

                for proc in procs_to_add:
                    self._all_procedures[str(proc.name)] = {
                        'type': proc.procedure_type,
                        'name': proc.name,
                        'args': proc.args,
                        'actions': proc.actions,
                        'meta': proc.meta,
                    }

    @staticmethod
    def _serialize_procedure(
        proc: Union[dict, Callable], name: Optional[str] = None
    ) -> dict:
        ret = json.loads(json.dumps(proc, cls=ProcedureEncoder))
        if name:
            ret['name'] = name

        return ret

    def _get_serialized_procedures(self) -> dict:
        return {
            name: self._serialize_procedure(proc, name=name)
            for name, proc in self._all_procedures.items()
        }

    def main(self, *_, **__):
        self._sync_db_procedures()

        while not self.should_stop():
            self.publish_entities(self._get_wrapped_procedures())
            self.wait_stop()
