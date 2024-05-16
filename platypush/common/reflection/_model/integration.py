import contextlib
import inspect
import os
import re
import textwrap as tw
from dataclasses import dataclass, field
from typing import Type, Optional, Dict, Set

from platypush.utils import (
    get_backend_class_by_name,
    get_plugin_class_by_name,
    get_plugin_name_by_class,
    get_backend_name_by_class,
    get_decorators,
)
from platypush.utils.manifest import Manifest, ManifestType, Dependencies

from .._parser import DocstringParser
from .._serialize import Serializable
from . import Constructor, Action
from .component import Component
from .constants import doc_base_url


@dataclass
class Integration(Component, DocstringParser, Serializable):
    """
    Represents the metadata of an integration (plugin or backend).
    """

    _class_type_re = re.compile(r"^<class '(?P<name>[\w_]+)'>$")

    name: str
    type: Type
    doc: Optional[str] = None
    constructor: Optional[Constructor] = None
    actions: Dict[str, Action] = field(default_factory=dict)
    _manifest: Optional[Manifest] = None
    _skip_manifest: bool = False

    def __post_init__(self):
        """
        Initialize the manifest object.
        """
        if not self._skip_manifest:
            self._init_manifest()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": f"{self.type.__module__}.{self.type.__qualname__}",
            "doc": self.doc,
            "doc_url": self.doc_url,
            "args": {
                **(
                    {name: arg.to_dict() for name, arg in self.constructor.args.items()}
                    if self.constructor
                    else {}
                ),
            },
            "actions": {
                k: {
                    "doc_url": f"{self.doc_url}#{self.cls.__module__}.{self.cls.__qualname__}.{k}",
                    **v.to_dict(),
                }
                for k, v in self.actions.items()
                if self.cls
            },
            "events": {
                f"{e.__module__}.{e.__qualname__}": {
                    "doc": inspect.getdoc(e),
                    "doc_url": f"{doc_base_url}/events/"
                    + ".".join(e.__module__.split(".")[3:])
                    + f".html#{e.__module__}.{e.__qualname__}",
                }
                for e in self.events
            },
            "deps": self.deps.to_dict(),
            "config_snippet": self.config_snippet,
        }

    @classmethod
    def _merge_actions(cls, actions: Dict[str, Action], new_actions: Dict[str, Action]):
        """
        Utility function to merge a new mapping of actions into an existing one.
        """
        for action_name, action in new_actions.items():
            # Set the action if it doesn't exist
            if action_name not in actions:
                actions[action_name] = action

            # Set the action documentation if it's not set
            if action.doc and not actions[action_name].doc:
                actions[action_name].doc = action.doc

            # Merge the parameters
            cls._merge_params(actions[action_name].args, action.args)

    @classmethod
    def _merge_events(cls, events: Set[Type], new_events: Set[Type]):
        """
        Utility function to merge a new mapping of actions into an existing one.
        """
        events.update(new_events)

    @classmethod
    def by_name(cls, name: str) -> "Integration":
        """
        :param name: Integration name.
        :return: A parsed Integration class given its type.
        """
        type = (
            get_backend_class_by_name(".".join(name.split(".")[1:]))
            if name.startswith("backend.")
            else get_plugin_class_by_name(name)
        )
        return cls.by_type(type)

    @classmethod
    def by_type(cls, type: Type, _skip_manifest: bool = False) -> "Integration":
        """
        :param type: Integration type (plugin or backend).
        :param _skip_manifest: Whether we should skip parsing the manifest file for this integration
            (you SHOULDN'T use this flag outside of this class!).
        :return: A parsed Integration class given its type.
        """
        from platypush.backend import Backend
        from platypush.plugins import Plugin

        assert issubclass(
            type, (Plugin, Backend)
        ), f"Expected a Plugin or Backend class, got {type}"

        name = (
            get_plugin_name_by_class(type)
            if issubclass(type, Plugin)
            else "backend." + get_backend_name_by_class(type)
        )

        assert name
        obj = cls(
            name=name,
            type=type,
            doc=cls._expand_rst_extensions(inspect.getdoc(type) or '', type) or None,
            constructor=Constructor.parse(type),
            actions={
                name: Action.parse(getattr(type, name))
                for name in get_decorators(type, climb_class_hierarchy=True).get(
                    "action", []
                )
            },
            _skip_manifest=_skip_manifest,
        )

        for p_type in inspect.getmro(type)[1:]:
            with contextlib.suppress(AssertionError):
                p_obj = cls.by_type(p_type, _skip_manifest=True)
                # Merge constructor parameters
                if obj.constructor and p_obj.constructor:
                    cls._merge_params(obj.constructor.args, p_obj.constructor.args)

                # Merge actions
                cls._merge_actions(obj.actions, p_obj.actions)
                # Merge events
                try:
                    cls._merge_events(obj.events, p_obj.events)
                except FileNotFoundError:
                    pass

        return obj

    @property
    def cls(self) -> Optional[Type]:
        """
        :return: The class of an integration.
        """
        manifest_type = self.manifest.package.split(".")[1]
        if manifest_type == "backend":
            getter = get_backend_class_by_name
        elif manifest_type == "plugins":
            getter = get_plugin_class_by_name
        else:
            return None

        return getter(".".join(self.manifest.package.split(".")[2:]))

    @property
    def base_type(self) -> Type:
        """
        :return: The base type of this integration, either :class:`platypush.backend.Backend` or
            :class:`platypush.plugins.Plugin`.
        """
        from platypush.backend import Backend
        from platypush.plugins import Plugin

        assert self.cls, f'No class found for integration {self.name}'
        if issubclass(self.cls, Plugin):
            return Plugin
        if issubclass(self.cls, Backend):
            return Backend

        raise AssertionError(f"Unknown base type for {self.cls}")

    @classmethod
    def from_manifest(cls, manifest_file: str) -> "Integration":
        """
        Create an `IntegrationMetadata` object from a manifest file.

        :param manifest_file: Path of the manifest file.
        :return: A parsed Integration class given its manifest file.
        """
        manifest = Manifest.from_file(manifest_file)
        name = ".".join(
            [
                "backend" if manifest.manifest_type == ManifestType.BACKEND else "",
                *manifest.package.split(".")[2:],
            ]
        ).strip(".")

        return cls.by_name(name)

    def _init_manifest(self) -> Manifest:
        """
        Initialize the manifest object.
        """
        if not self._manifest:
            self._manifest = Manifest.from_file(self.manifest_file)
        return self._manifest

    @classmethod
    def _type_str(cls, param_type) -> str:
        """
        Utility method to pretty-print the type string of a parameter.
        """
        type_str = str(param_type).replace("typing.", "")
        if m := cls._class_type_re.match(type_str):
            return m.group("name")

        return type_str

    @property
    def manifest(self) -> Manifest:
        """
        :return: The parsed Manifest object.
        """
        return self._init_manifest()

    @property
    def manifest_file(self) -> str:
        """
        :return: Path of the manifest file for the integration.
        """
        return os.path.join(
            os.path.dirname(inspect.getfile(self.type)), "manifest.json"
        )

    @property
    def description(self) -> Optional[str]:
        """
        :return: The description of the integration.
        """
        return self.manifest.description

    @property
    def events(self) -> Set[Type]:
        """
        :return: Events triggered by the integration.
        """
        return set(self.manifest.events)

    @property
    def deps(self) -> Dependencies:
        """
        :return: Dependencies of the integration.
        """
        return self.manifest.install

    @classmethod
    def _indent_yaml_comment(cls, s: str) -> str:
        return tw.indent(
            "\n".join(
                [
                    line if line.startswith("#") else f"# {line}"
                    for line in s.split("\n")
                ]
            ),
            "  ",
        )

    @property
    def config_snippet(self) -> str:
        """
        :return: A YAML snippet with the configuration parameters of the integration.
        """
        return tw.dedent(
            self.name
            + ":\n"
            + (
                "\n".join(
                    f'  # [{"Required" if param.required else "Optional"}]\n'
                    + (f"{self._indent_yaml_comment(param.doc)}" if param.doc else "")
                    + "\n  "
                    + ("# " if not param.required else "")
                    + f"{name}: "
                    + (str(param.default) if param.default is not None else "")
                    + (
                        self._indent_yaml_comment(f"type={self._type_str(param.type)}")
                        if param.type
                        else ""
                    )
                    + "\n"
                    for name, param in self.constructor.args.items()
                )
                if self.constructor and self.constructor.args
                else "    # No configuration required\n"
            )
        )

    @property
    def doc_url(self) -> str:
        """
        :return: URL of the documentation for the integration.
        """
        from platypush.backend import Backend
        from platypush.plugins import Plugin

        if issubclass(self.type, Plugin):
            section = 'plugins'
        elif issubclass(self.type, Backend):
            section = 'backend'
        else:
            raise AssertionError(f'Unknown integration type {self.type}')

        return f"{doc_base_url}/{section}/{self.name}.html"
