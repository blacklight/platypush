import inspect
import textwrap as tw
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    get_type_hints,
)

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
        """
        Initialize the return type and parameters from the function annotations.
        """

        # If we're dealing with a wrapped @action, then unwrap the underlying function
        if hasattr(self.obj, "wrapped"):
            self.obj = self.obj.wrapped

        # Initialize the return type from the annotations
        annotations = getattr(self.obj, "__annotations__", {})
        if annotations:
            self.returns.type = annotations.get("return")

        # Initialize the parameters from the signature
        defaults = self.spec.defaults or ()
        defaults = ((Any,) * (len(self.param_names) - len(defaults or ()))) + defaults
        self.parsed_params = {
            name: Argument(
                name=name,
                type=self.param_types.get(name),
                default=default if default is not Any else None,
                required=default is Any,
            )
            for name, default in zip(self.param_names, defaults)
        }

        # Update the parameters with the keyword-only arguments
        self.parsed_params.update(
            {
                arg: Argument(
                    name=arg,
                    type=self.param_types.get(arg),
                    default=(self.spec.kwonlydefaults or {}).get(arg),
                    required=arg not in (self.spec.kwonlydefaults or {}),
                )
                for arg in self.spec.kwonlyargs
            }
        )

    @property
    def spec(self) -> inspect.FullArgSpec:
        return inspect.getfullargspec(self.obj)

    @property
    def param_names(self) -> List[str]:
        return list(self.spec.args[1:])

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
