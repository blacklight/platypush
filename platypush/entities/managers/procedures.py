from abc import ABC, abstractmethod
from typing import Callable, Dict, Union

from platypush.config import Config
from . import EntityManager


class ProcedureEntityManager(EntityManager, ABC):
    """
    Base class for integrations that can run and manage procedures.
    """

    @abstractmethod
    def exec(self, procedure: str, *args, **kwargs):
        """
        Run a procedure.

        :param procedure: Procedure to run, by name.
        :param args: Arguments to pass to the procedure.
        :param kwargs: Keyword arguments to pass to the procedure.
        """
        raise NotImplementedError()

    @property
    def _all_procedures(self) -> Dict[str, Union[dict, Callable]]:
        """
        :return: All the procedures that can be run by this entity manager.
        """
        return Config.get_procedures()
