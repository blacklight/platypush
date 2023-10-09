import importlib
import logging
import re
import textwrap as tw

from .._model.constants import doc_base_url
from .context import ParseContext


# pylint: disable=too-few-public-methods
class RstExtensionsMixin:
    """
    Mixin class for handling non-standard reStructuredText extensions.
    """

    _rst_extensions = {
        name: re.compile(regex)
        for name, regex in {
            "class": "(:class:`(?P<name>[^`]+)`)",
            "method": "(:meth:`(?P<name>[^`]+)`)",
            "function": "(:func:`(?P<name>[^`]+)`)",
            "schema": r"^((?P<indent>\s*)(?P<before>.*)"
            r"(\.\. schema:: (?P<name>[\w.]+)\s*"
            r"(\((?P<args>.+?)\))?)(?P<after>.*))$",
        }.items()
    }

    logger = logging.getLogger(__name__)

    @classmethod
    def _expand_rst_extensions(cls, docstr: str, ctx: ParseContext) -> str:
        """
        Expand the known reStructuredText extensions in a docstring.
        """
        for ex_name, regex in cls._rst_extensions.items():
            match = regex.search(docstr)
            if not match:
                continue

            try:
                docstr = (
                    cls._expand_schema(docstr, match)
                    if ex_name == "schema"
                    else cls._expand_module(docstr, ex_name, match, ctx)
                )
            except Exception as e:
                cls.logger.warning(
                    "Could not import module %s: %s", match.group("name"), e
                )
                continue

        return docstr

    @classmethod
    def _expand_schema(cls, docstr: str, match: re.Match) -> str:
        from marshmallow import missing
        from marshmallow.validate import OneOf

        value = match.group("name")
        mod = importlib.import_module(
            "platypush.schemas." + ".".join(value.split(".")[:-1])
        )
        obj_cls = getattr(mod, value.split(".")[-1])
        schema_args = (
            eval(f'dict({match.group("args")})') if match.group("args") else {}
        )
        obj = obj_cls(**schema_args)

        schema_doc = tw.indent(
            ".. code-block:: python\n\n"
            + tw.indent(
                ("[" if obj.many else "")
                + "{\n"
                + tw.indent(
                    ",\n".join(
                        (
                            (
                                "# " + field.metadata["description"] + "\n"
                                if field.metadata.get("description")
                                else ""
                            )
                            + (
                                "# Possible values: "
                                + str(field.validate.choices)
                                + "\n"
                                if isinstance(field.validate, OneOf)
                                else ""
                            )
                            + f'"{field_name}": '
                            + (
                                (
                                    '"'
                                    + field.metadata.get("example", field.default)
                                    + '"'
                                    if isinstance(
                                        field.metadata.get("example", field.default),
                                        str,
                                    )
                                    else str(
                                        field.metadata.get("example", field.default)
                                    )
                                )
                                if not (
                                    field.metadata.get("example") is None
                                    and field.default is missing
                                )
                                else "..."
                            )
                        )
                        for field_name, field in obj.fields.items()
                    ),
                    prefix="  ",
                )
                + "\n}"
                + ("]" if obj.many else ""),
                prefix="  ",
            ),
            prefix=match.group("indent") + "  ",
        )

        docstr = docstr.replace(
            match.group(0),
            match.group("before") + "\n\n" + schema_doc + "\n\n" + match.group("after"),
        )

        return docstr

    @classmethod
    def _expand_module(
        cls, docstr: str, ex_name: str, match: re.Match, ctx: ParseContext
    ) -> str:
        value = match.group("name")
        if value.startswith("."):
            modname = ctx.obj.__module__  # noqa
            obj_name = ctx.obj.__qualname__
        elif ex_name == "method":
            modname = ".".join(value.split(".")[:-2])
            obj_name = ".".join(value.split(".")[-2:])
        else:
            modname = ".".join(value.split(".")[:-1])
            obj_name = value.split(".")[-1]

        url_path = None

        if modname.startswith("platypush.plugins"):
            url_path = "plugins/" + ".".join(modname.split(".")[2:])
        elif modname.startswith("platypush.backend"):
            url_path = "backends/" + ".".join(modname.split(".")[2:])
        elif modname.startswith("platypush.message.event"):
            url_path = "events/" + ".".join(modname.split(".")[3:])
        elif modname.startswith("platypush.message.response"):
            url_path = "responses/" + ".".join(modname.split(".")[3:])

        if url_path:
            docstr = docstr.replace(
                match.group(0),
                f"`{obj_name} <{doc_base_url}/{url_path}.html#{modname}.{obj_name}>`_",
            )
        else:
            docstr = docstr.replace(match.group(0), f"``{value}``")

        return docstr
