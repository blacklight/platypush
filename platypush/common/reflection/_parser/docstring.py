import re
import textwrap as tw
from contextlib import contextmanager
from typing import Callable, Dict, Generator, Optional

from .._model.argument import Argument
from .._model.returns import ReturnValue
from .._serialize import Serializable
from .context import ParseContext
from .rst import RstExtensionsMixin
from .state import ParseState


class DocstringParser(Serializable, RstExtensionsMixin):
    """
    Mixin for objects that can parse docstrings.
    """

    _param_doc_re = re.compile(r"^:param\s+(?P<name>[\w_]+):\s+(?P<doc>.*)$")
    _type_doc_re = re.compile(r"^:type\s+[\w_]+:.*$")
    _return_doc_re = re.compile(r"^:return:\s+(?P<doc>.*)$")
    _default_docstring = re.compile(r"^\s*Initialize self\.\s*See help.*$")

    def __init__(
        self,
        name: str,
        doc: Optional[str] = None,
        args: Optional[Dict[str, Argument]] = None,
        has_varargs: bool = False,
        has_kwargs: bool = False,
        returns: Optional[ReturnValue] = None,
    ):
        self.name = name
        self.doc = doc
        self.args = args or {}
        self.has_varargs = has_varargs
        self.has_kwargs = has_kwargs
        self.returns = returns

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "doc": self.doc,
            "args": {k: v.to_dict() for k, v in self.args.items()},
            "has_varargs": self.has_varargs,
            "has_kwargs": self.has_kwargs,
            "returns": self.returns.to_dict() if self.returns else None,
        }

    @staticmethod
    def _norm_indent(text: Optional[str]) -> Optional[str]:
        """
        Normalize the indentation of a docstring.

        :param text: Input docstring
        :return: A representation of the docstring where all the leading spaces have been removed.
        """
        if not text:
            return None

        lines = text.split("\n")
        return (lines[0] + "\n" + tw.dedent("\n".join(lines[1:]) or "")).strip()

    @classmethod
    @contextmanager
    def _parser(cls, obj: Callable) -> Generator[ParseContext, None, None]:
        """
        Manages the parsing context manager.

        :param obj: Method to parse.
        :return: The parsing context.
        """

        ctx = ParseContext(obj)
        yield ctx

        # Normalize the parameters docstring indentation
        for param in ctx.parsed_params.values():
            param.doc = cls._norm_indent(param.doc)

        # Normalize the return docstring indentation
        ctx.returns.doc = cls._norm_indent(ctx.returns.doc)

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

        # Expand any custom RST extensions
        line = cls._expand_rst_extensions(line, ctx.obj)

        # Update the return type docstring if required
        m = cls._return_doc_re.match(line)
        if m or (ctx.state == ParseState.RETURN and cls._is_continuation_line(line)):
            ctx.state = ParseState.RETURN
            ctx.returns.doc = ((ctx.returns.doc + "\n") if ctx.returns.doc else "") + (
                m.group("doc") if m else line
            ).rstrip()
            return

        # Initialize the documentation of a parameter on :param: docstring lines
        m = cls._param_doc_re.match(line)
        if m and ctx.parsed_params.get(m.group("name")):
            ctx.state = ParseState.PARAM
            ctx.cur_param = m.group("name")

            # Skip vararg/var keyword parameters
            if ctx.cur_param in {ctx.spec.varkw, ctx.spec.varargs}:
                return

            ctx.parsed_params[ctx.cur_param].doc = m.group("doc")
            return

        # Update the current parameter docstring if required
        if ctx.state == ParseState.PARAM and cls._is_continuation_line(line):
            if ctx.cur_param in ctx.parsed_params:
                ctx.parsed_params[ctx.cur_param].doc = (
                    (
                        (ctx.parsed_params[ctx.cur_param].doc or "")
                        + "\n"
                        + line.rstrip()
                    )
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
            args=ctx.parsed_params,
            has_varargs=ctx.spec.varargs is not None,
            has_kwargs=ctx.spec.varkw is not None,
            returns=ctx.returns,
        )
