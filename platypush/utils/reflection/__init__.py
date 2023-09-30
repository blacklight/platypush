import contextlib
import inspect
import os
import re
import textwrap as tw
from dataclasses import dataclass, field
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from typing import Optional, Type, Union, Callable, Dict, Set

from platypush.utils import (
    get_backend_class_by_name,
    get_backend_name_by_class,
    get_plugin_class_by_name,
    get_plugin_name_by_class,
    get_decorators,
)
from platypush.utils.manifest import Manifest, ManifestType, Dependencies
from platypush.utils.reflection._parser import DocstringParser, Parameter


class Action(DocstringParser):
    """
    Represents an integration action.
    """


class Constructor(DocstringParser):
    """
    Represents an integration constructor.
    """

    @classmethod
    def parse(cls, obj: Union[Type, Callable]) -> "Constructor":
        """
        Parse the parameters of a class constructor or action method.

        :param obj: Base type of the object.
        :return: The parsed parameters.
        """
        init = getattr(obj, "__init__", None)
        if init and callable(init):
            return super().parse(init)

        return super().parse(obj)


@dataclass
class IntegrationMetadata:
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
        if not self._skip_manifest:
            self._init_manifest()

    @staticmethod
    def _merge_params(params: Dict[str, Parameter], new_params: Dict[str, Parameter]):
        """
        Utility function to merge a new mapping of parameters into an existing one.
        """
        for param_name, param in new_params.items():
            # Set the parameter if it doesn't exist
            if param_name not in params:
                params[param_name] = param

            # Set the parameter documentation if it's not set
            if param.doc and not params[param_name].doc:
                params[param_name].doc = param.doc

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
            cls._merge_params(actions[action_name].params, action.params)

    @classmethod
    def _merge_events(cls, events: Set[Type], new_events: Set[Type]):
        """
        Utility function to merge a new mapping of actions into an existing one.
        """
        events.update(new_events)

    @classmethod
    def by_name(cls, name: str) -> "IntegrationMetadata":
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
    def by_type(cls, type: Type, _skip_manifest: bool = False) -> "IntegrationMetadata":
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
            doc=inspect.getdoc(type),
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
                    cls._merge_params(obj.constructor.params, p_obj.constructor.params)

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

    @classmethod
    def from_manifest(cls, manifest_file: str) -> "IntegrationMetadata":
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
            os.path.dirname(inspect.getfile(self.type)), "manifest.yaml"
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
                    for name, param in self.constructor.params.items()
                )
                if self.constructor and self.constructor.params
                else "    # No configuration required\n"
            )
        )


def import_file(path: str, name: Optional[str] = None):
    """
    Import a Python file as a module, even if no __init__.py is
    defined in the directory.

    :param path: Path of the file to import.
    :param name: Custom name for the imported module (default: same as the file's basename).
    :return: The imported module.
    """
    name = name or re.split(r"\.py$", os.path.basename(path))[0]
    loader = SourceFileLoader(name, os.path.expanduser(path))
    mod_spec = spec_from_loader(name, loader)
    assert mod_spec, f"Cannot create module specification for {path}"
    mod = module_from_spec(mod_spec)
    loader.exec_module(mod)
    return mod
