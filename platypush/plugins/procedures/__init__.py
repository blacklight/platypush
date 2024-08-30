from contextlib import contextmanager
import json
from dataclasses import dataclass
from typing import Callable, Collection, Generator, Iterable, Optional, Union

from sqlalchemy.orm import Session

from platypush.context import get_plugin
from platypush.entities.managers.procedures import ProcedureEntityManager
from platypush.entities.procedures import Procedure, ProcedureType
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.db import DbPlugin
from platypush.utils import run

from ._serialize import ProcedureEncoder


@dataclass
class _ProcedureWrapper:
    name: str
    obj: Union[dict, Callable]


class ProceduresPlugin(RunnablePlugin, ProcedureEntityManager):
    """
    Utility plugin to run and store procedures as native entities.
    """

    @action
    def exec(self, procedure: str, *args, **kwargs):
        return run(f'procedure.{procedure}', *args, **kwargs)

    def _convert_procedure(self, name: str, proc: Union[dict, Callable]) -> Procedure:
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
        )

    @action
    def status(self, *_, **__):
        """
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
        self.publish_entities(self._get_wrapped_procedures())
        return self._get_serialized_procedures()

    def _update_procedure(self, old: Procedure, new: Procedure, session: Session):
        assert old.procedure_type == ProcedureType.DB.value, (  # type: ignore[attr-defined]
            f'Procedure {old.name} is not stored in the database, '
            f'it should be removed from the source file: {old.source}'
        )

        old.external_id = new.external_id
        old.name = new.name
        old.args = new.args
        old.actions = new.actions
        session.add(old)

    @action
    def save(
        self,
        name: str,
        actions: Iterable[dict],
        args: Optional[Iterable[str]] = None,
        old_name: Optional[str] = None,
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
        """
        assert name, 'Procedure name cannot be empty'
        assert actions, 'Procedure actions cannot be empty'
        assert all(
            isinstance(action, dict) and action.get('action') for action in actions
        ), 'Procedure actions should be dictionaries with an "action" key'

        args = args or []
        proc_def = {
            'type': ProcedureType.DB.value,
            'name': name,
            'actions': actions,
            'args': args,
        }

        existing_proc = None
        old_proc = None
        new_proc = Procedure(
            external_id=name,
            plugin=str(self),
            procedure_type=ProcedureType.DB.value,
            name=name,
            actions=actions,
            args=args,
        )

        with self._db_session() as session:
            if old_name and old_name != name:
                old_proc = (
                    session.query(Procedure).filter(Procedure.name == old_name).first()
                )

                if old_proc:
                    self._update_procedure(old=old_proc, new=new_proc, session=session)
                else:
                    self.logger.warning(
                        'Procedure %s not found, skipping rename', old_name
                    )

            existing_proc = (
                session.query(Procedure).filter(Procedure.name == name).first()
            )

            if existing_proc:
                if old_proc:
                    self._delete(str(existing_proc.name), session=session)
                else:
                    self._update_procedure(
                        old=existing_proc, new=new_proc, session=session
                    )
            elif not old_proc:
                session.add(new_proc)

        if old_proc:
            old_name = str(old_proc.name)
            self._all_procedures.pop(old_name, None)

        self._all_procedures[name] = {
            **self._all_procedures.get(name, {}),  # type: ignore[operator]
            **proc_def,
        }

        self.status()

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

    @contextmanager
    def _db_session(self) -> Generator[Session, None, None]:
        db: Optional[DbPlugin] = get_plugin(DbPlugin)
        assert db, 'No database plugin configured'
        with db.get_session(
            autoflush=False, autocommit=False, expire_on_commit=False
        ) as session:
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

    def transform_entities(
        self, entities: Collection[_ProcedureWrapper], **_
    ) -> Collection[Procedure]:
        return [
            self._convert_procedure(name=proc.name, proc=proc.obj) for proc in entities
        ]

    def _get_wrapped_procedures(self) -> Collection[_ProcedureWrapper]:
        return [
            _ProcedureWrapper(name=name, obj=proc)
            for name, proc in self._all_procedures.items()
        ]

    def _sync_db_procedures(self):
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
                self.logger.info('Removing stale procedure record for %s', proc.name)
                session.delete(proc)

            procs_to_add = [
                proc
                for name, proc in saved_procs.items()
                if proc.procedure_type == ProcedureType.DB.value  # type: ignore[attr-defined]
                and name not in cur_proc_names
            ]

            for proc in procs_to_add:
                self._all_procedures[str(proc.name)] = {
                    'type': proc.procedure_type,
                    'name': proc.name,
                    'args': proc.args,
                    'actions': proc.actions,
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
