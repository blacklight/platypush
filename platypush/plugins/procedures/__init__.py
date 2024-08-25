import json
from dataclasses import dataclass
from typing import Callable, Collection, Optional, Union

from platypush.entities.managers.procedures import ProcedureEntityManager
from platypush.entities.procedures import Procedure
from platypush.plugins import RunnablePlugin, action
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
        while not self.should_stop():
            self.publish_entities(self._get_wrapped_procedures())
            self.wait_stop()
