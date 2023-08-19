from dataclasses import dataclass, field
import enum
import importlib
import inspect
import json
import logging
import os
import pathlib
import shutil
import sys

from typing import (
    Dict,
    Generator,
    List,
    Optional,
    Iterable,
    Mapping,
    Set,
    Type,
    Union,
)

import yaml

from platypush.message.event import Event

supported_package_managers = {
    'apk': ['apk', 'add', '--update', '--no-interactive', '--no-cache'],
    'apt': ['apt', 'install', '-y'],
    'pacman': ['pacman', '-S', '--noconfirm'],
}

_available_package_manager = None
logger = logging.getLogger(__name__)


class ManifestType(enum.Enum):
    """
    Manifest types.
    """

    PLUGIN = 'plugin'
    BACKEND = 'backend'


@dataclass
class Dependencies:
    """
    Dependencies for a plugin/backend.
    """

    before: List[str] = field(default_factory=list)
    """ Commands to execute before the component is installed. """
    packages: Set[str] = field(default_factory=set)
    """ System packages required by the component. """
    pip: Set[str] = field(default_factory=set)
    """ pip dependencies. """
    after: List[str] = field(default_factory=list)
    """ Commands to execute after the component is installed. """

    @classmethod
    def from_config(
        cls, conf_file: Optional[str] = None, pkg_manager: Optional[str] = None
    ) -> "Dependencies":
        """
        Parse the required dependencies from a configuration file.
        """
        deps = cls()

        for manifest in Manifests.by_config(conf_file, pkg_manager=pkg_manager):
            deps.before += manifest.install.before
            deps.pip.update(manifest.install.pip)
            deps.packages.update(manifest.install.packages)
            deps.after += manifest.install.after

        return deps

    def to_pkg_install_commands(
        self, pkg_manager: Optional[str] = None, skip_sudo: bool = False
    ) -> Generator[str, None, None]:
        """
        Generates the package manager commands required to install the given
        dependencies on the system.

        :param pkg_manager: Force package manager to use (default: looks for
            the one available on the system).
        :param skip_sudo: Skip sudo when installing packages (default: it will
            look if the current user is root and use sudo otherwise).
        """
        wants_sudo = not skip_sudo and os.getuid() != 0
        pkg_manager = pkg_manager or get_available_package_manager()
        if self.packages and pkg_manager:
            yield ' '.join(
                [
                    *(['sudo'] if wants_sudo else []),
                    *supported_package_managers[pkg_manager],
                    *sorted(self.packages),
                ]
            )

    def to_pip_install_commands(self) -> Generator[str, None, None]:
        """
        Generates the pip commands required to install the given dependencies on
        the system.
        """
        # Recent versions want an explicit --break-system-packages option when
        # installing packages via pip outside of a virtual environment
        wants_break_system_packages = (
            sys.version_info > (3, 10)
            and sys.prefix == sys.base_prefix  # We're not in a venv
        )

        if self.pip:
            yield (
                'pip install -U --no-input --no-cache-dir '
                + ('--break-system-packages ' if wants_break_system_packages else '')
                + ' '.join(sorted(self.pip))
            )

    def to_install_commands(
        self, pkg_manager: Optional[str] = None, skip_sudo: bool = False
    ) -> Generator[str, None, None]:
        """
        Generates the commands required to install the given dependencies on
        this system.

        :param pkg_manager: Force package manager to use (default: looks for
            the one available on the system).
        :param skip_sudo: Skip sudo when installing packages (default: it will
            look if the current user is root and use sudo otherwise).
        """
        for cmd in self.before:
            yield cmd

        for cmd in self.to_pkg_install_commands(
            pkg_manager=pkg_manager, skip_sudo=skip_sudo
        ):
            yield cmd

        for cmd in self.to_pip_install_commands():
            yield cmd

        for cmd in self.after:
            yield cmd


class Manifest:
    """
    Base class for plugin/backend manifests.
    """

    def __init__(
        self,
        package: str,
        description: Optional[str] = None,
        install: Optional[Dict[str, Iterable[str]]] = None,
        events: Optional[Mapping] = None,
        pkg_manager: Optional[str] = None,
        **_,
    ):
        self._pkg_manager = pkg_manager or get_available_package_manager()
        self.description = description
        self.install = self._init_deps(install or {})
        self.events = self._init_events(events or {})
        self.package = package
        self.component_name = '.'.join(package.split('.')[2:])
        self.component = None

    def _init_deps(self, install: Mapping[str, Iterable[str]]) -> Dependencies:
        deps = Dependencies()
        for key, items in install.items():
            if key == 'pip':
                deps.pip.update(items)
            elif key == 'before':
                deps.before += items
            elif key == 'after':
                deps.after += items
            elif key == self._pkg_manager:
                deps.packages.update(items)

        return deps

    @staticmethod
    def _init_events(
        events: Union[Iterable[str], Mapping[str, Optional[str]]]
    ) -> Dict[Type[Event], str]:
        evt_dict = events if isinstance(events, Mapping) else {e: None for e in events}
        ret = {}

        for evt_name, doc in evt_dict.items():
            evt_module_name, evt_class_name = evt_name.rsplit('.', 1)
            try:
                evt_module = importlib.import_module(evt_module_name)
                evt_class = getattr(evt_module, evt_class_name)
            except Exception as e:
                raise AssertionError(f'Could not load event {evt_name}: {e}') from e

            ret[evt_class] = doc or evt_class.__doc__

        return ret

    @classmethod
    def from_file(cls, filename: str, pkg_manager: Optional[str] = None) -> "Manifest":
        """
        Parse a manifest filename into a ``Manifest`` class.
        """
        with open(str(filename), 'r') as f:
            manifest = yaml.safe_load(f).get('manifest', {})

        assert 'type' in manifest, f'Manifest file {filename} has no type field'
        comp_type = ManifestType(manifest.pop('type'))
        manifest_class = _manifest_class_by_type[comp_type]
        return manifest_class(**manifest, pkg_manager=pkg_manager)

    def __repr__(self):
        """
        :return: A JSON serialized representation of the manifest.
        """
        return json.dumps(
            {
                'description': self.description,
                'install': self.install,
                'events': {
                    '.'.join([evt_type.__module__, evt_type.__name__]): doc
                    for evt_type, doc in self.events.items()
                },
                'type': _manifest_type_by_class[self.__class__].value,
                'package': self.package,
                'component_name': self.component_name,
            }
        )


# pylint: disable=too-few-public-methods
class PluginManifest(Manifest):
    """
    Plugin manifest.
    """


# pylint: disable=too-few-public-methods
class BackendManifest(Manifest):
    """
    Backend manifest.
    """


class Manifests:
    """
    General-purpose manifests utilities.
    """

    @staticmethod
    def by_base_class(
        base_class: Type, pkg_manager: Optional[str] = None
    ) -> Generator[Manifest, None, None]:
        """
        Get all the manifest files declared under the base path of a given class
        and parse them into :class:`Manifest` objects.
        """
        for mf in pathlib.Path(os.path.dirname(inspect.getfile(base_class))).rglob(
            'manifest.yaml'
        ):
            yield Manifest.from_file(str(mf), pkg_manager=pkg_manager)

    @staticmethod
    def by_config(
        conf_file: Optional[str] = None,
        pkg_manager: Optional[str] = None,
    ) -> Generator[Manifest, None, None]:
        """
        Get all the manifest objects associated to the extensions declared in a
        given configuration file.
        """
        import platypush
        from platypush.config import Config

        conf_args = []
        if conf_file:
            conf_args.append(conf_file)

        Config.init(*conf_args)
        app_dir = os.path.dirname(inspect.getfile(platypush))

        for name in Config.get_backends().keys():
            yield Manifest.from_file(
                os.path.join(app_dir, 'backend', *name.split('.'), 'manifest.yaml'),
                pkg_manager=pkg_manager,
            )

        for name in Config.get_plugins().keys():
            yield Manifest.from_file(
                os.path.join(app_dir, 'plugins', *name.split('.'), 'manifest.yaml'),
                pkg_manager=pkg_manager,
            )


def get_available_package_manager() -> Optional[str]:
    """
    Get the name of the available package manager on the system, if supported.
    """
    # pylint: disable=global-statement
    global _available_package_manager
    if _available_package_manager:
        return _available_package_manager

    available_package_managers = [
        pkg_manager
        for pkg_manager in supported_package_managers
        if shutil.which(pkg_manager)
    ]

    if not available_package_managers:
        logger.warning(
            '\nYour OS does not provide any of the supported package managers.\n'
            'You may have to install some optional dependencies manually.\n'
            'Supported package managers: %s.\n',
            ', '.join(supported_package_managers.keys()),
        )

        return None

    _available_package_manager = available_package_managers[0]
    return _available_package_manager


_manifest_class_by_type: Mapping[ManifestType, Type[Manifest]] = {
    ManifestType.PLUGIN: PluginManifest,
    ManifestType.BACKEND: BackendManifest,
}

_manifest_type_by_class: Mapping[Type[Manifest], ManifestType] = {
    cls: t for t, cls in _manifest_class_by_type.items()
}
