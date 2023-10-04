import inspect
import textwrap as tw
from dataclasses import dataclass, field
from typing import Callable, Optional, Iterable, Tuple, Any, Type, get_type_hints

from .._model.argument import Argument
from .._model.returns import ReturnValue
from .state import ParseState


@dataclass
class ParseContext:
    """
    Runtime parsing context.
    """

    obj: Callable
    state: ParseState = ParseState.DOC
    cur_param: Optional[str] = None
    doc: Optional[str] = None
    returns: ReturnValue = field(default_factory=ReturnValue)
    parsed_params: dict[str, Argument] = field(default_factory=dict)

    def __post_init__(self):
        annotations = getattr(self.obj, "__annotations__", {})
        if annotations:
            self.returns.type = annotations.get("return")

    @property
    def spec(self) -> inspect.FullArgSpec:
        return inspect.getfullargspec(self.obj)

    @property
    def param_names(self) -> Iterable[str]:
        return self.spec.args[1:]

    @property
    def param_defaults(self) -> Tuple[Any]:
        defaults = self.spec.defaults or ()
        return ((Any,) * (len(self.spec.args[1:]) - len(defaults))) + defaults

    @property
    def param_types(self) -> dict[str, Type]:
        return get_type_hints(self.obj)

    @property
    def doc_lines(self) -> Iterable[str]:
        return tw.dedent(inspect.getdoc(self.obj) or "").split("\n")
