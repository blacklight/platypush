import inspect
import re
import textwrap as tw
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import IntEnum
from typing import (
    Any,
    Optional,
    Iterable,
    Type,
    get_type_hints,
    Callable,
    Tuple,
    Generator,
    Dict,
)


@dataclass
class ReturnValue:
    """
    Represents the return value of an action.
    """

    doc: Optional[str] = None
    type: Optional[Type] = None


@dataclass
class Parameter:
    """
    Represents an integration constructor/action parameter.
    """

    name: str
    required: bool = False
    doc: Optional[str] = None
    type: Optional[Type] = None
    default: Optional[str] = None


class ParseState(IntEnum):
    """
    Parse state.
    """

    DOC = 0
    PARAM = 1
    TYPE = 2
    RETURN = 3


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
    parsed_params: dict[str, Parameter] = field(default_factory=dict)

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


class DocstringParser:
    """
    Mixin for objects that can parse docstrings.
    """

    _param_doc_re = re.compile(r"^:param\s+(?P<name>[\w_]+):\s+(?P<doc>.*)$")
    _type_doc_re = re.compile(r"^:type\s+[\w_]+:.*$")
    _return_doc_re = re.compile(r"^:return:\s+(?P<doc>.*)$")
    _default_docstring = re.compile(r"^Initialize self. See help")

    def __init__(
        self,
        name: str,
        doc: Optional[str] = None,
        params: Optional[Dict[str, Parameter]] = None,
        returns: Optional[ReturnValue] = None,
    ):
        self.name = name
        self.doc = doc
        self.params = params or {}
        self.returns = returns

    @classmethod
    @contextmanager
    def _parser(cls, obj: Callable) -> Generator[ParseContext, None, None]:
        """
        Manages the parsing context manager.

        :param obj: Method to parse.
        :return: The parsing context.
        """

        def norm_indent(text: Optional[str]) -> Optional[str]:
            """
            Normalize the indentation of a docstring.

            :param text: Input docstring
            :return: A representation of the docstring where all the leading spaces have been removed.
            """
            if not text:
                return None

            lines = text.split("\n")
            return (lines[0] + " " + tw.dedent("\n".join(lines[1:]) or "")).strip()

        ctx = ParseContext(obj)
        yield ctx

        # Normalize the parameters docstring indentation
        for param in ctx.parsed_params.values():
            param.doc = norm_indent(param.doc)

        # Normalize the return docstring indentation
        ctx.returns.doc = norm_indent(ctx.returns.doc)

    @staticmethod
    def _is_continuation_line(line: str) -> bool:
        return not line.strip() or line.startswith(" ")

    @classmethod
    def _parse_line(cls, line: str, ctx: ParseContext):
        """
        Parse a single line of the docstring and updates the parse context accordingly.

        :param line: Docstring line.
        :param ctx: Parse context.
        """
        # Ignore old in-doc type hints
        if cls._type_doc_re.match(line) or (
            ctx.state == ParseState.TYPE and cls._is_continuation_line(line)
        ):
            ctx.state = ParseState.TYPE
            return

        # Ignore the default constructor docstring
        if cls._default_docstring.match(line):
            return

        # Update the return type docstring if required
        m = cls._return_doc_re.match(line)
        if m or (ctx.state == ParseState.RETURN and cls._is_continuation_line(line)):
            ctx.state = ParseState.RETURN
            ctx.returns.doc = ((ctx.returns.doc + "\n") if ctx.returns.doc else "") + (
                m.group("doc") if m else line
            ).rstrip()
            return

        # Create a new parameter entry if the docstring says so
        m = cls._param_doc_re.match(line)
        if m:
            ctx.state = ParseState.PARAM
            idx = len(ctx.parsed_params)
            ctx.cur_param = m.group("name")

            # Skip vararg/var keyword parameters
            if ctx.cur_param == ctx.spec.varkw or ctx.spec.varargs:
                return

            ctx.parsed_params[ctx.cur_param] = Parameter(
                name=ctx.cur_param,
                required=(
                    idx >= len(ctx.param_defaults) or ctx.param_defaults[idx] is Any
                ),
                doc=m.group("doc"),
                type=ctx.param_types.get(ctx.cur_param),
                default=ctx.param_defaults[idx]
                if idx < len(ctx.param_defaults) and ctx.param_defaults[idx] is not Any
                else None,
            )
            return

        # Update the current parameter docstring if required
        if (
            ctx.state == ParseState.PARAM
            and cls._is_continuation_line(line)
            and ctx.cur_param in ctx.parsed_params
        ):
            ctx.parsed_params[ctx.cur_param].doc = (
                ((ctx.parsed_params[ctx.cur_param].doc or "") + "\n" + line.rstrip())
                if ctx.parsed_params.get(ctx.cur_param)
                and ctx.parsed_params[ctx.cur_param].doc
                else ""
            )
            return

        # Update the current docstring if required
        ctx.cur_param = None
        ctx.doc = ((ctx.doc + "\n") if ctx.doc else "") + line.rstrip()
        ctx.state = ParseState.DOC

    @classmethod
    def parse(cls, obj: Callable):
        """
        Parse the parameters of a class constructor or action method.
        :param obj: Method to parse.
        :return: The parsed parameters.
        """
        with cls._parser(obj) as ctx:
            for line in ctx.doc_lines:
                cls._parse_line(line, ctx)

        return cls(
            name=obj.__name__,
            doc=ctx.doc,
            params=ctx.parsed_params,
            returns=ctx.returns,
        )
